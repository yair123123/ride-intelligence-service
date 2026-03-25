from __future__ import annotations

import mimetypes
from urllib.parse import urlparse

import httpx

from app.domain.schemas.transcription import AudioDownloadResult


class AudioDownloadService:
    SUPPORTED_CONTENT_TYPES = {
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "audio/webm",
        "audio/mp4",
        "audio/ogg",
        "audio/flac",
        "application/octet-stream",
    }

    def __init__(self, timeout_seconds: float, max_file_size_mb: int) -> None:
        self._timeout_seconds = timeout_seconds
        self._max_bytes = max_file_size_mb * 1024 * 1024

    def download(self, audio_url: str) -> AudioDownloadResult:
        with httpx.Client(timeout=self._timeout_seconds, follow_redirects=True) as client:
            response = client.get(audio_url)
            response.raise_for_status()

        file_bytes = response.content
        if not file_bytes:
            raise ValueError("Audio download is empty")
        if len(file_bytes) > self._max_bytes:
            raise ValueError("Audio file exceeds configured maximum size")

        content_type = (response.headers.get("content-type") or "").split(";")[0].strip() or None
        if content_type and content_type not in self.SUPPORTED_CONTENT_TYPES:
            raise ValueError(f"Unsupported audio content type: {content_type}")

        parsed = urlparse(audio_url)
        file_name = parsed.path.rsplit("/", 1)[-1] or "audio.bin"
        if "." not in file_name and content_type:
            guessed_ext = mimetypes.guess_extension(content_type) or ".bin"
            file_name = f"audio{guessed_ext}"

        return AudioDownloadResult(
            file_bytes=file_bytes,
            file_name=file_name,
            content_type=content_type,
            size_bytes=len(file_bytes),
        )
