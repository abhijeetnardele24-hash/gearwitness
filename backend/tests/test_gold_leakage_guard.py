import json
import os

import pytest

from backend.app.services.evaluation_runner import (
    FORBIDDEN_GOLD_FIELDS,
    run_gearwitness_pipeline_eval,
    validate_zero_gold_leakage,
)


def test_validate_zero_gold_leakage_clean():
    clean_inputs = [
        {"case_id": "c1", "checkout_image_path": "co.jpg", "checkin_image_path": "ci.jpg"}
    ]
    # Should execute without exception
    validate_zero_gold_leakage(clean_inputs)


def test_validate_zero_gold_leakage_catches_forbidden_fields():
    leaky_inputs = [
        {
            "case_id": "c1",
            "checkout_image_path": "co.jpg",
            "checkin_image_path": "ci.jpg",
            "has_damage": True,  # FORBIDDEN GOLD LABEL
        }
    ]
    with pytest.raises(ValueError, match="SECURITY VIOLATION.*leaks gold"):
        validate_zero_gold_leakage(leaky_inputs)


@pytest.mark.asyncio
async def test_pipeline_eval_rejects_gold_leaks():
    leaky_record = {
        "case_id": "eval_01",
        "checkout_image_path": "co.jpg",
        "checkin_image_path": "ci.jpg",
        "expected_condition": "scratch",  # FORBIDDEN
    }
    with pytest.raises(ValueError, match="SECURITY VIOLATION"):
        await run_gearwitness_pipeline_eval([leaky_record])


def test_physical_benchmark_inputs_have_no_gold_keys():
    inputs_path = os.path.join("data", "benchmark_inputs.jsonl")
    if not os.path.exists(inputs_path):
        pytest.skip("benchmark_inputs.jsonl not yet built")

    with open(inputs_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            record = json.loads(line)
            leaked = FORBIDDEN_GOLD_FIELDS.intersection(record.keys())
            assert not leaked, (
                f"Record #{idx} in benchmark_inputs.jsonl contains forbidden gold fields: {leaked}!"
            )
