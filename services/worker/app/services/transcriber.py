import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import ffmpeg


class Transcriber:
    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            output_dir = os.getenv("PROCESSED_DIR", "./data/processed")
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def transcribe(
        self,
        input_path: str,
        model_size: str = "tiny",
        job_id: int = 0
    ) -> Dict[str, Any]:
        """Transcribe audio/video file using Whisper"""
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        # Extract audio first (Whisper needs audio)
        audio_path = self.output_dir / f"{job_id}_audio_for_whisper.wav"
        try:
            (
                ffmpeg
                .input(str(input_file))
                .output(str(audio_path), acodec="pcm_s16le", ar=16000, ac=1)
                .overwrite_output()
                .run(quiet=True)
            )
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio: {e}")

        # Transcribe with Whisper (lazy import)
        try:
            import whisper
        except ImportError:
            audio_path.unlink(missing_ok=True)
            raise RuntimeError("openai-whisper not installed. Run: pip install openai-whisper")

        model = whisper.load_model(model_size)
        result = model.transcribe(str(audio_path), language="en", verbose=False)

        # Save transcript
        transcript_path = self.output_dir / f"{job_id}_transcript.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        # Save segments as JSON
        segments_path = self.output_dir / f"{job_id}_segments.json"
        with open(segments_path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {"start": seg["start"], "end": seg["end"], "text": seg["text"]}
                    for seg in result.get("segments", [])
                ],
                f,
                indent=2
            )

        # Clean up audio
        audio_path.unlink(missing_ok=True)

        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "transcript_path": str(transcript_path),
            "segments_path": str(segments_path),
        }
