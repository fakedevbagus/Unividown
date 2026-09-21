from datetime import datetime
from typing import Iterable, Optional, Sequence, Tuple

import redis

from app.config import settings


class QueueUnavailable(RuntimeError):
    """Raised when Redis is required but unavailable."""


class RedisQueue:
    PRIORITY_SCALE = 10_000_000_000

    def __init__(self, client=None):
        self.redis = client or redis.Redis.from_url(
            settings.redis_url or "redis://localhost:6379",
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        self.queue_key = "unividown:download_queue"
        self.processing_key = "unividown:processing_queue"

    def _unavailable(self, operation: str, exc: redis.RedisError):
        if settings.redis_required:
            raise QueueUnavailable(f"Redis {operation} failed") from exc
        return False

    def _score(self, priority: int, timestamp: float) -> float:
        # Higher priority wins. Within a priority, older jobs win.
        return (int(priority) * self.PRIORITY_SCALE) - timestamp

    def push_jobs(self, jobs: Sequence[Tuple[int, int]]) -> bool:
        """Atomically enqueue jobs. Returns False when optional Redis is unavailable."""
        if not jobs:
            return True
        now = datetime.now().timestamp()
        try:
            pipe = self.redis.pipeline(transaction=True)
            for index, (job_id, priority) in enumerate(jobs):
                score = self._score(priority, now + (index / 1_000_000))
                pipe.zadd(self.queue_key, {str(job_id): score})
            pipe.execute()
            return True
        except redis.RedisError as exc:
            return self._unavailable("enqueue", exc)

    def push_job(self, job_id: int, priority: int = 0) -> bool:
        return self.push_jobs([(job_id, priority)])

    def pop_job(self) -> Optional[int]:
        try:
            result = self.redis.zpopmax(self.queue_key, count=1)
            return int(result[0][0]) if result else None
        except redis.RedisError as exc:
            self._unavailable("dequeue", exc)
            return None

    def remove_jobs(self, job_ids: Iterable[int]) -> bool:
        values = [str(job_id) for job_id in job_ids]
        if not values:
            return True
        try:
            self.redis.zrem(self.queue_key, *values)
            self.redis.srem(self.processing_key, *values)
            return True
        except redis.RedisError as exc:
            return self._unavailable("remove", exc)

    def mark_processing(self, job_id: int) -> bool:
        try:
            self.redis.sadd(self.processing_key, str(job_id))
            return True
        except redis.RedisError as exc:
            return self._unavailable("mark processing", exc)

    def unmark_processing(self, job_id: int) -> bool:
        try:
            self.redis.srem(self.processing_key, str(job_id))
            return True
        except redis.RedisError as exc:
            return self._unavailable("unmark processing", exc)

    def get_queue_length(self) -> int:
        try:
            return self.redis.zcard(self.queue_key)
        except redis.RedisError as exc:
            self._unavailable("queue length", exc)
            return 0

    def get_processing_count(self) -> int:
        try:
            return self.redis.scard(self.processing_key)
        except redis.RedisError as exc:
            self._unavailable("processing count", exc)
            return 0

    def clear_queue(self) -> bool:
        try:
            self.redis.delete(self.queue_key)
            self.redis.delete(self.processing_key)
            return True
        except redis.RedisError as exc:
            return self._unavailable("clear", exc)


queue = RedisQueue()
