from pathlib import Path
from typing import Collection
from uuid import uuid4

import magic
from fastapi import HTTPException, UploadFile

from app.config import settings
from app.utils.file_validator import ALLOWED_EXTENSIONS, ALLOWED_TYPES

CHUNK_SIZE = 1024 * 1024


def detect_mime(path: Path) -> str:
    return magic.Magic(mime=True).from_file(str(path))


def cleanup_uploads(paths: Collection[str]) -> None:
    for stored_path in paths:
        try:
            candidate = Path(stored_path)
            if candidate.is_file():
                candidate.unlink()
        except OSError:
            pass


async def save_upload(file: UploadFile, allowed_types: Collection[str] = ALLOWED_TYPES) -> str:
    """Stream an upload into a UUID path and validate its actual MIME type."""
    original_name = Path(file.filename or "upload").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported file extension")

    upload_root = Path(settings.upload_dir).resolve()
    upload_root.mkdir(parents=True, exist_ok=True)
    token = uuid4().hex
    temporary = upload_root / f".{token}.part"
    destination = upload_root / f"{token}{suffix}"
    total = 0

    try:
        with temporary.open("xb") as output:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > settings.max_file_size:
                    raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {settings.max_file_size} bytes")
                output.write(chunk)

        if total == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        mime_type = detect_mime(temporary)
        if mime_type not in allowed_types:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {mime_type}")

        temporary.replace(destination)
        return str(destination)
    except Exception:
        cleanup_uploads([str(temporary), str(destination)])
        raise
    finally:
        await file.close()
