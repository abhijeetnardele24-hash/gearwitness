import pytest

from backend.app.config import AppMode
from backend.app.models.schemas import (
    BoundingBox,
    CaptureViewEnum,
    ConditionTypeEnum,
    ProposalDecisionEnum,
)
from backend.app.services.fixture_generator import ensure_fixture_images
from backend.app.services.gemma_analyzer import GemmaAnalyzer, encode_image_base64


@pytest.mark.asyncio
async def test_gemma_health_fixture_mode():
    analyzer = GemmaAnalyzer(app_mode=AppMode.FIXTURE)
    connected, model_name, available = await analyzer.check_health()
    assert connected is False
    assert "Fixture" in model_name
    assert available is False


@pytest.mark.asyncio
async def test_gemma_health_local_mode_offline():
    # Points to unrouted port to test graceful offline detection
    analyzer = GemmaAnalyzer(base_url="http://localhost:59999", app_mode=AppMode.LOCAL)
    connected, model_name, available = await analyzer.check_health()
    assert connected is False
    assert available is False


def test_app_mode_local_loads_successfully():
    from backend.app.config import AppMode, Settings
    cfg = Settings(APP_MODE="local")
    assert cfg.APP_MODE == AppMode.LOCAL
    analyzer = GemmaAnalyzer(app_mode=cfg.APP_MODE)
    assert analyzer.app_mode == AppMode.LOCAL
    assert analyzer.base_url == "http://localhost:11434"


def test_app_mode_live_backward_compatible_alias():
    from backend.app.config import AppMode, Settings
    cfg = Settings(APP_MODE="live")
    assert cfg.APP_MODE == AppMode.LOCAL
    analyzer = GemmaAnalyzer(app_mode=cfg.APP_MODE)
    assert analyzer.app_mode == AppMode.LOCAL


@pytest.mark.asyncio
async def test_analyze_crop_pair_local_mode_offline_degraded(tmp_path):
    paths = ensure_fixture_images(str(tmp_path))
    analyzer = GemmaAnalyzer(base_url="http://localhost:59999", app_mode=AppMode.LOCAL)
    bbox = BoundingBox(x=10, y=10, width=50, height=50)
    proposal = await analyzer.analyze_crop_pair(
        inspection_id="insp_test",
        asset_name="Sony FX3",
        view=CaptureViewEnum.FRONT,
        bbox=bbox,
        checkout_crop_path=paths["fx3_front_checkout"],
        checkin_crop_path=paths["fx3_front_checkin"],
        index=0,
    )
    assert proposal.condition_type == ConditionTypeEnum.UNKNOWN
    assert proposal.confidence == 0.0
    assert "[DEGRADED" in proposal.model_rationale
    assert "OFFLINE" in proposal.model_rationale


@pytest.mark.asyncio
async def test_analyze_crop_pair_fixture_scratch(tmp_path):
    paths = ensure_fixture_images(str(tmp_path))
    analyzer = GemmaAnalyzer(app_mode=AppMode.FIXTURE)

    bbox = BoundingBox(x=10, y=10, width=50, height=50)
    proposal = await analyzer.analyze_crop_pair(
        inspection_id="insp_test",
        asset_name="Sony FX3",
        view=CaptureViewEnum.FRONT,
        bbox=bbox,
        checkout_crop_path=paths["fx3_front_checkout"],
        checkin_crop_path=paths["fx3_front_checkin"],
        index=0,
    )

    assert proposal.condition_type == ConditionTypeEnum.SCRATCH
    assert proposal.confidence > 0.8
    assert proposal.operator_decision == ProposalDecisionEnum.PENDING
    assert "gemma" in proposal.model_rationale.lower()


@pytest.mark.asyncio
async def test_analyze_crop_pair_fixture_missing_accessory(tmp_path):
    paths = ensure_fixture_images(str(tmp_path))
    analyzer = GemmaAnalyzer(app_mode=AppMode.FIXTURE)

    bbox = BoundingBox(x=100, y=100, width=60, height=60)
    proposal = await analyzer.analyze_crop_pair(
        inspection_id="insp_test",
        asset_name="Sony FX3",
        view=CaptureViewEnum.ACCESSORIES,
        bbox=bbox,
        checkout_crop_path=paths["fx3_acc_checkout"],
        checkin_crop_path=paths["fx3_acc_checkin"],
        index=0,
    )

    assert proposal.condition_type == ConditionTypeEnum.MISSING_ACCESSORY
    assert proposal.confidence >= 0.9


def test_encode_image_base64(tmp_path):
    p = str(tmp_path / "sample.txt")
    with open(p, "wb") as f:
        f.write(b"HELLO_BASE64")
    encoded = encode_image_base64(p)
    assert isinstance(encoded, str)
    assert len(encoded) > 0
