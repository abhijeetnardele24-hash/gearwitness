from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class CaptureViewEnum(str, Enum):
    FRONT = "front"
    BACK = "back"
    TOP = "top"
    ACCESSORIES = "accessories"
    DETAIL = "detail"


class ProposalDecisionEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    UNCERTAIN = "uncertain"


class ConditionTypeEnum(str, Enum):
    SCRATCH = "scratch"
    SCUFF = "scuff"
    DENT = "dent"
    CRACK = "crack"
    MISSING_ACCESSORY = "missing_accessory"
    NORMAL_WEAR = "normal_wear"
    ARTIFACT_LIGHTING = "artifact_lighting"
    UNKNOWN = "unknown"


class SeverityEnum(str, Enum):
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"


class KitItem(BaseModel):
    id: str
    name: str
    quantity: int = 1
    description: Optional[str] = None
    is_present_checkout: bool = True
    is_present_checkin: Optional[bool] = None
    serial_or_part_no: Optional[str] = None


class KitItemCreate(BaseModel):
    name: str
    quantity: int = 1
    description: Optional[str] = None
    serial_or_part_no: Optional[str] = None


class ChecklistItemUpdate(BaseModel):
    is_present_checkin: bool


class Asset(BaseModel):
    id: str
    name: str
    category: str
    serial_number: str
    qr_code: Optional[str] = None
    kit_items: List[KitItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssetCreate(BaseModel):
    name: str
    category: str
    serial_number: str
    qr_code: Optional[str] = None
    kit_items: List[KitItemCreate] = Field(default_factory=list)


class MediaEvidence(BaseModel):
    id: str
    filename: str
    storage_path: str
    public_url: str = Field(default="", description="Browser-safe URL for rendering")
    sha256_hash: str
    file_size_bytes: int
    mime_type: str
    width: int
    height: int
    capture_view: CaptureViewEnum
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_checkout: bool  # True = Checkout baseline, False = Checkin return

    @field_validator("public_url", mode="before")
    @classmethod
    def set_public_url(cls, v: Optional[str], info) -> str:
        if v:
            return v
        data = info.data
        path = data.get("storage_path", "")
        from backend.app.services.storage import get_public_url
        return get_public_url(path) or f"/{path}"


class BoundingBox(BaseModel):
    """Normalized bounding box coordinates in 0.0 to 1.0 range."""
    x: float = Field(description="Normalized X origin (0.0 to 1.0)")
    y: float = Field(description="Normalized Y origin (0.0 to 1.0)")
    width: float = Field(description="Normalized Width (0.0 to 1.0)")
    height: float = Field(description="Normalized Height (0.0 to 1.0)")

    @field_validator("x", "y", "width", "height", mode="before")
    @classmethod
    def normalize_coord(cls, v: Union[int, float]) -> float:
        val = float(v)
        # If passed in pixels or percentages (>1.0), auto-normalize
        if val > 1.0:
            if val <= 100.0:
                val = val / 100.0
            else:
                val = min(1.0, val / 1000.0)
        return max(0.0, min(1.0, round(val, 4)))


class AlignmentResult(BaseModel):
    is_aligned: bool
    inlier_count: int
    homography_matrix: Optional[List[List[float]]] = None
    alignment_confidence: float
    insufficient_overlap: bool = False
    difference_score: float = 0.0
    diff_heatmap_path: Optional[str] = None
    diff_heatmap_url: Optional[str] = None


class ChangeProposal(BaseModel):
    id: str
    inspection_id: str
    capture_view: CaptureViewEnum
    bounding_box: BoundingBox
    checkout_crop_path: Optional[str] = None
    checkin_crop_path: Optional[str] = None
    checkout_crop_url: Optional[str] = None
    checkin_crop_url: Optional[str] = None
    condition_type: ConditionTypeEnum
    severity: SeverityEnum = SeverityEnum.MINOR
    confidence: float = Field(ge=0.0, le=1.0)
    description: str
    model_rationale: str
    operator_decision: ProposalDecisionEnum = ProposalDecisionEnum.PENDING
    operator_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None


class OperatorDecisionUpdate(BaseModel):
    decision: ProposalDecisionEnum
    operator_notes: Optional[str] = None
    notes: Optional[str] = None  # Alias for frontend flexibility


class InspectionStatusEnum(str, Enum):
    CREATED = "created"
    CHECKOUT_CAPTURED = "checkout_captured"
    CHECKIN_CAPTURED = "checkin_captured"
    ANALYZING = "analyzing"
    REVIEW_READY = "review_ready"
    APPROVED = "approved"


class Inspection(BaseModel):
    id: str
    asset_id: str
    asset_name: str
    serial_number: str
    customer_reference: str
    status: InspectionStatusEnum = InspectionStatusEnum.CREATED
    checkout_timestamp: Optional[datetime] = None
    checkin_timestamp: Optional[datetime] = None
    media: List[MediaEvidence] = Field(default_factory=list)
    proposals: List[ChangeProposal] = Field(default_factory=list)
    kit_checklist: List[KitItem] = Field(default_factory=list)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InspectionCreate(BaseModel):
    asset_id: str
    customer_reference: str
    notes: Optional[str] = None


class ExportManifest(BaseModel):
    inspection_id: str
    asset_name: str
    serial_number: str
    customer_reference: str
    checkout_timestamp: Optional[str]
    checkin_timestamp: Optional[str]
    generated_at: str
    gearwitness_version: str
    app_mode: str
    model_used: Optional[str]
    source_media_hashes: Dict[str, str]
    total_proposals: int
    confirmed_proposals: int
    dismissed_proposals: int
    uncertain_proposals: int
    checklist_status: Dict[str, bool]
    disclaimer: str
    manifest_digest_sha256: Optional[str] = None
    manifest_hash_sha256: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    app_mode: str
    version: str
    ollama_connected: bool
    model_name: str
    target_model: Optional[str] = None
    model_available: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
