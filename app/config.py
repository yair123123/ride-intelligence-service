from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "ride-intelligence-service"
    app_version: str = "0.1.0"

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_transcription_model: str = Field(
        default="whisper-1", alias="OPENAI_TRANSCRIPTION_MODEL"
    )
    openai_parsing_model: str = Field(default="gpt-4o-mini", alias="OPENAI_PARSING_MODEL")

    http_timeout_seconds: float = Field(default=20.0, alias="HTTP_TIMEOUT_SECONDS")
    download_timeout_seconds: float = Field(
        default=30.0, alias="DOWNLOAD_TIMEOUT_SECONDS"
    )
    max_audio_file_size_mb: int = Field(default=20, alias="MAX_AUDIO_FILE_SIZE_MB")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Rule engine weights
    weight_origin_city: float = 0.12
    weight_origin_street: float = 0.14
    weight_origin_house_number: float = 0.08
    weight_destination_city: float = 0.12
    weight_destination_street: float = 0.14
    weight_destination_house_number: float = 0.08
    weight_high_parser_confidence: float = 0.12
    weight_non_trivial_texts: float = 0.08

    penalty_identical_origin_destination: float = 0.2
    penalty_missing_critical_field: float = 0.08
    penalty_ambiguity: float = 0.06
    penalty_short_transcript: float = 0.1
    penalty_low_information_text: float = 0.08
    penalty_low_parser_confidence: float = 0.12

    parser_confidence_high_threshold: float = 0.8
    parser_confidence_low_threshold: float = 0.45

    min_text_length_non_trivial: int = 8
    min_combined_transcript_length: int = 16

    threshold_can_create_ride: float = 0.8
    threshold_manual_review: float = 0.6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
