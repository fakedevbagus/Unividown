from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from enum import Enum


class QualityEnum(str, Enum):
    BEST = "best"
    P1080 = "1080"
    P720 = "720"
    P480 = "480"
    P360 = "360"
    AUDIO = "audio"
    MP3 = "mp3"


class ToolTypeEnum(str, Enum):
    CONVERT = "convert"
    TRIM = "trim"
    COMPRESS = "compress"
    MERGE = "merge"


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class DownloadRequest(BaseModel):
    url: HttpUrl
    quality: QualityEnum = Field(default=QualityEnum.BEST)
    format: Optional[str] = Field(default="mp4", pattern="^(mp4|mkv|webm|avi|mov|flv|mp3|m4a|wav|flac|ogg)$")
    bitrate: Optional[int] = Field(default=None, ge=64, le=320)
    priority: int = Field(default=0, ge=0, le=10)


class BatchDownloadRequest(BaseModel):
    urls: List[HttpUrl] = Field(..., min_length=1, max_length=50)
    quality: QualityEnum = Field(default=QualityEnum.BEST)


class ConvertRequest(BaseModel):
    format: str = Field(default="mp4", pattern="^(mp4|mkv|webm|avi|mov|flv|mp3|m4a|wav|flac|ogg)$")


class TrimRequest(BaseModel):
    start: float = Field(default=0, ge=0)
    end: float = Field(default=10, gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {"start": 0.0, "end": 10.0}
        }


class CompressRequest(BaseModel):
    bitrate: str = Field(default="1000k", pattern="^\\d+[kKmMgG]?$")


class MergeRequest(BaseModel):
    pass  # Files handled via multipart


class RetryRequest(BaseModel):
    pass


class PaginationParams(BaseModel):
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class JobFilter(BaseModel):
    status: Optional[JobStatusEnum] = None


class SettingsUpdate(BaseModel):
    download_dir: Optional[str] = None
    max_concurrent: Optional[int] = Field(default=None, ge=1, le=10)