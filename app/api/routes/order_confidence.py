from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_order_confidence_service
from app.domain.schemas.order_confidence import OrderConfidenceRequest, OrderConfidenceResponse
from app.services.order_confidence_service import OrderConfidenceService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/order-confidence", tags=["order-confidence"])


@router.post("/evaluate", response_model=OrderConfidenceResponse)
def evaluate_order_confidence(
    request: OrderConfidenceRequest,
    service: OrderConfidenceService = Depends(get_order_confidence_service),
) -> OrderConfidenceResponse:
    try:
        return service.evaluate(request)
    except Exception as exc:  # pragma: no cover
        logger.exception("confidence evaluation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "internal_error", "message": "Internal server error"},
        ) from exc
