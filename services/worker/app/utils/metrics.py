from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional

registry = CollectorRegistry()

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# Download metrics
downloads_total = Counter(
    'downloads_total',
    'Total downloads',
    ['status', 'platform'],
    registry=registry
)

download_duration_seconds = Histogram(
    'download_duration_seconds',
    'Download duration in seconds',
    ['platform'],
    registry=registry
)

downloads_active = Gauge(
    'downloads_active',
    'Currently active downloads',
    registry=registry
)

downloads_queued = Gauge(
    'downloads_queued',
    'Downloads waiting in queue',
    registry=registry
)

# Processing metrics
processing_jobs_total = Counter(
    'processing_jobs_total',
    'Total processing jobs',
    ['tool_type', 'status'],
    registry=registry
)

processing_duration_seconds = Histogram(
    'processing_duration_seconds',
    'Processing duration in seconds',
    ['tool_type'],
    registry=registry
)

# System metrics
worker_uptime_seconds = Gauge(
    'worker_uptime_seconds',
    'Worker uptime in seconds',
    registry=registry
)

queue_size = Gauge(
    'queue_size',
    'Current queue size',
    ['queue_type'],
    registry=registry
)

def record_http_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request metrics"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

def record_download(status: str, platform: Optional[str] = None, duration: Optional[float] = None):
    """Record download metrics"""
    downloads_total.labels(status=status, platform=platform or 'unknown').inc()
    if duration is not None:
        download_duration_seconds.labels(platform=platform or 'unknown').observe(duration)

def record_processing_job(tool_type: str, status: str, duration: Optional[float] = None):
    """Record processing job metrics"""
    processing_jobs_total.labels(tool_type=tool_type, status=status).inc()
    if duration is not None:
        processing_duration_seconds.labels(tool_type=tool_type).observe(duration)

def set_active_downloads(count: int):
    """Set active downloads gauge"""
    downloads_active.set(count)

def set_queued_downloads(count: int):
    """Set queued downloads gauge"""
    downloads_queued.set(count)

def set_queue_size(queue_type: str, size: int):
    """Set queue size gauge"""
    queue_size.labels(queue_type=queue_type).set(size)

def set_worker_uptime(seconds: float):
    """Set worker uptime"""
    worker_uptime_seconds.set(seconds)

def get_metrics() -> bytes:
    """Get metrics in Prometheus format"""
    return generate_latest(registry)

def get_content_type() -> str:
    """Get Prometheus content type"""
    return CONTENT_TYPE_LATEST