from fastapi import APIRouter

from backend.app.api.routes import assets, health, inspections, reports, review

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(assets.router)
api_router.include_router(inspections.router)
api_router.include_router(review.router)
api_router.include_router(reports.router)
