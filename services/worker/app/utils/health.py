import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import redis
from sqlalchemy import text

from app.config import settings
from app.database import engine


def _result(ok: bool, detail: str, required: bool = True) -> Dict[str, Any]:
    return {"ok": ok, "required": required, "detail": detail}


def check_database() -> Dict[str, Any]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return _result(True, "database query succeeded")
    except Exception as exc:
        return _result(False, f"database unavailable: {type(exc).__name__}")


def check_redis() -> Dict[str, Any]:
    required = settings.redis_required
    if not settings.redis_url:
        return _result(not required, "redis not configured", required)
    try:
        client = redis.Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=0.25,
            socket_timeout=0.25,
        )
        client.ping()
        return _result(True, "redis ping succeeded", required)
    except Exception as exc:
        return _result(False, f"redis unavailable: {type(exc).__name__}", required)


def check_storage() -> Dict[str, Any]:
    paths = [settings.upload_dir, settings.download_dir, settings.processed_dir]
    try:
        for value in paths:
            path = Path(value)
            path.mkdir(parents=True, exist_ok=True)
            probe = path / ".healthcheck"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
        return _result(True, "storage paths are writable")
    except Exception as exc:
        return _result(False, f"storage unavailable: {type(exc).__name__}")


def check_ffmpeg() -> Dict[str, Any]:
    binary = shutil.which("ffmpeg")
    return _result(bool(binary), binary or "ffmpeg not found")


def check_worker_tasks(tasks: Optional[Iterable[Any]]) -> Dict[str, Any]:
    task_list = [task for task in (tasks or []) if task is not None]
    ok = bool(task_list) and all(not task.done() for task in task_list)
    return _result(ok, "background worker tasks running" if ok else "background worker task stopped")


def build_readiness_report(tasks: Optional[Iterable[Any]] = None) -> Dict[str, Any]:
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "storage": check_storage(),
        "ffmpeg": check_ffmpeg(),
        "workers": check_worker_tasks(tasks),
    }
    ready = all(value["ok"] for value in checks.values() if value["required"])
    degraded = any(not value["ok"] for value in checks.values() if not value["required"])
    return {"status": "ready" if ready else "not_ready", "ready": ready, "degraded": degraded, "checks": checks}
