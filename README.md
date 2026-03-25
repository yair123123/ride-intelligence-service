# ride-intelligence-service

Standalone internal HTTP microservice that converts generic taxi-order call audio into structured, validated output through a 3-stage pipeline:

1. **Audio URL → transcription** (OpenAI Whisper)
2. **Transcript → structured JSON** (OpenAI Responses API with strict JSON schema)
3. **Structured JSON + text signals → deterministic system confidence + decision** (rule engine)

This service is generic and intentionally does **not** include telephony/session/dispatch/ride allocation business logic.

## Tech Stack

- Python 3.12
- FastAPI
- Pydantic v2 + pydantic-settings
- httpx
- pytest

## Endpoints

### Health
- `GET /health`

### Stage 1: Transcription
- `POST /v1/transcriptions`

Request:
```json
{
  "audio_url": "https://example.com/order.mp3",
  "language": "he",
  "model": "whisper-1",
  "include_segments": true
}
```

### Stage 2: Parse transcript into normalized order JSON
- `POST /v1/order-json/parse`

Request:
```json
{
  "origin_text": "תל אביב דיזנגוף 10",
  "destination_text": "רמת גן ביאליק 20",
  "notes_text": "בלי מזוודה"
}
```

### Stage 3: Deterministic confidence engine
- `POST /v1/order-confidence/evaluate`

Request:
```json
{
  "origin_text": "תל אביב דיזנגוף 10",
  "destination_text": "רמת גן ביאליק 20",
  "notes_text": "בלי מזוודה",
  "parsed_order": {
    "origin": {
      "raw_text": "תל אביב דיזנגוף 10",
      "city": "תל אביב",
      "street": "דיזנגוף",
      "house_number": "10",
      "landmark": null,
      "neighborhood": null,
      "parsed_confidence": 0.9,
      "missing_fields": [],
      "ambiguities": []
    },
    "destination": {
      "raw_text": "רמת גן ביאליק 20",
      "city": "רמת גן",
      "street": "ביאליק",
      "house_number": "20",
      "landmark": null,
      "neighborhood": null,
      "parsed_confidence": 0.9,
      "missing_fields": [],
      "ambiguities": []
    },
    "notes": {
      "raw_text": "בלי מזוודה",
      "clean_text": "בלי מזוודה"
    },
    "parser_confidence": 0.92,
    "warnings": []
  }
}
```

### Full pipeline orchestration
- `POST /v1/order-pipeline/process`

Request:
```json
{
  "origin_audio_url": "https://example.com/origin.mp3",
  "destination_audio_url": "https://example.com/destination.mp3",
  "notes_audio_url": "https://example.com/notes.mp3",
  "language": "he"
}
```

## Environment Variables

- `OPENAI_API_KEY` (required)
- `OPENAI_TRANSCRIPTION_MODEL` (default: `whisper-1`)
- `OPENAI_PARSING_MODEL` (default: `gpt-4o-mini`)
- `HTTP_TIMEOUT_SECONDS` (default: `20`)
- `DOWNLOAD_TIMEOUT_SECONDS` (default: `30`)
- `MAX_AUDIO_FILE_SIZE_MB` (default: `20`)
- `LOG_LEVEL` (default: `INFO`)

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your-key
uvicorn app.main:app --reload --port 8080
```

## Run tests

```bash
pytest -q
```

## Design notes

- Stage boundaries are explicit: transcription, parser confidence, and system confidence are separate concepts.
- System confidence is the only value used for final decisioning (`can_create_ride`, `requires_manual_review`, `requires_retry`).
- External provider payloads are normalized into internal DTOs and not leaked as-is.
