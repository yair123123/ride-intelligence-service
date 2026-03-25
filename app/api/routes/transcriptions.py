from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_transcription_service
from app.domain.schemas.transcription import TranscriptionRequest, TranscriptionResponse
from app.services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/transcriptions", tags=["transcriptions"])


@router.post("", response_model=TranscriptionResponse)
def transcribe_audio(
    request: TranscriptionRequest,
    service: TranscriptionService = Depends(get_transcription_service),
) -> TranscriptionResponse:
    try:
        return service.transcribe_from_url(request)
    except (ValueError, httpx.HTTPError) as exc:
        logger.exception("transcription failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "transcription_error", "message": str(exc)},
        ) from exc
    except Exception as exc:  # pragma: no cover
        logger.exception("unexpected transcription error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "internal_error", "message": "Internal server error"},
        ) from exc
