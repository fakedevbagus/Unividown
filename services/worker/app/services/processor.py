import os
from pathlib import Path
from typing import List, Optional
import ffmpeg


class MediaProcessor:
    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            output_dir = os.getenv("PROCESSED_DIR", "./data/processed")
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert(self, input_path: str, output_format: str, job_id: int) -> str:
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        fmt = output_format.lower().replace(".", "")
        output_file = self.output_dir / f"{job_id}.{fmt}"

        (
            ffmpeg
            .input(str(input_file))
            .output(str(output_file))
            .overwrite_output()
            .run(quiet=True)
        )

        return str(output_file)

    def trim(self, input_path: str, start_time: float, end_time: float, job_id: int) -> str:
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        duration = max(end_time - start_time, 0.1)
        output_file = self.output_dir / f"{job_id}_trimmed.mp4"

        (
            ffmpeg
            .input(str(input_file), ss=start_time, t=duration)
            .output(str(output_file), c="copy")
            .overwrite_output()
            .run(quiet=True)
        )

        return str(output_file)

    def compress(self, input_path: str, target_bitrate: str, job_id: int) -> str:
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        output_file = self.output_dir / f"{job_id}_compressed.mp4"

        (
            ffmpeg
            .input(str(input_file))
            .output(str(output_file), **{"b:v": target_bitrate, "preset": "fast"})
            .overwrite_output()
            .run(quiet=True)
        )

        return str(output_file)

    def merge(self, input_paths: List[str], job_id: int) -> str:
        if not input_paths:
            raise ValueError("No input files provided for merge")

        output_file = self.output_dir / f"{job_id}_merged.mp4"
        concat_file = self.output_dir / f"{job_id}_concat.txt"

        with open(concat_file, "w", encoding="utf-8") as f:
            for p in input_paths:
                resolved = Path(p).resolve()
                f.write(f"file '{resolved}'\n")

        try:
            (
                ffmpeg
                .input(str(concat_file), format="concat", safe=0)
                .output(str(output_file), c="copy")
                .overwrite_output()
                .run(quiet=True)
            )
        finally:
            if concat_file.exists():
                concat_file.unlink()

        return str(output_file)

    # Phase 16: New tools
    def extract_audio(self, input_path: str, output_format: str, job_id: int) -> str:
        """Extract audio from video"""
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        fmt = output_format.lower().replace(".", "")
        output_file = self.output_dir / f"{job_id}_audio.{fmt}"

        (
            ffmpeg
            .input(str(input_file))
            .output(str(output_file), **{"vn": None, "acodec": "libmp3lame" if fmt == "mp3" else "copy"})
            .overwrite_output()
            .run(quiet=True)
        )

        return str(output_file)

    def optimize_image(self, input_path: str, quality: int = 85, max_width: int = 1920, job_id: int = 0) -> str:
        """Optimize image for web"""
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        ext = input_file.suffix.lower().replace(".", "")
        output_file = self.output_dir / f"{job_id}_optimized.{ext}"

        (
            ffmpeg
            .input(str(input_file))
            .output(str(output_file), **{"q:v": quality, "vf": f"scale='min({max_width},iw)':-2"})
            .overwrite_output()
            .run(quiet=True)
        )

        return str(output_file)

    def extract_subtitle(self, input_path: str, job_id: int) -> List[str]:
        """Extract subtitles from video"""
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        output_file = self.output_dir / f"{job_id}_subtitles.vtt"

        try:
            (
                ffmpeg
                .input(str(input_file))
                .output(str(output_file), **{"map": "0:s:0"})
                .overwrite_output()
                .run(quiet=True)
            )
            if output_file.exists():
                return [str(output_file)]
        except ffmpeg.Error:
            pass

        return []

    def make_gif(self, input_path: str, start_time: float, duration: float, fps: int = 15, scale: int = 480, job_id: int = 0) -> str:
        """Create GIF from video"""
        input_file = Path(input_path).resolve()
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        output_file = self.output_dir / f"{job_id}_clip.gif"

        (
            ffmpeg
            .input(str(input_file), ss=start_time, t=duration)
            .output(str(output_file), **{"vf": f"fps={fps},scale={scale}:-1:flags=lanczos", "loop": 0})
            .overwrite_output()
            .run(quiet=True)
        )

        return str(output_file)
