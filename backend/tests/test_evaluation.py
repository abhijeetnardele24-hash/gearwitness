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

    metrics_file = tmp_path / "evaluation_metrics.json"
    manifest_file = tmp_path / "evaluation_run_manifest.json"

    assert metrics_file.exists()
    assert manifest_file.exists()

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)
    assert manifest_data["sample_count"] == 40
    assert manifest_data["evidence_commit_sha"] is None
    assert "provenance_note" in manifest_data
