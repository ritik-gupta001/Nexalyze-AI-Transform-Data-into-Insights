from fastapi import APIRouter
from app.models.schemas_tasks import HealthResponse
from app.core.config import get_settings
from datetime import datetime

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )
