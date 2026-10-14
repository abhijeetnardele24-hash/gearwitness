from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.app.models.database import repo
from backend.app.models.schemas import (
    CaptureViewEnum,
    Inspection,
    InspectionCreate,
    MediaEvidence,
)
from backend.app.services.pipeline import InspectionPipeline
from backend.app.services.storage import InvalidMediaError, save_media_file

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.get("", response_model=List[Inspection])
def list_inspections():
    """Lists all active and completed inspections."""
    return repo.list_inspections()


@router.get("/{inspection_id}", response_model=Inspection)
def get_inspection(inspection_id: str):
    """Retrieves complete inspection session with media, proposals, and checklist."""
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return insp


@router.post("", response_model=Inspection, status_code=201)
def create_inspection(payload: InspectionCreate):
    """Initializes a new return inspection session."""
    try:
        return repo.create_inspection(payload)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


async def _handle_media_upload(
    inspection_id: str,
    file: UploadFile,
    capture_view: CaptureViewEnum,
    is_checkout: bool,
) -> MediaEvidence:
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    content = await file.read()
    try:
        media = save_media_file(
            file_bytes=content,
            original_filename=file.filename or "upload.jpg",
            capture_view=capture_view,
            is_checkout=is_checkout,
        )
        # Persist to SQLite
        updated = repo.add_media_to_inspection(inspection_id, media)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to record uploaded media")
        return media
    except InvalidMediaError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@router.post("/{inspection_id}/upload", response_model=MediaEvidence)
async def upload_inspection_media_route1(
    inspection_id: str,
    file: UploadFile = File(...),
    capture_view: CaptureViewEnum = Form(...),
    is_checkout: bool = Form(...),
):
    """Safely ingests, validates, strips EXIF, and records a checkout or checkin photo."""
    return await _handle_media_upload(inspection_id, file, capture_view, is_checkout)


@router.post("/{inspection_id}/media", response_model=MediaEvidence)
async def upload_inspection_media_route2(
    inspection_id: str,
    file: UploadFile = File(...),
    capture_view: CaptureViewEnum = Form(...),
    is_checkout: bool = Form(...),
):
    """Alias for /upload to match media collection semantics."""
    return await _handle_media_upload(inspection_id, file, capture_view, is_checkout)


@router.post("/{inspection_id}/analyze", response_model=Inspection)
async def analyze_inspection(inspection_id: str):
    """
    Triggers OpenCV geometric alignment and local Gemma candidate proposal extraction.
    Persists proposals and kit updates to database and returns complete updated Inspection.
    """
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    pipeline = InspectionPipeline()

    all_proposals = []
    # Find matched pairs (same capture_view, one checkout, one checkin)
    views = {m.capture_view for m in insp.media}
    for v in views:
        co = next((m for m in insp.media if m.capture_view == v and m.is_checkout), None)
        ci = next((m for m in insp.media if m.capture_view == v and not m.is_checkout), None)
        if co and ci:
            alignment, proposals = await pipeline.process_view_pair(insp, co, ci)
            all_proposals.extend(proposals)

    # Persist all proposals to SQLite
    if all_proposals:
        repo.set_inspection_proposals(inspection_id, all_proposals)

    # Return freshly queried inspection
    return repo.get_inspection(inspection_id)
