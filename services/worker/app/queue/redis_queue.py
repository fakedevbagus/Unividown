import redis
import json
from datetime import datetime
from typing import Optional, List
from app.config import settings


class RedisQueue:
    def __init__(self):
        self.redis = redis.Redis.from_url(
            settings.redis_url or "redis://localhost:6379",
            decode_responses=True
        )
        self.queue_key = "unividown:download_queue"
        self.processing_key = "unividown:processing_queue"

    def push_job(self, job_id: int, priority: int = 0):
        """Push job ke queue dengan priority (higher = lebih diprioritaskan)"""
        score = priority + datetime.now().timestamp()
        self.redis.zadd(self.queue_key, {str(job_id): score})

    def pop_job(self) -> Optional[int]:
        """Ambil job dengan priority tertinggi"""
        result = self.redis.zpopmax(self.queue_key, count=1)
        if result:
            return int(result[0][0])
        return None

    def mark_processing(self, job_id: int):
        """Tandai job sedang diproses"""
        self.redis.sadd(self.processing_key, str(job_id))

    def unmark_processing(self, job_id: int):
        """Hapus tanda processing"""
        self.redis.srem(self.processing_key, str(job_id))

    def get_queue_length(self) -> int:
        return self.redis.zcard(self.queue_key)

    def get_processing_count(self) -> int:
        return self.redis.scard(self.processing_key)

    def clear_queue(self):
        self.redis.delete(self.queue_key)
        self.redis.delete(self.processing_key)


queue = RedisQueue()