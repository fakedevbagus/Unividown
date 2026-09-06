import magic
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException


ALLOWED_VIDEO_TYPES = {
    "video/mp4", "video/webm", "video/x-matroska", 
    "video/x-msvideo", "video/quicktime", "video/x-flv"
}
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp4", "audio/wav", 
    "audio/x-wav", "audio/flac", "audio/ogg", "audio/x-vorbis"
}
ALLOWED_IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif"
}
ALLOWED_TYPES = ALLOWED_VIDEO_TYPES | ALLOWED_AUDIO_TYPES | ALLOWED_IMAGE_TYPES

MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
MAX_FILES_PER_REQUEST = 50


def validate_file(file_path: Path) -> Tuple[bool, str]:
    """
    Validate file size and MIME type.
    Returns (is_valid, mime_type).
    """
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check size
    file_size = file_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024**3)}GB"
        )
    
    # Check MIME type using python-magic
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(str(file_path))
    
    if file_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file_type}. Allowed: video, audio, image"
        )
    
    return True, file_type


def validate_multipart_files(files: list) -> None:
    """Validate multiple uploaded files."""
    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files. Maximum: {MAX_FILES_PER_REQUEST}"
        )
    
    for file in files:
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File {file.filename} too large"
            )
        
        # Check extension as fallback
        ext = Path(file.filename).suffix.lower().lstrip('.')
        allowed_exts = {
            'mp4', 'mkv', 'webm', 'avi', 'mov', 'flv',
            'mp3', 'm4a', 'wav', 'flac', 'ogg',
            'jpg', 'jpeg', 'png', 'webp', 'gif'
        }
        if ext not in allowed_exts:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file extension: {ext}"
            )


def get_file_category(mime_type: str) -> str:
    """Categorize file by MIME type."""
    if mime_type in ALLOWED_VIDEO_TYPES:
        return "video"
    elif mime_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    elif mime_type in ALLOWED_IMAGE_TYPES:
        return "image"
    return "unknown"