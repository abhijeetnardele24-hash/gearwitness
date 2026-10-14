import os
import uuid
from typing import List, Tuple

from backend.app.models.schemas import (
    AlignmentResult,
    CaptureViewEnum,
    ChangeProposal,
    ConditionTypeEnum,
    Inspection,
    InspectionStatusEnum,
    MediaEvidence,
)
from backend.app.services.gemma_analyzer import GemmaAnalyzer
from backend.app.services.storage import ensure_upload_dirs
from backend.app.services.vision_alignment import align_and_detect_changes, crop_bounding_box


class InspectionPipeline:
    """
    Coordinates deterministic OpenCV alignment, candidate region proposal,
    multimodal Gemma reasoning, and kit inventory reconciliation.
    """

    def __init__(self, analyzer: GemmaAnalyzer = None):
        self.analyzer = analyzer or GemmaAnalyzer()

    async def process_view_pair(
        self,
        inspection: Inspection,
        checkout_media: MediaEvidence,
        checkin_media: MediaEvidence,
    ) -> Tuple[AlignmentResult, List[ChangeProposal]]:
        """
        Processes a single matched view pair (e.g. FRONT checkout vs FRONT checkin).
        """
        base_dir = ensure_upload_dirs()
        diff_dir = os.path.join(base_dir, "diffs")
        crop_dir = os.path.join(base_dir, "crops")

        # 1. Deterministic CV Alignment & Difference Detection
        alignment, bboxes = align_and_detect_changes(
            checkout_path=checkout_media.storage_path,
            checkin_path=checkin_media.storage_path,
            output_diff_dir=diff_dir,
        )

        proposals: List[ChangeProposal] = []

        # 2. Extract crops and query Gemma/Fixture for each bounding box
        for i, box in enumerate(bboxes):
            crop_id = str(uuid.uuid4())[:8]
            checkout_crop_path = os.path.join(crop_dir, f"crop_checkout_{crop_id}.jpg")
            checkin_crop_path = os.path.join(crop_dir, f"crop_checkin_{crop_id}.jpg")

            crop_bounding_box(checkout_media.storage_path, box, checkout_crop_path)
            crop_bounding_box(checkin_media.storage_path, box, checkin_crop_path)

            proposal = await self.analyzer.analyze_crop_pair(
                inspection_id=inspection.id,
                asset_name=inspection.asset_name,
                view=checkout_media.capture_view,
                bbox=box,
                checkout_crop_path=checkout_crop_path,
                checkin_crop_path=checkin_crop_path,
                index=i,
            )
            proposals.append(proposal)

        # 3. Kit Checklist Auto-Flagging for Accessories view
        if checkout_media.capture_view == CaptureViewEnum.ACCESSORIES:
            has_missing = any(
                p.condition_type == ConditionTypeEnum.MISSING_ACCESSORY for p in proposals
            )
            if has_missing:
                # Flag cable or secondary accessory as missing in checklist
                for item in inspection.kit_checklist:
                    if (
                        "cable" in item.name.lower()
                        or "charger" in item.name.lower()
                        or "cap" in item.name.lower()
                    ):
                        item.is_present_checkin = False
                        break

        # Attach proposals and advance status
        inspection.proposals.extend(proposals)
        inspection.status = InspectionStatusEnum.REVIEW_READY

        return alignment, proposals
