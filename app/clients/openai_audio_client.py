from __future__ import annotations

import io
from typing import Any

import httpx


class OpenAIAudioClient:
    """Thin OpenAI audio transcription client."""

    def __init__(self, api_key: str, timeout_seconds: float) -> None:
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def transcribe(
        self,
        file_bytes: bytes,
        file_name: str,
        language: str,
        model: str,
        include_segments: bool,
    ) -> dict[str, Any]:
        data = {
            "model": model,
            "language": language,
            "response_format": "verbose_json" if include_segments else "json",
        }
        files = {"file": (file_name, io.BytesIO(file_bytes), "application/octet-stream")}

        with httpx.Client(timeout=self._timeout_seconds) as client:
            response = client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                data=data,
                files=files,
            )
            response.raise_for_status()
            return response.json()
