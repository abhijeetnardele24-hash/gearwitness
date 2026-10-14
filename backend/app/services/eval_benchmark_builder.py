import json
import os

import cv2
import numpy as np


def build_evaluation_benchmark(
    base_data_dir: str = "data",
    images_subdir: str = "benchmark_images",
):
    """
    Constructs the 40-case matched-pair evaluation benchmark with physical separation
    between inputs (benchmark_inputs.jsonl) and gold standards (benchmark_gold.jsonl).
    Categories:
    - 10 no-change lighting/angle
    - 8 scratch/scuff
    - 6 dent/crack
    - 8 missing accessory
    - 4 occlusion
    - 4 ambiguous / hard edge cases
    """
    img_dir = os.path.join(base_data_dir, images_subdir)
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(base_data_dir, exist_ok=True)

    inputs_path = os.path.join(base_data_dir, "benchmark_inputs.jsonl")
    gold_path = os.path.join(base_data_dir, "benchmark_gold.jsonl")

    inputs_records = []
    gold_records = []

    case_definitions = []

    # 1. 10 No-Change Pairs (harmless lighting shifts, angle perturbations, color temp)
    for i in range(1, 11):
        case_definitions.append({
            "case_id": f"gw_eval_{len(case_definitions)+1:02d}",
            "category": "no_change",
            "asset_name": "Sony FX3 Cinema Kit",
            "view": "front",
            "has_damage": False,
            "expected_condition": "none",
            "expected_severity": "none",
            "missing_items": [],
            "rotation_deg": (i % 3) * 0.8,
            "brightness_shift": (i % 4) * 6 - 8,
            "scratch_coords": None,
            "dent_coords": None,
            "missing_cable": False,
            "occlusion": False,
            "ambiguous": False,
        })

    # 2. 8 Scratch / Scuff Pairs
    for i in range(1, 9):
        case_definitions.append({
            "case_id": f"gw_eval_{len(case_definitions)+1:02d}",
            "category": "scratch_scuff",
            "asset_name": "Sony FX3 Cinema Kit" if i <= 4 else "DeWalt Hammer Drill",
            "view": "front" if i % 2 == 1 else "top",
            "has_damage": True,
            "expected_condition": "scratch" if i <= 5 else "scuff",
            "expected_severity": "minor" if i <= 6 else "moderate",
            "missing_items": [],
            "rotation_deg": 0.5,
            "brightness_shift": -4,
            "scratch_coords": (400 + i * 20, 220 + i * 15, 450 + i * 20, 250 + i * 15),
            "dent_coords": None,
            "missing_cable": False,
            "occlusion": False,
            "ambiguous": False,
        })

    # 3. 6 Dent / Crack Pairs
    for i in range(1, 7):
        case_definitions.append({
            "case_id": f"gw_eval_{len(case_definitions)+1:02d}",
            "category": "dent_crack",
            "asset_name": "DeWalt Hammer Drill" if i <= 3 else "Sony FX3 Cinema Kit",
            "view": "front" if i % 2 == 1 else "back",
            "has_damage": True,
            "expected_condition": "dent" if i <= 3 else "crack",
            "expected_severity": "moderate" if i <= 4 else "severe",
            "missing_items": [],
            "rotation_deg": 1.0,
            "brightness_shift": 5,
            "scratch_coords": None,
            "dent_coords": (320 + i * 30, 280, 22 + i * 2),
            "missing_cable": False,
            "occlusion": False,
            "ambiguous": False,
        })

    # 4. 8 Missing Accessory Pairs
    for i in range(1, 9):
        case_definitions.append({
            "case_id": f"gw_eval_{len(case_definitions)+1:02d}",
            "category": "missing_accessory",
            "asset_name": "Sony FX3 Cinema Kit" if i <= 4 else "DeWalt Hammer Drill",
            "view": "accessories",
            "has_damage": True,
            "expected_condition": "missing_accessory",
            "expected_severity": "moderate",
            "missing_items": ["USB-C 10Gbps Tether Cable"] if i <= 4 else ["Fast Charger Station"],
            "rotation_deg": 0.0,
            "brightness_shift": 0,
            "scratch_coords": None,
            "dent_coords": None,
            "missing_cable": True,
            "occlusion": False,
            "ambiguous": False,
        })

    # 5. 4 Occlusion Pairs (partial shadow or hand partially occluding edge)
    for _i in range(1, 5):
        case_definitions.append({
            "case_id": f"gw_eval_{len(case_definitions)+1:02d}",
            "category": "occlusion",
            "asset_name": "Sony FX3 Cinema Kit",
            "view": "front",
            "has_damage": False,
            "expected_condition": "artifact_lighting",
            "expected_severity": "none",
            "missing_items": [],
            "rotation_deg": 0.8,
            "brightness_shift": -12,
            "scratch_coords": None,
            "dent_coords": None,
            "missing_cable": False,
            "occlusion": True,
            "ambiguous": False,
        })

    # 6. 4 Ambiguous / Hard Edge Cases
    for i in range(1, 5):
        case_definitions.append({
            "case_id": f"gw_eval_{len(case_definitions)+1:02d}",
            "category": "ambiguous",
            "asset_name": "Sony FX3 Cinema Kit",
            "view": "detail",
            "has_damage": (i % 2 == 1),
            "expected_condition": "normal_wear" if i % 2 == 0 else "scratch",
            "expected_severity": "minor" if i % 2 == 1 else "none",
            "missing_items": [],
            "rotation_deg": 2.2,  # Substantial angle skew
            "brightness_shift": 18,
            "scratch_coords": (480, 240, 495, 248) if i % 2 == 1 else None,
            "dent_coords": None,
            "missing_cable": False,
            "occlusion": False,
            "ambiguous": True,
        })

    w, h = 640, 480

    for c in case_definitions:
        case_id = c["case_id"]
        co_filename = f"{case_id}_checkout.jpg"
        ci_filename = f"{case_id}_checkin.jpg"
        co_path = os.path.join(img_dir, co_filename)
        ci_path = os.path.join(img_dir, ci_filename)

        # Baseline Checkout Image
        img_co = np.full((h, w, 3), (240, 238, 236), dtype=np.uint8)
        cv2.rectangle(img_co, (80, 60), (560, 420), (220, 218, 215), -1)
        cv2.rectangle(img_co, (200, 160), (440, 360), (45, 45, 45), -1)
        cv2.circle(img_co, (320, 260), 65, (60, 60, 60), -1)
        cv2.circle(img_co, (320, 260), 30, (25, 60, 90), -1)
        cv2.putText(img_co, c["asset_name"].upper(), (210, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1)

        # Return Checkin Image
        img_ci = img_co.copy()
        if c["brightness_shift"] != 0:
            img_ci = cv2.convertScaleAbs(img_ci, alpha=1.0, beta=c["brightness_shift"])

        # Inject damage if specified
        if c["scratch_coords"]:
            x1, y1, x2, y2 = c["scratch_coords"]
            cv2.line(img_ci, (x1, y1), (x2, y2), (220, 225, 230), 2)

        if c["dent_coords"]:
            dx, dy, r = c["dent_coords"]
            cv2.circle(img_ci, (dx, dy), r, (25, 25, 25), -1)
            cv2.ellipse(img_ci, (dx + 2, dy + 2), (r, r // 2), 30, 0, 360, (15, 15, 15), -1)

        if c["missing_cable"]:
            # Empty accessory compartment
            cv2.rectangle(img_ci, (460, 280), (540, 400), (90, 90, 90), -1)
            cv2.putText(img_ci, "EMPTY", (475, 345), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (140, 140, 140), 1)

        if c["occlusion"]:
            # Partial soft shadow
            cv2.ellipse(img_ci, (120, 120), (90, 50), -25, 0, 360, (160, 160, 160), -1)

        if c["rotation_deg"] > 0:
            rot_mat = cv2.getRotationMatrix2D((w // 2, h // 2), c["rotation_deg"], 1.0)
            img_ci = cv2.warpAffine(img_ci, rot_mat, (w, h), borderValue=(240, 238, 236))

        cv2.imwrite(co_path, img_co)
        cv2.imwrite(ci_path, img_ci)

        # Decoupled Inputs Record (STRICTLY NO GOLD LABELS OR CATEGORY)
        inputs_records.append({
            "case_id": case_id,
            "asset_name": c["asset_name"],
            "view": c["view"],
            "checkout_image_path": co_path,
            "checkin_image_path": ci_path,
            "kit_checklist": ["Camera Body", "24-70mm Lens", "Dual Charger", "USB-C 10Gbps Tether Cable", "Hardcase"],
        })

        # Decoupled Gold Record (Scoring only)
        gold_records.append({
            "case_id": case_id,
            "category": c["category"],
            "has_damage": c["has_damage"],
            "expected_condition": c["expected_condition"],
            "expected_severity": c["expected_severity"],
            "missing_items": c["missing_items"],
            "is_ambiguous": c["ambiguous"],
        })

    with open(inputs_path, "w", encoding="utf-8") as f_in:
        for r in inputs_records:
            f_in.write(json.dumps(r) + "\n")

    with open(gold_path, "w", encoding="utf-8") as f_gold:
        for r in gold_records:
            f_gold.write(json.dumps(r) + "\n")

    return inputs_path, gold_path, len(case_definitions)
