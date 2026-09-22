import asyncio
import json

from app.database import SessionLocal
from app.models.processing_job import ProcessingJob
from app.services.processor import MediaProcessor
from app.services.transcriber import Transcriber
from app.services.uploads import cleanup_uploads


def recover_interrupted_processing_jobs(db) -> int:
    jobs = db.query(ProcessingJob).filter_by(status="processing").all()
    for job in jobs:
        job.status = "pending"
        job.error_message = "Recovered after worker restart"
    if jobs:
        db.commit()
    return len(jobs)


class ProcessWorker:
    def __init__(self):
        self.processor = MediaProcessor()
        self.transcriber = Transcriber()
        self.running = True

    async def process_queue(self):
        recovery_db = SessionLocal()
        try:
            recovered = recover_interrupted_processing_jobs(recovery_db)
            if recovered:
                print(f"[ProcessWorker] Recovered {recovered} interrupted processing job(s).")
        finally:
            recovery_db.close()

        print("[ProcessWorker] Media queue processor started.")
        while self.running:
            db = SessionLocal()
            try:
                job = db.query(ProcessingJob).filter_by(status="pending").first()
                if job:
                    input_files = json.loads(job.input_files) if job.input_files else []
                    job.status = "processing"
                    job.error_message = None
                    db.commit()
                    db.refresh(job)
                    try:
                        await self.process_job(job, db)
                    except Exception as error:
                        print(f"[ProcessWorker] Job {job.id} failed: {error}")
                        job.status = "failed"
                        job.error_message = str(error)
                        db.commit()
                    finally:
                        cleanup_uploads(input_files)
            except Exception as error:
                print(f"[ProcessWorker] Queue loop error: {error}")
            finally:
                db.close()
            await asyncio.sleep(1)

    async def process_job(self, job: ProcessingJob, db):
        loop = asyncio.get_running_loop()
        params = json.loads(job.parameters) if job.parameters else {}
        input_files = json.loads(job.input_files) if job.input_files else []

        def execute():
            if job.tool_type == "convert":
                return self.processor.convert(input_files[0], params.get("format", "mp4"), job.id)
            if job.tool_type == "trim":
                return self.processor.trim(input_files[0], float(params.get("start", 0)), float(params.get("end", 10)), job.id)
            if job.tool_type == "compress":
                return self.processor.compress(input_files[0], params.get("bitrate", "1000k"), job.id)
            if job.tool_type == "merge":
                return self.processor.merge(input_files, job.id)
            if job.tool_type == "audio_convert":
                return self.processor.extract_audio(input_files[0], params.get("format", "mp3"), job.id)
            if job.tool_type == "image_optimize":
                return self.processor.optimize_image(input_files[0], int(params.get("quality", 85)), int(params.get("max_width", 1920)), job.id)
            if job.tool_type == "subtitle_extract":
                result = self.processor.extract_subtitle(input_files[0], job.id)
                return result[0] if result else ""
            if job.tool_type == "gif_make":
                return self.processor.make_gif(input_files[0], float(params.get("start", 0)), float(params.get("duration", 5)), int(params.get("fps", 15)), int(params.get("scale", 480)), job.id)
            if job.tool_type == "transcribe":
                result = self.transcriber.transcribe(input_files[0], params.get("model", "tiny"), job.id)
                return result["transcript_path"]
            raise ValueError(f"Unknown tool type: {job.tool_type}")

        output_path = await loop.run_in_executor(None, execute)
        job.output_files = json.dumps([output_path]) if output_path else json.dumps([])
        job.progress = 100.0
        job.status = "completed"
        job.error_message = None
        db.commit()
        print(f"[ProcessWorker] Job {job.id} ({job.tool_type}) completed.")
