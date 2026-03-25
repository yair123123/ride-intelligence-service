from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_order_parsing_service
from app.domain.schemas.order_parsing import OrderParseRequest, OrderParseResponse
from app.services.order_json_parsing_service import OrderJsonParsingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/order-json", tags=["order-json"])


@router.post("/parse", response_model=OrderParseResponse)
def parse_order(
    request: OrderParseRequest,
    service: OrderJsonParsingService = Depends(get_order_parsing_service),
) -> OrderParseResponse:
    try:
        return service.parse(request)
    except (ValueError, httpx.HTTPError) as exc:
        logger.exception("order parse failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "parse_error", "message": str(exc)},
        ) from exc
    except Exception as exc:  # pragma: no cover
        logger.exception("unexpected parsing error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "internal_error", "message": "Internal server error"},
        ) from exc
