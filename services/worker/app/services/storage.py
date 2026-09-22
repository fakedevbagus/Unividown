from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import Iterable

from fastapi import HTTPException

from app.config import settings


@dataclass
class CleanupReport:
    deleted_files: int = 0
    deleted_bytes: int = 0


def storage_roots() -> list[Path]:
    return [Path(settings.upload_dir).resolve(), Path(settings.download_dir).resolve(), Path(settings.processed_dir).resolve()]


def iter_storage_files() -> Iterable[Path]:
    for root in storage_roots():
        if not root.exists():
            continue
        for path in root.rglob('*'):
            if path.is_file():
                yield path


def storage_usage_bytes() -> int:
    total = 0
    for path in iter_storage_files():
        try:
            total += path.stat().st_size
        except OSError:
            continue
    return total


def ensure_storage_capacity(incoming_bytes: int = 0) -> None:
    quota = settings.storage_quota_bytes
    if quota > 0 and storage_usage_bytes() + max(0, incoming_bytes) > quota:
        raise HTTPException(status_code=507, detail='Storage quota exceeded')


def cleanup_expired_storage(now: float | None = None) -> CleanupReport:
    report = CleanupReport()
    retention_seconds = max(0, settings.output_retention_hours) * 3600
    cutoff = (time() if now is None else now) - retention_seconds
    for path in list(iter_storage_files()):
        try:
            stat = path.stat()
            if stat.st_mtime > cutoff:
                continue
            path.unlink()
            report.deleted_files += 1
            report.deleted_bytes += stat.st_size
        except OSError:
            continue
    for root in storage_roots():
        if not root.exists():
            continue
        for directory in sorted((path for path in root.rglob('*') if path.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass
    return report
