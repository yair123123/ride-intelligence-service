from __future__ import annotations

import logging
import time

from app.clients.openai_audio_client import OpenAIAudioClient
from app.config import Settings
from app.domain.schemas.common import AudioSegment
from app.domain.schemas.transcription import TranscriptionRequest, TranscriptionResponse
from app.services.audio_download_service import AudioDownloadService

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(
        self,
        settings: Settings,
        audio_download_service: AudioDownloadService,
        openai_audio_client: OpenAIAudioClient,
    ) -> None:
        self._settings = settings
        self._download = audio_download_service
        self._client = openai_audio_client

    def transcribe_from_url(self, request: TranscriptionRequest) -> TranscriptionResponse:
        model = request.model or self._settings.openai_transcription_model
        language = request.language or "he"

        start_download = time.perf_counter()
        downloaded = self._download.download(str(request.audio_url))
        download_duration = time.perf_counter() - start_download
        logger.info("audio download finished", extra={"seconds": round(download_duration, 3)})

        start_tx = time.perf_counter()
        provider_response = self._client.transcribe(
            file_bytes=downloaded.file_bytes,
            file_name=downloaded.file_name,
            language=language,
            model=model,
            include_segments=request.include_segments,
        )
        tx_duration = time.perf_counter() - start_tx
        logger.info("audio transcription finished", extra={"seconds": round(tx_duration, 3)})

        segments: list[AudioSegment] = []
        for seg in provider_response.get("segments", []) or []:
            segments.append(
                AudioSegment(
                    start=float(seg.get("start", 0.0)),
                    end=float(seg.get("end", 0.0)),
                    text=str(seg.get("text", "")),
                )
            )

        return TranscriptionResponse(
            success=True,
            provider="openai",
            model=model,
            audio_url=request.audio_url,
            language=language,
            text=str(provider_response.get("text", "")),
            duration_seconds=float(provider_response.get("duration", 0.0) or 0.0),
            segments=segments,
            warnings=[],
        )
