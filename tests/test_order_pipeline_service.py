from __future__ import annotations

from app.domain.schemas.order_confidence import OrderConfidenceResponse
from app.domain.schemas.order_parsing import (
    OrderParseResponse,
    ParsedLocation,
    ParsedNotes,
)
from app.domain.schemas.order_pipeline import OrderPipelineRequest
from app.domain.schemas.transcription import TranscriptionResponse
from app.services.order_pipeline_service import OrderPipelineService


class StubTranscriptionService:
    def __init__(self) -> None:
        self._responses = [
            "תל אביב דיזנגוף 10",
            "רמת גן ביאליק 20",
            "בלי מזוודה",
        ]

    def transcribe_from_url(self, request):  # noqa: ANN001
        text = self._responses.pop(0)
        return TranscriptionResponse(
            success=True,
            model="whisper-1",
            audio_url=request.audio_url,
            language="he",
            text=text,
            duration_seconds=1.0,
            segments=[],
            warnings=[],
        )


class StubParsingService:
    def parse(self, request):  # noqa: ANN001
        return OrderParseResponse(
            success=True,
            origin=ParsedLocation(
                raw_text=request.origin_text,
                city="תל אביב",
                street="דיזנגוף",
                house_number="10",
                landmark=None,
                neighborhood=None,
                parsed_confidence=0.9,
                missing_fields=[],
                ambiguities=[],
            ),
            destination=ParsedLocation(
                raw_text=request.destination_text,
                city="רמת גן",
                street="ביאליק",
                house_number="20",
                landmark=None,
                neighborhood=None,
                parsed_confidence=0.9,
                missing_fields=[],
                ambiguities=[],
            ),
            notes=ParsedNotes(raw_text=request.notes_text, clean_text=request.notes_text),
            parser_confidence=0.92,
            warnings=[],
            error=None,
        )


class StubConfidenceService:
    def evaluate(self, request):  # noqa: ANN001
        return OrderConfidenceResponse(
            success=True,
            system_confidence=0.91,
            can_create_ride=True,
            requires_manual_review=False,
            requires_retry=False,
            missing_fields=[],
            reasons=["all good"],
            penalties=[],
            error=None,
        )


def test_pipeline_orchestration_happy_path() -> None:
    service = OrderPipelineService(
        transcription_service=StubTranscriptionService(),
        parsing_service=StubParsingService(),
        confidence_service=StubConfidenceService(),
    )

    request = OrderPipelineRequest(
        origin_audio_url="https://example.com/origin.mp3",
        destination_audio_url="https://example.com/dest.mp3",
        notes_audio_url="https://example.com/notes.mp3",
        language="he",
    )

    result = service.process(request)
    assert result.success is True
    assert result.transcription.origin_text == "תל אביב דיזנגוף 10"
    assert result.parsed_order.parser_confidence == 0.92
    assert result.confidence_evaluation.can_create_ride is True
