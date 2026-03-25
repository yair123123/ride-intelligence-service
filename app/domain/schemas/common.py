from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class BaseResponse(BaseModel):
    success: bool = True
    error: ErrorDetail | None = None


class AudioSegment(BaseModel):
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    text: str
