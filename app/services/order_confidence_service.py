from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.domain.schemas.order_confidence import OrderConfidenceRequest, OrderConfidenceResponse


@dataclass
class ConfidenceComputation:
    score: float
    reasons: list[str]
    penalties: list[str]
    missing_fields: list[str]


class OrderConfidenceService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def evaluate(self, request: OrderConfidenceRequest) -> OrderConfidenceResponse:
        comp = self._compute_score(request)
        score = max(0.0, min(1.0, round(comp.score, 4)))

        can_create = score >= self._settings.threshold_can_create_ride
        manual_review = self._settings.threshold_manual_review <= score < self._settings.threshold_can_create_ride
        retry = score < self._settings.threshold_manual_review

        return OrderConfidenceResponse(
            success=True,
            system_confidence=score,
            can_create_ride=can_create,
            requires_manual_review=manual_review,
            requires_retry=retry,
            missing_fields=sorted(set(comp.missing_fields)),
            reasons=comp.reasons,
            penalties=comp.penalties,
            error=None,
        )

    def _compute_score(self, request: OrderConfidenceRequest) -> ConfidenceComputation:
        s = self._settings
        score = 0.0
        reasons: list[str] = []
        penalties: list[str] = []
        missing: list[str] = []

        origin = request.parsed_order.origin
        dest = request.parsed_order.destination
        parser_conf = request.parsed_order.parser_confidence

        def add_if(value: str | None, weight: float, reason: str, missing_name: str) -> None:
            nonlocal score
            if value and value.strip():
                score += weight
                reasons.append(reason)
            else:
                missing.append(missing_name)
                score -= s.penalty_missing_critical_field
                penalties.append(f"missing:{missing_name}")

        add_if(origin.city, s.weight_origin_city, "origin city present", "origin.city")
        add_if(origin.street, s.weight_origin_street, "origin street present", "origin.street")
        add_if(origin.house_number, s.weight_origin_house_number, "origin house number present", "origin.house_number")
        add_if(dest.city, s.weight_destination_city, "destination city present", "destination.city")
        add_if(dest.street, s.weight_destination_street, "destination street present", "destination.street")
        add_if(dest.house_number, s.weight_destination_house_number, "destination house number present", "destination.house_number")

        if parser_conf >= s.parser_confidence_high_threshold:
            score += s.weight_high_parser_confidence
            reasons.append("parser confidence high")
        elif parser_conf <= s.parser_confidence_low_threshold:
            score -= s.penalty_low_parser_confidence
            penalties.append("low parser confidence")

        if (
            len(request.origin_text.strip()) >= s.min_text_length_non_trivial
            and len(request.destination_text.strip()) >= s.min_text_length_non_trivial
        ):
            score += s.weight_non_trivial_texts
            reasons.append("origin/destination texts are non-trivial")

        if request.origin_text.strip() and request.origin_text.strip() == request.destination_text.strip():
            score -= s.penalty_identical_origin_destination
            penalties.append("origin and destination text identical")

        ambiguities = len(origin.ambiguities) + len(dest.ambiguities)
        if ambiguities > 0:
            score -= s.penalty_ambiguity * ambiguities
            penalties.append(f"ambiguities:{ambiguities}")

        combined_text = f"{request.origin_text} {request.destination_text} {request.notes_text}".strip()
        if len(combined_text) < s.min_combined_transcript_length:
            score -= s.penalty_short_transcript
            penalties.append("transcript too short")

        low_info_tokens = {"כן", "לא", "פה", "שם", "whatever", "unknown"}
        words = {w.strip(' ,.!?;:\"\'').lower() for w in combined_text.split() if w.strip()}
        if words and words.issubset(low_info_tokens):
            score -= s.penalty_low_information_text
            penalties.append("low-information transcript")

        return ConfidenceComputation(score=score, reasons=reasons, penalties=penalties, missing_fields=missing)
