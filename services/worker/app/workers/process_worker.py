import asyncio
import json
from app.services.processor import MediaProcessor
from app.services.transcriber import Transcriber
from app.database import SessionLocal
from app.models.processing_job import ProcessingJob


class ProcessWorker:
    def __init__(self):
        self.processor = MediaProcessor()
        self.transcriber = Transcriber()
        self.running = True

    async def process_queue(self):
        print("[ProcessWorker] Media queue processor started.")
        while self.running:
            db = SessionLocal()
            try:
                job = db.query(ProcessingJob).filter_by(status="pending").first()
                if job:
                    job.status = "processing"
                    db.commit()
                    db.refresh(job)

                    try:
                        await self.process_job(job, db)
                    except Exception as e:
                        print(f"[ProcessWorker] Job {job.id} failed: {e}")
                        job.status = "failed"
                        job.error_message = str(e)
                        db.commit()
            except Exception as e:
                print(f"[ProcessWorker] Queue loop error: {e}")
            finally:
                db.close()

            await asyncio.sleep(1)

    async def process_job(self, job: ProcessingJob, db):
        loop = asyncio.get_running_loop()
        params = json.loads(job.parameters) if job.parameters else {}
        input_files = json.loads(job.input_files) if job.input_files else []

        def execute():
            if job.tool_type == "convert":
                fmt = params.get("format", "mp4")
                return self.processor.convert(input_files[0], fmt, job.id)
            elif job.tool_type == "trim":
                start = float(params.get("start", 0))
                end = float(params.get("end", 10))
                return self.processor.trim(input_files[0], start, end, job.id)
            elif job.tool_type == "compress":
                bitrate = params.get("bitrate", "1000k")
                return self.processor.compress(input_files[0], bitrate, job.id)
            elif job.tool_type == "merge":
                return self.processor.merge(input_files, job.id)
            # Phase 16: New tool types
            elif job.tool_type == "audio_convert":
                fmt = params.get("format", "mp3")
                return self.processor.extract_audio(input_files[0], fmt, job.id)
            elif job.tool_type == "image_optimize":
                quality = int(params.get("quality", 85))
                max_width = int(params.get("max_width", 1920))
                return self.processor.optimize_image(input_files[0], quality, max_width, job.id)
            elif job.tool_type == "subtitle_extract":
                result = self.processor.extract_subtitle(input_files[0], job.id)
                return result[0] if result else ""
            elif job.tool_type == "gif_make":
                start = float(params.get("start", 0))
                duration = float(params.get("duration", 5))
                fps = int(params.get("fps", 15))
                scale = int(params.get("scale", 480))
                return self.processor.make_gif(input_files[0], start, duration, fps, scale, job.id)
            # Phase 17: AI Transcription
            elif job.tool_type == "transcribe":
                model = params.get("model", "tiny")
                result = self.transcriber.transcribe(input_files[0], model, job.id)
                return result["transcript_path"]
            else:
                raise ValueError(f"Unknown tool type: {job.tool_type}")

        output_path = await loop.run_in_executor(None, execute)
        job.output_files = json.dumps([output_path]) if output_path else json.dumps([])
        job.progress = 100.0
        job.status = "completed"
        db.commit()
        print(f"[ProcessWorker] Job {job.id} ({job.tool_type}) completed.")
