from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.models.database import repo
from backend.app.models.schemas import ChangeProposal, OperatorDecisionUpdate

router = APIRouter(prefix="/inspections", tags=["Operator Review"])


class ChecklistItemUpdate(BaseModel):
    is_present_checkin: bool


@router.patch("/{inspection_id}/proposals/{proposal_id}", response_model=ChangeProposal)
def update_proposal_decision(
    inspection_id: str,
    proposal_id: str,
    payload: OperatorDecisionUpdate,
):
    """
    Enforces the human decision boundary: operator must actively confirm,
    dismiss, or flag a proposal as uncertain.
    """
    try:
        return repo.update_proposal_decision(
            inspection_id=inspection_id,
            proposal_id=proposal_id,
            decision=payload.decision,
            operator_notes=payload.operator_notes,
        )
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err


@router.patch("/{inspection_id}/checklist/{item_id}")
def update_checklist_item(
    inspection_id: str,
    item_id: str,
    payload: ChecklistItemUpdate,
):
    """Updates manual verification status for a specific kit checklist item."""
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    target = next((item for item in insp.kit_checklist if item.id == item_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    target.is_present_checkin = payload.is_present_checkin
    return target
