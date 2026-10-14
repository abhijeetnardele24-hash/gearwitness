from typing import List

from fastapi import APIRouter, HTTPException

from backend.app.models.database import repo
from backend.app.models.schemas import Asset, AssetCreate

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=List[Asset])
def list_assets():
    """Lists all registered rental assets and their kit item checklists."""
    return repo.list_assets()


@router.get("/{asset_id}", response_model=Asset)
def get_asset(asset_id: str):
    """Retrieves single asset details by ID."""
    asset = repo.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.post("", response_model=Asset, status_code=201)
def create_asset(payload: AssetCreate):
    """Registers a new equipment asset with associated kit checklist."""
    return repo.create_asset(payload)
