from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.schemas.common import BaseResponse
from app.domain.schemas.order_parsing import ParsedOrderData


class OrderConfidenceRequest(BaseModel):
    origin_text: str
    destination_text: str
    notes_text: str = ""
    parsed_order: ParsedOrderData


class OrderConfidenceResponse(BaseResponse):
    system_confidence: float = Field(ge=0.0, le=1.0)
    can_create_ride: bool
    requires_manual_review: bool
    requires_retry: bool
    missing_fields: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    penalties: list[str] = Field(default_factory=list)
