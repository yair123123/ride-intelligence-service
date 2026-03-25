from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_order_pipeline_service
from app.domain.schemas.order_pipeline import OrderPipelineRequest, OrderPipelineResponse
from app.services.order_pipeline_service import OrderPipelineService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/order-pipeline", tags=["order-pipeline"])


@router.post("/process", response_model=OrderPipelineResponse)
def process_order_pipeline(
    request: OrderPipelineRequest,
    service: OrderPipelineService = Depends(get_order_pipeline_service),
) -> OrderPipelineResponse:
    try:
        return service.process(request)
    except Exception as exc:  # pragma: no cover
        logger.exception("pipeline processing failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "internal_error", "message": "Internal server error"},
        ) from exc
