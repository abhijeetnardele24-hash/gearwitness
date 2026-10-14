import pytest

from backend.app.models.database import repo
from backend.app.models.schemas import CaptureViewEnum, InspectionStatusEnum
from backend.app.services.pipeline import InspectionPipeline


@pytest.mark.asyncio
async def test_pipeline_process_hero_view_pair(reset_repo):
    insp = repo.get_inspection("insp_hero_demo")
    assert insp is not None

    co_media = next(
        m for m in insp.media if m.capture_view == CaptureViewEnum.FRONT and m.is_checkout
    )
    ci_media = next(
        m for m in insp.media if m.capture_view == CaptureViewEnum.FRONT and not m.is_checkout
    )

    pipeline = InspectionPipeline()
    alignment, proposals = await pipeline.process_view_pair(insp, co_media, ci_media)

    assert alignment is not None
    assert len(proposals) >= 1
    assert insp.status == InspectionStatusEnum.REVIEW_READY


@pytest.mark.asyncio
async def test_pipeline_reconciles_missing_accessory(reset_repo):
    insp = repo.get_inspection("insp_hero_demo")
    co_media = next(
        m for m in insp.media if m.capture_view == CaptureViewEnum.ACCESSORIES and m.is_checkout
    )
    ci_media = next(
        m for m in insp.media if m.capture_view == CaptureViewEnum.ACCESSORIES and not m.is_checkout
    )

    pipeline = InspectionPipeline()
    alignment, proposals = await pipeline.process_view_pair(insp, co_media, ci_media)

    # Check that cable is flagged missing
    cable_item = next((item for item in insp.kit_checklist if "cable" in item.name.lower()), None)
    assert cable_item is not None
    assert cable_item.is_present_checkin is False
