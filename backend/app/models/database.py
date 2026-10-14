import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.app.config import settings
from backend.app.models.schemas import (
    Asset,
    AssetCreate,
    BoundingBox,
    CaptureViewEnum,
    ChangeProposal,
    ConditionTypeEnum,
    Inspection,
    InspectionCreate,
    InspectionStatusEnum,
    KitItem,
    MediaEvidence,
    ProposalDecisionEnum,
    SeverityEnum,
)
from backend.app.services.fixture_generator import ensure_fixture_images
from backend.app.services.storage import calculate_sha256, ensure_upload_dirs


class Repository:
    """Thread-safe in-memory and persistent SQLite model repository."""

    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        self.inspections: Dict[str, Inspection] = {}
        self._seed_default_data()

    def _seed_default_data(self):
        """Initializes default asset catalog and preloaded hero demo inspection."""
        ensure_upload_dirs()
        fixture_paths = ensure_fixture_images()

        # Asset 1: Sony FX3 Cinema Kit
        fx3_id = "asset_fx3_cinema"
        kit_items = [
            KitItem(
                id="kit_01",
                name="Sony FX3 Camera Body",
                quantity=1,
                serial_or_part_no="S/N 4892011",
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="kit_02",
                name="FE 24-70mm f/2.8 GM Lens",
                quantity=1,
                serial_or_part_no="S/N 1928374",
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="kit_03",
                name="Dual Fast Battery Charger",
                quantity=1,
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="kit_04",
                name="USB-C 10Gbps Tether Cable",
                quantity=1,
                is_present_checkout=True,
                is_present_checkin=False,
            ),  # Missing on return!
            KitItem(
                id="kit_05",
                name="Pelican Hardcase with Foam Insert",
                quantity=1,
                is_present_checkout=True,
                is_present_checkin=True,
            ),
        ]
        asset_fx3 = Asset(
            id=fx3_id,
            name="Sony FX3 Cinema Kit",
            category="Camera & Lenses",
            serial_number="4892011",
            qr_code="GW-ASSET-4892011",
            kit_items=kit_items,
        )
        self.assets[fx3_id] = asset_fx3

        # Asset 2: DeWalt 20V Max XR Hammer Drill Kit
        dewalt_id = "asset_dewalt_drill"
        dewalt_items = [
            KitItem(
                id="dw_01",
                name="DCD996 Hammer Drill Body",
                quantity=1,
                serial_or_part_no="S/N DW-88219",
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="dw_02",
                name="5.0Ah 20V MAX Battery (2x)",
                quantity=2,
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="dw_03",
                name="Fast Charger Station",
                quantity=1,
                is_present_checkout=True,
                is_present_checkin=True,
            ),
            KitItem(
                id="dw_04",
                name="Heavy Duty Contractor Bag",
                quantity=1,
                is_present_checkout=True,
                is_present_checkin=True,
            ),
        ]
        self.assets[dewalt_id] = Asset(
            id=dewalt_id,
            name="DeWalt 20V Max XR Hammer Drill Kit",
            category="Power Tools",
            serial_number="DW-88219",
            qr_code="GW-ASSET-DW88219",
            kit_items=dewalt_items,
        )

        # Seed Preloaded Hero Demo Inspection
        insp_hero_id = "insp_hero_demo"
        with open(fixture_paths["fx3_front_checkout"], "rb") as f:
            h_front_co = calculate_sha256(f.read())
        with open(fixture_paths["fx3_front_checkin"], "rb") as f:
            h_front_ci = calculate_sha256(f.read())
        with open(fixture_paths["fx3_acc_checkout"], "rb") as f:
            h_acc_co = calculate_sha256(f.read())
        with open(fixture_paths["fx3_acc_checkin"], "rb") as f:
            h_acc_ci = calculate_sha256(f.read())

        media_list = [
            MediaEvidence(
                id="med_front_co",
                filename="fx3_front_checkout.jpg",
                storage_path=fixture_paths["fx3_front_checkout"],
                sha256_hash=h_front_co,
                file_size_bytes=os.path.getsize(fixture_paths["fx3_front_checkout"]),
                mime_type="image/jpeg",
                width=900,
                height=600,
                capture_view=CaptureViewEnum.FRONT,
                is_checkout=True,
            ),
            MediaEvidence(
                id="med_front_ci",
                filename="fx3_front_checkin.jpg",
                storage_path=fixture_paths["fx3_front_checkin"],
                sha256_hash=h_front_ci,
                file_size_bytes=os.path.getsize(fixture_paths["fx3_front_checkin"]),
                mime_type="image/jpeg",
                width=900,
                height=600,
                capture_view=CaptureViewEnum.FRONT,
                is_checkout=False,
            ),
            MediaEvidence(
                id="med_acc_co",
                filename="fx3_accessories_checkout.jpg",
                storage_path=fixture_paths["fx3_acc_checkout"],
                sha256_hash=h_acc_co,
                file_size_bytes=os.path.getsize(fixture_paths["fx3_acc_checkout"]),
                mime_type="image/jpeg",
                width=900,
                height=600,
                capture_view=CaptureViewEnum.ACCESSORIES,
                is_checkout=True,
            ),
            MediaEvidence(
                id="med_acc_ci",
                filename="fx3_accessories_checkin.jpg",
                storage_path=fixture_paths["fx3_acc_checkin"],
                sha256_hash=h_acc_ci,
                file_size_bytes=os.path.getsize(fixture_paths["fx3_acc_checkin"]),
                mime_type="image/jpeg",
                width=900,
                height=600,
                capture_view=CaptureViewEnum.ACCESSORIES,
                is_checkout=False,
            ),
        ]

        hero_proposals = [
            ChangeProposal(
                id="prop_01_scratch",
                inspection_id=insp_hero_id,
                capture_view=CaptureViewEnum.FRONT,
                bounding_box=BoundingBox(x=550, y=200, width=70, height=50),
                checkout_crop_path=fixture_paths["fx3_front_checkout"],
                checkin_crop_path=fixture_paths["fx3_front_checkin"],
                condition_type=ConditionTypeEnum.SCRATCH,
                severity=SeverityEnum.MINOR,
                confidence=0.89,
                description="Linear chassis finish abrasion on upper right housing corner, approx 18mm.",
                model_rationale=f"[{settings.GEMMA_MODEL_NAME}] High-contrast scratch boundary detected that is completely absent from baseline checkout photo.",
                operator_decision=ProposalDecisionEnum.PENDING,
            ),
            ChangeProposal(
                id="prop_02_reflection",
                inspection_id=insp_hero_id,
                capture_view=CaptureViewEnum.FRONT,
                bounding_box=BoundingBox(x=250, y=320, width=45, height=30),
                checkout_crop_path=fixture_paths["fx3_front_checkout"],
                checkin_crop_path=fixture_paths["fx3_front_checkin"],
                condition_type=ConditionTypeEnum.ARTIFACT_LIGHTING,
                severity=SeverityEnum.NONE,
                confidence=0.72,
                description="Harmless specular lighting highlight shift on rubberized grip contour.",
                model_rationale=f"[{settings.GEMMA_MODEL_NAME}] Luminance variation caused by directional lighting; no geometric deformation or material loss.",
                operator_decision=ProposalDecisionEnum.PENDING,
            ),
            ChangeProposal(
                id="prop_03_missing_cable",
                inspection_id=insp_hero_id,
                capture_view=CaptureViewEnum.ACCESSORIES,
                bounding_box=BoundingBox(x=620, y=310, width=130, height=160),
                checkout_crop_path=fixture_paths["fx3_acc_checkout"],
                checkin_crop_path=fixture_paths["fx3_acc_checkin"],
                condition_type=ConditionTypeEnum.MISSING_ACCESSORY,
                severity=SeverityEnum.MODERATE,
                confidence=0.95,
                description="Designated USB-C tether cable compartment in case foam is empty.",
                model_rationale=f"[{settings.GEMMA_MODEL_NAME}] Coiled cable present at checkout is absent in return capture; empty foam recess visible.",
                operator_decision=ProposalDecisionEnum.PENDING,
            ),
        ]

        hero_inspection = Inspection(
            id=insp_hero_id,
            asset_id=fx3_id,
            asset_name="Sony FX3 Cinema Kit",
            serial_number="4892011",
            customer_reference="CUST-7749-BERLIN",
            status=InspectionStatusEnum.REVIEW_READY,
            checkout_timestamp=datetime(2026, 10, 13, 10, 0, tzinfo=timezone.utc),
            checkin_timestamp=datetime(2026, 10, 14, 18, 30, tzinfo=timezone.utc),
            media=media_list,
            proposals=hero_proposals,
            kit_checklist=[k.model_copy() for k in kit_items],
            notes="3-day commercial video shoot rental return. Customer returned kit in person.",
        )
        self.inspections[insp_hero_id] = hero_inspection

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        return self.assets.get(asset_id)

    def list_assets(self) -> List[Asset]:
        return list(self.assets.values())

    def create_asset(self, data: AssetCreate) -> Asset:
        asset_id = f"asset_{uuid.uuid4().hex[:8]}"
        items = [
            KitItem(
                id=f"kit_{uuid.uuid4().hex[:6]}",
                name=k.name,
                quantity=k.quantity,
                description=k.description,
                serial_or_part_no=k.serial_or_part_no,
            )
            for k in data.kit_items
        ]
        asset = Asset(
            id=asset_id,
            name=data.name,
            category=data.category,
            serial_number=data.serial_number,
            qr_code=data.qr_code or f"GW-ASSET-{data.serial_number}",
            kit_items=items,
        )
        self.assets[asset_id] = asset
        return asset

    def get_inspection(self, inspection_id: str) -> Optional[Inspection]:
        return self.inspections.get(inspection_id)

    def list_inspections(self) -> List[Inspection]:
        return list(self.inspections.values())

    def create_inspection(self, data: InspectionCreate) -> Inspection:
        asset = self.get_asset(data.asset_id)
        if not asset:
            raise ValueError(f"Asset '{data.asset_id}' not found.")

        insp_id = f"insp_{uuid.uuid4().hex[:8]}"
        inspection = Inspection(
            id=insp_id,
            asset_id=asset.id,
            asset_name=asset.name,
            serial_number=asset.serial_number,
            customer_reference=data.customer_reference,
            status=InspectionStatusEnum.CREATED,
            kit_checklist=[k.model_copy() for k in asset.kit_items],
            notes=data.notes,
        )
        self.inspections[insp_id] = inspection
        return inspection

    def update_proposal_decision(
        self,
        inspection_id: str,
        proposal_id: str,
        decision: ProposalDecisionEnum,
        operator_notes: Optional[str] = None,
    ) -> ChangeProposal:
        inspection = self.get_inspection(inspection_id)
        if not inspection:
            raise ValueError(f"Inspection '{inspection_id}' not found.")

        target = None
        for p in inspection.proposals:
            if p.id == proposal_id:
                p.operator_decision = decision
                p.operator_notes = operator_notes
                p.resolved_at = datetime.now(timezone.utc)
                target = p
                break

        if not target:
            raise ValueError(f"Proposal '{proposal_id}' not found in inspection '{inspection_id}'.")

        # If all proposals resolved, advance status
        if all(p.operator_decision != ProposalDecisionEnum.PENDING for p in inspection.proposals):
            inspection.status = InspectionStatusEnum.APPROVED

        return target


# Global repository instance
repo = Repository()
