import threading


class DownloadCancellationRegistry:
    """Process-local cooperative cancellation flags for active downloads."""

    def __init__(self):
        self._cancelled: set[int] = set()
        self._lock = threading.Lock()

    def request(self, job_id: int) -> None:
        with self._lock:
            self._cancelled.add(job_id)

    def is_requested(self, job_id: int) -> bool:
        with self._lock:
            return job_id in self._cancelled

    def clear(self, job_id: int) -> None:
        with self._lock:
            self._cancelled.discard(job_id)


cancellation_registry = DownloadCancellationRegistry()