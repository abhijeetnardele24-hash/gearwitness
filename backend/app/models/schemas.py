from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


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
    sha256_hash: str
    file_size_bytes: int
    mime_type: str
    width: int
    height: int
    capture_view: CaptureViewEnum
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_checkout: bool  # True = Checkout baseline, False = Checkin return


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class AlignmentResult(BaseModel):
    is_aligned: bool
    inlier_count: int
    homography_matrix: Optional[List[List[float]]] = None
    alignment_confidence: float
    insufficient_overlap: bool = False
    difference_score: float = 0.0
    diff_heatmap_path: Optional[str] = None


class ChangeProposal(BaseModel):
    id: str
    inspection_id: str
    capture_view: CaptureViewEnum
    bounding_box: BoundingBox
    checkout_crop_path: Optional[str] = None
    checkin_crop_path: Optional[str] = None
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
    manifest_hash_sha256: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    app_mode: str
    version: str
    ollama_connected: bool
    model_name: str
    model_available: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
