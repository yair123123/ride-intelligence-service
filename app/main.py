from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.order_confidence import router as order_confidence_router
from app.api.routes.order_parsing import router as order_parsing_router
from app.api.routes.order_pipeline import router as order_pipeline_router
from app.api.routes.transcriptions import router as transcriptions_router
from app.config import get_settings
from app.utils.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router)
app.include_router(transcriptions_router)
app.include_router(order_parsing_router)
app.include_router(order_confidence_router)
app.include_router(order_pipeline_router)
