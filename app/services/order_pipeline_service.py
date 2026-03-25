from __future__ import annotations

from app.domain.schemas.order_confidence import OrderConfidenceRequest
from app.domain.schemas.order_parsing import OrderParseRequest, ParsedOrderData
from app.domain.schemas.order_pipeline import (
    OrderPipelineRequest,
    OrderPipelineResponse,
    PipelineTranscription,
)
from app.domain.schemas.transcription import TranscriptionRequest
from app.services.order_confidence_service import OrderConfidenceService
from app.services.order_json_parsing_service import OrderJsonParsingService
from app.services.transcription_service import TranscriptionService


class OrderPipelineService:
    def __init__(
        self,
        transcription_service: TranscriptionService,
        parsing_service: OrderJsonParsingService,
        confidence_service: OrderConfidenceService,
    ) -> None:
        self._transcription_service = transcription_service
        self._parsing_service = parsing_service
        self._confidence_service = confidence_service

    def process(self, request: OrderPipelineRequest) -> OrderPipelineResponse:
        origin_tx = self._transcription_service.transcribe_from_url(
            TranscriptionRequest(audio_url=request.origin_audio_url, language=request.language)
        )
        destination_tx = self._transcription_service.transcribe_from_url(
            TranscriptionRequest(audio_url=request.destination_audio_url, language=request.language)
        )
        notes_tx = self._transcription_service.transcribe_from_url(
            TranscriptionRequest(audio_url=request.notes_audio_url, language=request.language)
        )

        parsed = self._parsing_service.parse(
            OrderParseRequest(
                origin_text=origin_tx.text,
                destination_text=destination_tx.text,
                notes_text=notes_tx.text,
            )
        )

        confidence = self._confidence_service.evaluate(
            OrderConfidenceRequest(
                origin_text=origin_tx.text,
                destination_text=destination_tx.text,
                notes_text=notes_tx.text,
                parsed_order=ParsedOrderData.model_validate(parsed.model_dump(exclude={"success", "error"})),
            )
        )

        return OrderPipelineResponse(
            success=True,
            transcription=PipelineTranscription(
                origin_text=origin_tx.text,
                destination_text=destination_tx.text,
                notes_text=notes_tx.text,
            ),
            parsed_order=parsed,
            confidence_evaluation=confidence,
            error=None,
        )
