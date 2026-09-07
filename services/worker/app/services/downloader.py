import os
import re
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
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
        """Extract metadata without downloading. Detect playlist vs video."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Detect playlist
            if 'entries' in info and info['entries'] is not None:
                entries = []
                for entry in info['entries']:
                    if entry:
                        entries.append({
                            'id': entry.get('id'),
                            'title': entry.get('title'),
                            'url': entry.get('url') or entry.get('webpage_url') or entry.get('id'),
                            'duration': entry.get('duration'),
                            'thumbnail': entry.get('thumbnail'),
                        })
                return {
                    'type': 'playlist',
                    'title': info.get('title'),
                    'entries': entries,
                    'count': len(entries),
                }
            else:
                return {
                    'type': 'video',
                    'title': info.get('title'),
                    'url': url,
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader'),
                    'extractor': info.get('extractor'),
                }

    def get_available_formats(self, url: str) -> List[Dict[str, Any]]:
        """Return available quality/format options for a URL."""
        ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            full = ydl.extract_info(url, download=False)
            if 'entries' in full and full.get('entries'):
                return []
            formats = full.get('formats', [])
            seen = set()
            options = []
            for f in formats:
                height = f.get('height')
                ext = f.get('ext')
                if height and height not in seen:
                    seen.add(height)
                    options.append({'height': height, 'ext': ext, 'label': f"{height}p"})
            options.sort(key=lambda x: x['height'], reverse=True)
            return options

    def download(
        self,
        url: str,
        job_id: int,
        quality: str = "best",
        format_spec: str = "best",
        resume: bool = False,
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
            'continue_dl': resume,  # Resume partial downloads
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
