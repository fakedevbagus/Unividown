import redis
from fastapi.testclient import TestClient

from app.api.endpoints import downloads as downloads_endpoint
from app.database import SessionLocal, init_db
from app.main import app
from app.models.download_job import DownloadJob
from app.queue.redis_queue import QueueUnavailable, RedisQueue

init_db()


def test_info_static_route_is_not_parsed_as_job_id(monkeypatch):
    monkeypatch.setattr(
        downloads_endpoint.downloader_service,
        "get_info",
        lambda url: {
            "type": "video",
            "title": "Fixture",
            "thumbnail": None,
            "duration": 10,
            "uploader": "tester",
            "extractor": "fixture",
        },
    )
    with TestClient(app) as client:
        response = client.get(
            "/api/downloads/info", params={"url": "https://example.com/video"}
        )
    assert response.status_code == 200
    assert response.json()["title"] == "Fixture"


def test_create_uses_database_fallback_when_optional_redis_is_down(monkeypatch):
    monkeypatch.setattr(downloads_endpoint.queue, "push_jobs", lambda jobs: False)
    with TestClient(app) as client:
        response = client.post(
            "/api/downloads", json={"url": "https://example.com/fallback"}
        )
    assert response.status_code == 200
    assert response.json()["queue_backend"] == "database"


def test_required_enqueue_failure_does_not_leave_orphan_job(monkeypatch):
    def fail(_jobs):
        raise QueueUnavailable("redis unavailable")

    monkeypatch.setattr(downloads_endpoint.queue, "push_jobs", fail)
    target = "https://example.com/required-redis-failure"
    with TestClient(app) as client:
        response = client.post("/api/downloads", json={"url": target})
    assert response.status_code == 503

    db = SessionLocal()
    try:
        assert db.query(DownloadJob).filter_by(url=target).count() == 0
    finally:
        db.close()


def test_retry_is_idempotent_for_pending_job(monkeypatch):
    db = SessionLocal()
    job = DownloadJob(url="https://example.com/already-pending", status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = job.id
    db.close()

    def unexpected_enqueue(_jobs):
        raise AssertionError("pending job must not be enqueued twice")

    monkeypatch.setattr(downloads_endpoint.queue, "push_jobs", unexpected_enqueue)
    with TestClient(app) as client:
        response = client.post(f"/api/downloads/{job_id}/retry")
    assert response.status_code == 200
    assert response.json()["queue_backend"] == "existing"
    assert response.json()["job"]["retry_count"] == 0


class FailingPipeline:
    def zadd(self, *_args, **_kwargs):
        return self

    def execute(self):
        raise redis.ConnectionError("offline")


class FailingRedis:
    def pipeline(self, transaction=True):
        return FailingPipeline()

    def zpopmax(self, *_args, **_kwargs):
        raise redis.ConnectionError("offline")


def test_optional_queue_failure_returns_database_fallback(monkeypatch):
    from app.queue import redis_queue

    monkeypatch.setattr(redis_queue.settings, "redis_required", False)
    test_queue = RedisQueue(client=FailingRedis())
    assert test_queue.push_jobs([(1, 0)]) is False
    assert test_queue.pop_job() is None


def test_required_queue_failure_is_explicit(monkeypatch):
    from app.queue import redis_queue

    monkeypatch.setattr(redis_queue.settings, "redis_required", True)
    test_queue = RedisQueue(client=FailingRedis())
    try:
        test_queue.push_jobs([(1, 0)])
    except QueueUnavailable:
        pass
    else:
        raise AssertionError("required Redis failure must raise QueueUnavailable")


def test_priority_score_prefers_priority_then_oldest():
    test_queue = RedisQueue(client=FailingRedis())
    assert test_queue._score(2, 200.0) > test_queue._score(1, 100.0)
    assert test_queue._score(1, 100.0) > test_queue._score(1, 200.0)
