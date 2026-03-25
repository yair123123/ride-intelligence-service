from __future__ import annotations

from functools import lru_cache

from app.clients.openai_audio_client import OpenAIAudioClient
from app.clients.openai_responses_client import OpenAIResponsesClient
from app.config import Settings, get_settings
from app.services.audio_download_service import AudioDownloadService
from app.services.order_confidence_service import OrderConfidenceService
from app.services.order_json_parsing_service import OrderJsonParsingService
from app.services.order_pipeline_service import OrderPipelineService
from app.services.transcription_service import TranscriptionService


@lru_cache(maxsize=1)
def get_audio_download_service() -> AudioDownloadService:
    settings = get_settings()
    return AudioDownloadService(
        timeout_seconds=settings.download_timeout_seconds,
        max_file_size_mb=settings.max_audio_file_size_mb,
    )


@lru_cache(maxsize=1)
def get_openai_audio_client() -> OpenAIAudioClient:
    settings = get_settings()
    return OpenAIAudioClient(
        api_key=settings.openai_api_key,
        timeout_seconds=settings.http_timeout_seconds,
    )


@lru_cache(maxsize=1)
def get_openai_responses_client() -> OpenAIResponsesClient:
    settings = get_settings()
    return OpenAIResponsesClient(
        api_key=settings.openai_api_key,
        timeout_seconds=settings.http_timeout_seconds,
    )


@lru_cache(maxsize=1)
def get_transcription_service() -> TranscriptionService:
    return TranscriptionService(
        settings=get_settings(),
        audio_download_service=get_audio_download_service(),
        openai_audio_client=get_openai_audio_client(),
    )


@lru_cache(maxsize=1)
def get_order_parsing_service() -> OrderJsonParsingService:
    return OrderJsonParsingService(
        settings=get_settings(),
        responses_client=get_openai_responses_client(),
    )


@lru_cache(maxsize=1)
def get_order_confidence_service() -> OrderConfidenceService:
    return OrderConfidenceService(settings=get_settings())


@lru_cache(maxsize=1)
def get_order_pipeline_service() -> OrderPipelineService:
    return OrderPipelineService(
        transcription_service=get_transcription_service(),
        parsing_service=get_order_parsing_service(),
        confidence_service=get_order_confidence_service(),
    )


def get_app_settings() -> Settings:
    return get_settings()
