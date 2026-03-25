from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl

from app.domain.schemas.common import BaseResponse
from app.domain.schemas.order_confidence import OrderConfidenceResponse
from app.domain.schemas.order_parsing import OrderParseResponse


class OrderPipelineRequest(BaseModel):
    origin_audio_url: HttpUrl
    destination_audio_url: HttpUrl
    notes_audio_url: HttpUrl
    language: str = Field(default="he", min_length=2, max_length=10)


class PipelineTranscription(BaseModel):
    origin_text: str
    destination_text: str
    notes_text: str


class OrderPipelineResponse(BaseResponse):
    transcription: PipelineTranscription
    parsed_order: OrderParseResponse
    confidence_evaluation: OrderConfidenceResponse
