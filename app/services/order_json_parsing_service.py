from __future__ import annotations

from app.clients.openai_responses_client import OpenAIResponsesClient
from app.config import Settings
from app.domain.schemas.order_parsing import OrderParseRequest, OrderParseResponse, ParsedOrderData


class OrderJsonParsingService:
    def __init__(self, settings: Settings, responses_client: OpenAIResponsesClient) -> None:
        self._settings = settings
        self._client = responses_client

    @staticmethod
    def _json_schema() -> dict:
        return {
            "type": "object",
            "additionalProperties": False,
            "required": ["origin", "destination", "notes", "parser_confidence", "warnings"],
            "properties": {
                "origin": {"$ref": "#/$defs/location"},
                "destination": {"$ref": "#/$defs/location"},
                "notes": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["raw_text", "clean_text"],
                    "properties": {
                        "raw_text": {"type": "string"},
                        "clean_text": {"type": ["string", "null"]},
                    },
                },
                "parser_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            "$defs": {
                "location": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "raw_text",
                        "city",
                        "street",
                        "house_number",
                        "landmark",
                        "neighborhood",
                        "parsed_confidence",
                        "missing_fields",
                        "ambiguities",
                    ],
                    "properties": {
                        "raw_text": {"type": "string"},
                        "city": {"type": ["string", "null"]},
                        "street": {"type": ["string", "null"]},
                        "house_number": {"type": ["string", "null"]},
                        "landmark": {"type": ["string", "null"]},
                        "neighborhood": {"type": ["string", "null"]},
                        "parsed_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "missing_fields": {"type": "array", "items": {"type": "string"}},
                        "ambiguities": {"type": "array", "items": {"type": "string"}},
                    },
                }
            },
        }

    def parse(self, request: OrderParseRequest) -> OrderParseResponse:
        parsed = self._client.parse_order(
            model=self._settings.openai_parsing_model,
            origin_text=request.origin_text,
            destination_text=request.destination_text,
            notes_text=request.notes_text,
            json_schema=self._json_schema(),
        )
        normalized = ParsedOrderData.model_validate(parsed)
        return OrderParseResponse(success=True, error=None, **normalized.model_dump())
