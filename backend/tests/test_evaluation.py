import json
import os

import pytest

from backend.app.services.eval_benchmark_builder import build_evaluation_benchmark
from backend.app.services.evaluation_runner import run_full_benchmark


def test_build_evaluation_benchmark_counts(tmp_path):
    in_path, gd_path, count = build_evaluation_benchmark(base_data_dir=str(tmp_path))
    assert count == 40
    assert os.path.exists(in_path)
    assert os.path.exists(gd_path)

    with open(in_path, "r", encoding="utf-8") as f:
        in_lines = [line for line in f if line.strip()]
    assert len(in_lines) == 40

    with open(gd_path, "r", encoding="utf-8") as f:
        gd_lines = [line for line in f if line.strip()]
    assert len(gd_lines) == 40


@pytest.mark.asyncio
async def test_run_full_benchmark_output(tmp_path):
    output = await run_full_benchmark(base_data_dir=str(tmp_path), write_artifacts=True)
    assert output["sample_count"] == 40
    assert len(output["results"]) == 2

    # Verify required truthfulness metadata fields
    assert output["execution_mode"] == "fixture"
    assert output["classifier_type"] == "Deterministic Fixture Classifier"
    assert output["live_model_executed"] is False
    assert output["model_endpoint_reachable"] is False
    assert output["model_name"] == "gemma3:4b"
    assert "evaluated_commit_sha" in output

    metrics_file = tmp_path / "evaluation_metrics.json"
    manifest_file = tmp_path / "evaluation_run_manifest.json"

    assert metrics_file.exists()
    assert manifest_file.exists()

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    assert manifest_data["sample_count"] == 40
    assert manifest_data["evidence_commit_sha"] is None
    assert manifest_data["live_model_executed"] is False
    assert manifest_data["execution_mode"] == "fixture"
    assert manifest_data["classifier_type"] == "Deterministic Fixture Classifier"
    assert "provenance_note" in manifest_data


@pytest.mark.asyncio
async def test_fixture_results_never_labeled_as_live_gemma(tmp_path):
    output = await run_full_benchmark(base_data_dir=str(tmp_path), write_artifacts=False)
    system_names = [res["system_name"] for res in output["results"]]

    # Strictly forbidden labels when live model did not execute
    assert "GearWitness Hybrid (CV + Gemma)" not in system_names
    assert "GearWitness Pipeline (CV + Live Gemma 3)" not in system_names
    assert "GearWitness Fixture Pipeline (CV + Deterministic Fixture Classifier)" in system_names
    assert output["live_model_executed"] is False
