from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class DownloadJob(Base):
    __tablename__ = "download_jobs"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    platform = Column(String, nullable=True)
    title = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending/processing/completed/failed/paused/cancelled
    progress = Column(Float, default=0.0)
    priority = Column(Integer, default=0)
    quality = Column(String, nullable=True)
    bitrate = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "platform": self.platform,
            "title": self.title,
            "thumbnail_url": self.thumbnail_url,
            "status": self.status,
            "progress": self.progress,
            "priority": self.priority,
            "quality": self.quality,
            "bitrate": self.bitrate,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
