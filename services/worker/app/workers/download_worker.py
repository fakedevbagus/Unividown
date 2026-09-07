import asyncio
import os
import re
from pathlib import Path
from typing import Optional, Any
from app.services.downloader import Downloader, clean_ansi
from app.database import SessionLocal
from app.models.download_job import DownloadJob
from app.models.downloaded_file import DownloadedFile


class DownloadWorker:
    def __init__(self, sio: Optional[Any] = None):
        self.downloader = Downloader()
        self.running = True
        self.sio = sio

    def set_sio(self, sio: Any):
        self.sio = sio

    async def emit_event(self, event: str, data: dict, room: Optional[str] = None):
        if self.sio:
            try:
                if room:
                    await self.sio.emit(event, data, room=room)
                else:
                    await self.sio.emit(event, data)
            except Exception as e:
                print(f"[Worker] SIO emit error: {e}")

    async def process_queue(self):
        """Background queue processor for download jobs."""
        print("[DownloadWorker] Queue processor started.")
        while self.running:
            db = SessionLocal()
            try:
                job = (
                    db.query(DownloadJob)
                    .filter_by(status="pending")
                    .order_by(DownloadJob.priority.desc(), DownloadJob.created_at.asc())
                    .first()
                )

                if job:
                    job.status = "processing"
                    db.commit()
                    db.refresh(job)

                    await self.emit_event(
                        "download:status",
                        {"jobId": job.id, "status": "processing"},
                        room=f"job:{job.id}"
                    )

                    # Retry loop with exponential backoff
                    max_retries = 3
                    success = False
                    last_error = None
                    for attempt in range(max_retries + 1):
                        try:
                            await self.download_video(job, db, resume=(attempt > 0))
                            success = True
                            break
                        except Exception as e:
                            last_error = e
                            print(f"[DownloadWorker] Job {job.id} attempt {attempt + 1} failed: {e}")
                            job.retry_count = attempt + 1
                            job.error_message = str(e)
                            db.commit()
                            if attempt < max_retries:
                                await asyncio.sleep(2 ** attempt)
                    if not success:
                        job.status = "failed"
                        job.error_message = str(last_error) if last_error else "Unknown error"
                        db.commit()
                        await self.emit_event(
                            "download:error",
                            {"jobId": job.id, "error": str(last_error)},
                            room=f"job:{job.id}"
                        )
            except Exception as loop_err:
                print(f"[DownloadWorker] Queue loop error: {loop_err}")
            finally:
                db.close()

            await asyncio.sleep(1)

    async def download_video(self, job: DownloadJob, db, resume: bool = False):
        loop = asyncio.get_running_loop()

        def progress_hook(d):
            if d.get('status') == 'downloading':
                raw_pct = d.get('_percent_str', '0%')
                clean_pct = clean_ansi(raw_pct).replace('%', '')
                try:
                    pct = float(clean_pct)
                except ValueError:
                    pct = 0.0

                job.progress = pct
                db.commit()

                # Emit real-time progress via asyncio thread-safe call
                speed = clean_ansi(d.get('_speed_str', ''))
                eta = clean_ansi(d.get('_eta_str', ''))
                if self.sio:
                    asyncio.run_coroutine_threadsafe(
                        self.emit_event(
                            "download:progress",
                            {
                                "jobId": job.id,
                                "progress": pct,
                                "speed": speed,
                                "eta": eta,
                            },
                            room=f"job:{job.id}"
                        ),
                        loop
                    )

        # Run blocking yt-dlp in executor to not block event loop
        def do_download():
            return self.downloader.download(
                url=job.url,
                job_id=job.id,
                quality=job.quality or "best",
                resume=resume,
                progress_callback=progress_hook,
            )

        info = await loop.run_in_executor(None, do_download)

        # Update metadata
        if info:
            job.title = info.get("title", job.title)
            job.thumbnail_url = info.get("thumbnail", job.thumbnail_url)
            job.platform = info.get("extractor", job.platform)

        # Scan downloaded files in job directory
        job_dir = Path(self.downloader.output_dir) / str(job.id)
        if job_dir.exists():
            for f in job_dir.iterdir():
                if f.is_file() and not f.name.endswith(".part") and not f.name.endswith(".ytdl"):
                    ext = f.suffix.lower().replace(".", "")
                    file_type = "video"
                    if ext in ["mp3", "m4a", "wav", "flac", "ogg", "aac"]:
                        file_type = "audio"
                    elif ext in ["jpg", "jpeg", "png", "webp"]:
                        file_type = "thumbnail"
                    elif ext in ["vtt", "srt", "ass"]:
                        file_type = "subtitle"

                    saved_file = DownloadedFile(
                        job_id=job.id,
                        filename=f.name,
                        file_path=str(f.resolve()),
                        file_type=file_type,
                        file_size=f.stat().st_size,
                    )
                    db.add(saved_file)

        job.progress = 100.0
        job.status = "completed"
        db.commit()

        await self.emit_event(
            "download:completed",
            {"jobId": job.id, "title": job.title, "status": "completed"},
            room=f"job:{job.id}"
        )
        print(f"[DownloadWorker] Job {job.id} completed successfully.")
