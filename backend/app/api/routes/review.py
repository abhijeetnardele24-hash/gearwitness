
from fastapi import APIRouter, HTTPException

from backend.app.models.database import repo
from backend.app.models.schemas import (
    ChangeProposal,
    ChecklistItemUpdate,
    Inspection,
    KitItem,
    OperatorDecisionUpdate,
)

router = APIRouter(prefix="/inspections", tags=["Operator Review & Approvals"])


def _apply_decision(
    inspection_id: str,
    proposal_id: str,
    payload: OperatorDecisionUpdate,
) -> Inspection:
    notes = payload.notes if payload.notes is not None else payload.operator_notes
    updated_insp = repo.update_proposal_decision(
        inspection_id=inspection_id,
        proposal_id=proposal_id,
        decision=payload.decision,
        notes=notes,
    )
    if not updated_insp:
        raise HTTPException(
            status_code=404,
            detail=f"Proposal '{proposal_id}' or inspection '{inspection_id}' not found",
        )
    return updated_insp


@router.post(
    "/{inspection_id}/proposals/{proposal_id}/decision",
    response_model=Inspection,
    summary="Record operator decision on proposal (Canonical)",
)
def post_proposal_decision(
    inspection_id: str,
    proposal_id: str,
    payload: OperatorDecisionUpdate,
) -> Inspection:
    """Enforces human decision boundary. Returns complete updated Inspection."""
    return _apply_decision(inspection_id, proposal_id, payload)


@router.patch(
    "/{inspection_id}/proposals/{proposal_id}",
    response_model=ChangeProposal,
    summary="Record operator decision on proposal (Legacy / Detail Alias)",
)
def patch_proposal_decision(
    inspection_id: str,
    proposal_id: str,
    payload: OperatorDecisionUpdate,
) -> ChangeProposal:
    """Enforces human decision boundary. Returns updated ChangeProposal."""
    _apply_decision(inspection_id, proposal_id, payload)
    prop = repo.get_proposal(inspection_id, proposal_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return prop


def _apply_checklist(
    inspection_id: str,
    item_id: str,
    is_present: bool,
) -> Inspection:
    updated_insp = repo.update_kit_item_status(
        inspection_id=inspection_id,
        item_id=item_id,
        is_present=is_present,
    )
    if not updated_insp:
        raise HTTPException(
            status_code=404,
            detail=f"Checklist item '{item_id}' or inspection '{inspection_id}' not found",
        )
    return updated_insp


@router.post(
    "/{inspection_id}/checklist/{item_id}",
    response_model=Inspection,
    summary="Update kit checklist item status (Canonical)",
)
def post_checklist_item(
    inspection_id: str,
    item_id: str,
    payload: ChecklistItemUpdate,
) -> Inspection:
    """Updates manual verification status for a specific kit checklist item. Returns complete updated Inspection."""
    return _apply_checklist(inspection_id, item_id, payload.is_present_checkin)


@router.patch(
    "/{inspection_id}/checklist/{item_id}",
    response_model=KitItem,
    summary="Update kit checklist item status (Legacy / Detail Alias)",
)
def patch_checklist_item(
    inspection_id: str,
    item_id: str,
    payload: ChecklistItemUpdate,
) -> KitItem:
    """Updates manual verification status for a specific kit checklist item. Returns updated KitItem."""
    _apply_checklist(inspection_id, item_id, payload.is_present_checkin)
    item = repo.get_kit_item(inspection_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Kit item not found")
    return item


@router.post(
    "/{inspection_id}/approve",
    response_model=Inspection,
    summary="Approve inspection and seal manifest",
)
def approve_inspection(inspection_id: str) -> Inspection:
    """
    Server-enforced approval gate:
    1. Inspection must exist.
    2. Zero proposals may remain in 'pending' status.
    3. All kit items must have an explicit verification status.
    Returns complete updated Inspection with status 'approved'.
    """
    try:
        return repo.approve_inspection(inspection_id)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
