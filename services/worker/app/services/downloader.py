import os
import re
from pathlib import Path
from typing import Callable, Optional, Dict, Any
import yt_dlp


def clean_ansi(text: str) -> str:
    """Remove ANSI escape codes from yt-dlp percentage strings."""
    ansi_regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_regex.sub('', text).strip()


class Downloader:
    def __init__(self, output_dir: Optional[str] = None):
        if output_dir is None:
            output_dir = os.getenv("DOWNLOAD_DIR", "./data/downloads")
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_info(self, url: str) -> Dict[str, Any]:
        """Extract metadata without downloading."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def download(
        self,
        url: str,
        job_id: int,
        quality: str = "best",
        format_spec: str = "best",
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """Download video/audio to data/downloads/{job_id}."""
        job_dir = self.output_dir / str(job_id)
        job_dir.mkdir(parents=True, exist_ok=True)

        # Select appropriate format depending on quality request
        selected_format = format_spec
        if quality and quality != "best":
            # e.g., quality is "1080", "720", "480", "mp3"
            if quality in ("mp3", "audio"):
                selected_format = "bestaudio/best"
            else:
                selected_format = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"

        ydl_opts: Dict[str, Any] = {
            'outtmpl': str(job_dir / '%(title)s.%(ext)s'),
            'format': selected_format,
            'quiet': False,
            'no_warnings': True,
            'progress_hooks': [progress_callback] if progress_callback else [],
        }

        # If audio-only conversion is requested
        if quality in ("mp3", "audio"):
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return info
