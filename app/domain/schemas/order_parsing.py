from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.schemas.common import BaseResponse


class OrderParseRequest(BaseModel):
    origin_text: str
    destination_text: str
    notes_text: str = ""


class ParsedLocation(BaseModel):
    raw_text: str
    city: str | None = None
    street: str | None = None
    house_number: str | None = None
    landmark: str | None = None
    neighborhood: str | None = None
    parsed_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    missing_fields: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)


class ParsedNotes(BaseModel):
    raw_text: str
    clean_text: str | None = None


class ParsedOrderData(BaseModel):
    origin: ParsedLocation
    destination: ParsedLocation
    notes: ParsedNotes
    parser_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)


class OrderParseResponse(BaseResponse):
    origin: ParsedLocation
    destination: ParsedLocation
    notes: ParsedNotes
    parser_confidence: float = Field(ge=0.0, le=1.0)
    warnings: list[str] = Field(default_factory=list)
