from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl

from app.domain.schemas.common import AudioSegment, BaseResponse


class TranscriptionRequest(BaseModel):
    audio_url: HttpUrl
    language: str = Field(default="he", min_length=2, max_length=10)
    model: str = Field(default="whisper-1")
    include_segments: bool = True


class TranscriptionResponse(BaseResponse):
    provider: str = "openai"
    model: str
    audio_url: HttpUrl
    language: str
    text: str
    duration_seconds: float = Field(default=0.0, ge=0)
    segments: list[AudioSegment] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class AudioDownloadResult(BaseModel):
    file_bytes: bytes
    file_name: str
    content_type: str | None = None
    size_bytes: int = Field(gt=0)
