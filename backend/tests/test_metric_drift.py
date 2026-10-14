"""
Regression test suite ensuring zero drift between data/evaluation_metrics.json
and the documented metrics in docs/EVALUATION.md.
"""

import json
from pathlib import Path


def test_metric_drift_against_documented_evaluation():
    metrics_path = Path("data/evaluation_metrics.json")
    assert metrics_path.exists(), "evaluation_metrics.json must exist"

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    eval_md_path = Path("docs/EVALUATION.md")
    assert eval_md_path.exists(), "docs/EVALUATION.md must exist"

    eval_text = eval_md_path.read_text(encoding="utf-8")

    # Sample count
    sample_count = str(metrics_data["sample_count"])
    assert f"{sample_count} Distinct Cases" in eval_text or f"Sample Count | {sample_count}" in eval_text

    # Verify each result matches documented values
    for res in metrics_data["results"]:
        prec_str = f"{res['proposed_region_precision']:.3f}"
        rec_str = f"{res['proposed_region_recall']:.3f}"
        f1_str = f"{res['proposed_region_f1']:.3f}"

        assert prec_str in eval_text, f"Precision {prec_str} missing from EVALUATION.md"
        assert rec_str in eval_text, f"Recall {rec_str} missing from EVALUATION.md"
        assert f1_str in eval_text, f"F1 {f1_str} missing from EVALUATION.md"
