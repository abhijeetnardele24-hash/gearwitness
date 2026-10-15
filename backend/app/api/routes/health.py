from fastapi import APIRouter

from backend.app.config import settings
from backend.app.models.schemas import HealthResponse
from backend.app.services.gemma_analyzer import GemmaAnalyzer

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Returns application health, operating mode, and local Gemma connectivity."""
    analyzer = GemmaAnalyzer()
    connected, model_name, available = await analyzer.check_health()
    return HealthResponse(
        status="healthy",
        app_mode=settings.APP_MODE.value,
        version=settings.APP_VERSION,
        ollama_connected=connected,
        model_name=model_name,
        target_model=settings.GEMMA_MODEL_NAME,
        model_available=available,
    )
