from __future__ import annotations

import json
from typing import Any

import httpx


class OpenAIResponsesClient:
    """Thin OpenAI Responses API client for strict structured extraction."""

    def __init__(self, api_key: str, timeout_seconds: float) -> None:
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def parse_order(
        self,
        model: str,
        origin_text: str,
        destination_text: str,
        notes_text: str,
        json_schema: dict[str, Any],
    ) -> dict[str, Any]:
        instruction = (
            "You are a Hebrew taxi-order extraction engine. "
            "Extract only data directly supported by evidence in text. "
            "Preserve uncertainty, use null for unknown fields, report missing fields and ambiguities. "
            "Do not fabricate city, street, or house_number."
        )

        payload = {
            "model": model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": instruction}]},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Extract structured order JSON from:\n"
                                f"origin_text: {origin_text}\n"
                                f"destination_text: {destination_text}\n"
                                f"notes_text: {notes_text}"
                            ),
                        }
                    ],
                },
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "order_extraction",
                    "schema": json_schema,
                    "strict": True,
                }
            },
        }

        with httpx.Client(timeout=self._timeout_seconds) as client:
            response = client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        output_text = data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return json.loads(output_text)

        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return json.loads(content["text"])

        raise ValueError("No structured output returned from OpenAI Responses API")
