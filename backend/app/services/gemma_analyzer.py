import base64
import json
import logging
import uuid
from typing import Optional, Tuple

import httpx

from backend.app.config import AppMode, settings
from backend.app.models.schemas import (
    BoundingBox,
    CaptureViewEnum,
    ChangeProposal,
    ConditionTypeEnum,
    ProposalDecisionEnum,
    SeverityEnum,
)
from backend.app.services.storage import get_public_url

logger = logging.getLogger(__name__)


def encode_image_base64(image_path: str) -> str:
    """Encodes image file to base64 string for vision API requests."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class GemmaAnalyzer:
    """
    Multimodal Gemma integration client with strict structured output parsing,
    explicit degraded-state handling, and deterministic fixture-mode fallback.
    """

    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model_name: str = settings.GEMMA_MODEL_NAME,
        app_mode: AppMode = settings.APP_MODE,
        timeout: int = settings.MODEL_TIMEOUT_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.app_mode = app_mode
        self.timeout = timeout

    async def check_health(self) -> Tuple[bool, str, bool]:
        """
        Pings local Ollama service to verify connectivity and presence of target model.
        Returns (connected, configured_model, model_present).
        """
        if self.app_mode == AppMode.FIXTURE:
            return False, "Deterministic Fixture Engine", False

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    model_found = any(self.model_name in m for m in models)
                    return True, self.model_name, model_found
                return False, self.model_name, False
        except Exception as err:
            logger.debug("Ollama health probe error: %s", err)
            return False, self.model_name, False

    def _generate_fixture_proposal(
        self,
        inspection_id: str,
        view: CaptureViewEnum,
        bbox: BoundingBox,
        checkout_crop_path: Optional[str],
        checkin_crop_path: Optional[str],
        index: int,
    ) -> ChangeProposal:
        """
        Produces realistic, deterministically grounded change proposals for fixture mode.
        """
        prop_id = f"prop_{uuid.uuid4().hex[:8]}"
        co_url = get_public_url(checkout_crop_path)
        ci_url = get_public_url(checkin_crop_path)

        # Determine likely condition based on view and crop index
        if view == CaptureViewEnum.ACCESSORIES:
            cond = ConditionTypeEnum.MISSING_ACCESSORY
            sev = SeverityEnum.MODERATE
            conf = 0.94
            desc = "Missing accessory in designated tray compartment compared to checkout baseline."
            rationale = "Geometric template alignment confirms empty compartment slot where accessory was present at checkout."
        elif index == 0:
            cond = ConditionTypeEnum.SCRATCH
            sev = SeverityEnum.MINOR
            conf = 0.89
            desc = "Linear surface abrasion on chassis finish, approximately 18mm in length."
            rationale = "High local luminance gradient variance detected in return crop that is absent in checkout baseline."
        elif index == 1:
            cond = ConditionTypeEnum.SCUFF
            sev = SeverityEnum.MINOR
            conf = 0.82
            desc = "Light friction scuff on rubberized grip perimeter."
            rationale = "Edge boundary difference detected in rubberized grip quadrant."
        else:
            cond = ConditionTypeEnum.ARTIFACT_LIGHTING
            sev = SeverityEnum.NONE
            conf = 0.71
            desc = "Specular reflection difference consistent with acute lighting angle shift."
            rationale = (
                "Luminance hotspot without structural edge displacement or geometric deformation."
            )

        return ChangeProposal(
            id=prop_id,
            inspection_id=inspection_id,
            capture_view=view,
            bounding_box=bbox,
            checkout_crop_path=checkout_crop_path,
            checkin_crop_path=checkin_crop_path,
            checkout_crop_url=co_url,
            checkin_crop_url=ci_url,
            condition_type=cond,
            severity=sev,
            confidence=conf,
            description=desc,
            model_rationale=f"[{self.model_name} (Fixture)] {rationale}",
            operator_decision=ProposalDecisionEnum.PENDING,
        )

    async def analyze_crop_pair(
        self,
        inspection_id: str,
        asset_name: str,
        view: CaptureViewEnum,
        bbox: BoundingBox,
        checkout_crop_path: str,
        checkin_crop_path: str,
        index: int = 0,
    ) -> ChangeProposal:
        """
        Inspects aligned before/after crops using multimodal Gemma or deterministic fixture.
        In local mode, if Ollama is unreachable, returns an explicit degraded state
        rather than fabricating a fixture proposal.
        """
        co_url = get_public_url(checkout_crop_path)
        ci_url = get_public_url(checkin_crop_path)

        if self.app_mode == AppMode.FIXTURE:
            return self._generate_fixture_proposal(
                inspection_id, view, bbox, checkout_crop_path, checkin_crop_path, index
            )

        # Local Mode: Call Ollama Gemma Multimodal Endpoint
        try:
            checkout_b64 = encode_image_base64(checkout_crop_path)
            checkin_b64 = encode_image_base64(checkin_crop_path)

            prompt = (
                f"You are a forensic equipment return inspection specialist examining a '{asset_name}' ({view.value} view).\n"
                "Image 1 is the baseline checkout photo. Image 2 is the return check-in photo of the exact same localized area.\n"
                "Classify whether a physical change occurred. You must respond ONLY with a valid JSON object matching this schema:\n"
                "{\n"
                '  "condition_type": "scratch"|"scuff"|"dent"|"crack"|"missing_accessory"|"normal_wear"|"artifact_lighting",\n'
                '  "severity": "none"|"minor"|"moderate"|"severe",\n'
                '  "confidence": 0.0 to 1.0,\n'
                '  "description": "objective factual observation (1-2 sentences)",\n'
                '  "model_rationale": "specific visual difference between checkout and checkin crops"\n'
                "}\n"
                "Do NOT accuse anyone of fraud or deliberate damage. Stick strictly to physical visual evidence."
            )

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [checkout_b64, checkin_b64],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                },
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    resp_json = res.json()
                    response_text = resp_json.get("response", "{}")
                    parsed = json.loads(response_text)

                    cond_str = parsed.get("condition_type", "unknown").lower()
                    sev_str = parsed.get("severity", "minor").lower()

                    cond = (
                        ConditionTypeEnum(cond_str)
                        if cond_str in [c.value for c in ConditionTypeEnum]
                        else ConditionTypeEnum.UNKNOWN
                    )
                    sev = (
                        SeverityEnum(sev_str)
                        if sev_str in [s.value for s in SeverityEnum]
                        else SeverityEnum.MINOR
                    )
                    conf = max(0.0, min(1.0, float(parsed.get("confidence", 0.75))))

                    return ChangeProposal(
                        id=f"prop_{uuid.uuid4().hex[:8]}",
                        inspection_id=inspection_id,
                        capture_view=view,
                        bounding_box=bbox,
                        checkout_crop_path=checkout_crop_path,
                        checkin_crop_path=checkin_crop_path,
                        checkout_crop_url=co_url,
                        checkin_crop_url=ci_url,
                        condition_type=cond,
                        severity=sev,
                        confidence=conf,
                        description=parsed.get(
                            "description", "Condition difference detected in return crop."
                        ),
                        model_rationale=f"[{self.model_name}] {parsed.get('model_rationale', 'Visual change identified.')}",
                        operator_decision=ProposalDecisionEnum.PENDING,
                    )

        except Exception as e:
            logger.warning(
                "Local Gemma multimodal call failed, transitioning to degraded state: %s",
                e,
            )

        # Honest degraded state in local mode: Do NOT pretend model answered
        return ChangeProposal(
            id=f"prop_{uuid.uuid4().hex[:8]}",
            inspection_id=inspection_id,
            capture_view=view,
            bounding_box=bbox,
            checkout_crop_path=checkout_crop_path,
            checkin_crop_path=checkin_crop_path,
            checkout_crop_url=co_url,
            checkin_crop_url=ci_url,
            condition_type=ConditionTypeEnum.UNKNOWN,
            severity=SeverityEnum.NONE,
            confidence=0.0,
            description="Visual difference identified by OpenCV alignment engine. Local Gemma 3 model offline.",
            model_rationale=f"[DEGRADED - {self.model_name} OFFLINE] Multimodal endpoint unavailable. Operator manual decision required.",
            operator_decision=ProposalDecisionEnum.PENDING,
        )
