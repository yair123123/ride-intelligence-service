from __future__ import annotations

from app.config import Settings
from app.domain.schemas.order_confidence import OrderConfidenceRequest
from app.domain.schemas.order_parsing import ParsedLocation, ParsedNotes, ParsedOrderData
from app.services.order_confidence_service import OrderConfidenceService


def _settings() -> Settings:
    return Settings.model_validate({"OPENAI_API_KEY": "test-key"})


def _parsed_order(
    *,
    destination_street: str | None = "ביאליק",
    parser_confidence: float = 0.9,
    origin_ambiguities: list[str] | None = None,
    destination_ambiguities: list[str] | None = None,
) -> ParsedOrderData:
    return ParsedOrderData(
        origin=ParsedLocation(
            raw_text="תל אביב דיזנגוף 10",
            city="תל אביב",
            street="דיזנגוף",
            house_number="10",
            ambiguities=origin_ambiguities or [],
            missing_fields=[],
            parsed_confidence=0.9,
        ),
        destination=ParsedLocation(
            raw_text="רמת גן ביאליק 20",
            city="רמת גן",
            street=destination_street,
            house_number="20",
            ambiguities=destination_ambiguities or [],
            missing_fields=[] if destination_street else ["street"],
            parsed_confidence=0.9,
        ),
        notes=ParsedNotes(raw_text="בלי מזוודה", clean_text="בלי מזוודה"),
        parser_confidence=parser_confidence,
        warnings=[],
    )


def test_strong_complete_origin_destination_scores_high() -> None:
    service = OrderConfidenceService(_settings())
    result = service.evaluate(
        OrderConfidenceRequest(
            origin_text="תל אביב דיזנגוף 10",
            destination_text="רמת גן ביאליק 20",
            notes_text="בלי מזוודה",
            parsed_order=_parsed_order(),
        )
    )
    assert result.system_confidence >= 0.8
    assert result.can_create_ride is True


def test_missing_destination_street_penalized() -> None:
    service = OrderConfidenceService(_settings())
    result = service.evaluate(
        OrderConfidenceRequest(
            origin_text="תל אביב דיזנגוף 10",
            destination_text="רמת גן",
            notes_text="",
            parsed_order=_parsed_order(destination_street=None),
        )
    )
    assert "destination.street" in result.missing_fields
    assert result.system_confidence < 0.8


def test_identical_origin_and_destination_penalty() -> None:
    service = OrderConfidenceService(_settings())
    text = "תל אביב דיזנגוף 10"
    result = service.evaluate(
        OrderConfidenceRequest(
            origin_text=text,
            destination_text=text,
            notes_text="",
            parsed_order=_parsed_order(),
        )
    )
    assert any("identical" in p for p in result.penalties)


def test_low_parser_confidence_penalty() -> None:
    service = OrderConfidenceService(_settings())
    result = service.evaluate(
        OrderConfidenceRequest(
            origin_text="תל אביב דיזנגוף 10",
            destination_text="רמת גן ביאליק 20",
            notes_text="",
            parsed_order=_parsed_order(parser_confidence=0.2),
        )
    )
    assert any("low parser confidence" in p for p in result.penalties)


def test_ambiguous_parsing_penalty() -> None:
    service = OrderConfidenceService(_settings())
    result = service.evaluate(
        OrderConfidenceRequest(
            origin_text="דיזנגוף אולי פינת ארלוזורוב",
            destination_text="ביאליק אולי 20",
            notes_text="",
            parsed_order=_parsed_order(origin_ambiguities=["could be two streets"]),
        )
    )
    assert any("ambiguities" in p for p in result.penalties)
