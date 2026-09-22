import magic
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException

from app.config import settings

ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/webm", "video/x-matroska",
    "video/x-msvideo", "video/quicktime", "video/x-flv"
}
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp4", "audio/wav",
    "audio/x-wav", "audio/flac", "audio/ogg", "audio/x-vorbis"
}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_TYPES = ALLOWED_VIDEO_TYPES | ALLOWED_AUDIO_TYPES | ALLOWED_IMAGE_TYPES
ALLOWED_EXTENSIONS = {
    ".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv",
    ".mp3", ".m4a", ".wav", ".flac", ".ogg",
    ".jpg", ".jpeg", ".png", ".webp", ".gif",
}
MAX_FILES_PER_REQUEST = 50


def validate_file(file_path: Path) -> Tuple[bool, str]:
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if file_path.stat().st_size > settings.max_file_size:
        raise HTTPException(status_code=413, detail="File too large")
    file_type = magic.Magic(mime=True).from_file(str(file_path))
    if file_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file_type}")
    return True, file_type


def validate_multipart_files(files: list) -> None:
    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(status_code=413, detail=f"Too many files. Maximum: {MAX_FILES_PER_REQUEST}")
    for file in files:
        suffix = Path(Path(file.filename or "upload").name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=415, detail="Unsupported file extension")
        if file.size is not None and file.size > settings.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")


def get_file_category(mime_type: str) -> str:
    if mime_type in ALLOWED_VIDEO_TYPES:
        return "video"
    if mime_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    if mime_type in ALLOWED_IMAGE_TYPES:
        return "image"
    return "unknown"
