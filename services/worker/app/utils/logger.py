import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar


# Context variable for request correlation
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        # Add extra fields
        extra_fields = {
            k: v for k, v in record.__dict__.items()
            if k not in {
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'message', 'name', 'pathname', 'process', 'processName',
                'relativeCreated', 'thread', 'threadName', 'exc_info',
                'exc_text', 'stack_info', 'asctime'
            }
        }
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_format: bool = True) -> logging.Logger:
    """Configure application logging."""
    logger = logging.getLogger("unividown")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(f"unividown.{name}" if name else "unividown")


# Initialize default logger
logger = setup_logging()


class LoggerMixin:
    """Mixin class to add logging methods to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__.lower())
        return self._logger
    
    def log_info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)


def log_request(request_id: str, method: str, path: str, client_ip: str, **kwargs):
    """Log incoming request."""
    logger.info(
        "Incoming request",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "client_ip": client_ip,
            **kwargs
        }
    )


def log_response(request_id: str, status_code: int, duration_ms: float, **kwargs):
    """Log outgoing response."""
    logger.info(
        "Response sent",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2),
            **kwargs
        }
    )


def log_download_event(
    event: str,
    job_id: int,
    url: str = None,
    error: str = None,
    **kwargs
):
    """Log download-related events."""
    log_data = {
        "event_type": "download",
        "action": event,
        "job_id": job_id,
    }
    if url:
        log_data["url"] = url
    if error:
        log_data["error"] = error
    log_data.update(kwargs)
    
    logger.info(f"Download {event}", extra=log_data)


def log_processing_event(
    event: str,
    job_id: int,
    tool_type: str = None,
    error: str = None,
    **kwargs
):
    """Log processing-related events."""
    log_data = {
        "event_type": "processing",
        "action": event,
        "job_id": job_id,
    }
    if tool_type:
        log_data["tool_type"] = tool_type
    if error:
        log_data["error"] = error
    log_data.update(kwargs)
    
    logger.info(f"Processing {event}", extra=log_data)


def log_error_with_context(
    error: Exception,
    context: Dict[str, Any] = None,
    request_id: str = None
):
    """Log error with full context."""
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    if context:
        log_data["context"] = context
    if request_id:
        log_data["request_id"] = request_id
    
    logger.error("Application error", extra=log_data, exc_info=True)