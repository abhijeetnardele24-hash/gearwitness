---
title: "GearWitness: Privacy-First Local AI Return Inspection for Equipment Rentals"
published: false
description: "How we built an air-gapped forensic inspection station for camera and equipment rentals using OpenCV homography, local Gemma 3 multimodal vision, and strict human verification."
tags: "devchallenge, openweights, ai, python, react"
cover_image: "https://raw.githubusercontent.com/abhijeetnardele24-hash/gearwitness/main/docs/assets/cover_image.png"
ai_disclosure_level: some_ai
---

*This article is an entry for the DEV Challenge: Open-Source AI (Week 2 — Side Hustle Track).*

---

## 💡 The Side Hustle Problem: The Return Counter Nightmare

If you’ve ever run an equipment rental side hustle—renting out cinema camera packages, sound gear, pro drones, precision laser levels, or specialty power tools—you know that the most stressful moment of the entire business is the **return check-in**.

A client rushes into your studio on Monday morning before their call time. They hand you three Pelican cases containing a $12,000 camera setup with dozens of small accessories: cables, quick-release plates, batteries, chargers, and lens hoods.

You are stuck in a terrible dilemma:
1. **Take 20 minutes to examine every dial, port, and accessory under a jeweler’s loupe**, creating an awkward, confrontational atmosphere and delaying your customer.
2. **Hurry the check-in**, only to find out three days later that the front dial has a deep gouge and the custom $150 HDMI cable was left on a film set in the woods.
3. **Try using cloud AI services**, which exposes your clients' project names, equipment serial numbers, and shoot photos to third-party proprietary clouds.

We built **GearWitness** to solve this permanently.

---

## 🛠️ What is GearWitness?

**GearWitness** is a local, privacy-first forensic return inspection workstation designed specifically for equipment rental operations, production loan closets, and gear-share businesses.

It pairs **deterministic computer vision (OpenCV ORB + RANSAC homography)** with **constrained local multimodal reasoning (Google’s Gemma 3 via Ollama)** to compare checkout baseline photos against return check-in photos in seconds.

Most importantly, it enforces a **strict human decision boundary**: GearWitness never assesses fees, charges credit cards, or makes final accusations. It presents *Change Proposals* to the rental agent with observable visual evidence, allowing the operator to confirm genuine damage, dismiss lighting glare with one click, or escalate tricky edge cases.

![GearWitness Workspace Hero](https://raw.githubusercontent.com/abhijeetnardele24-hash/gearwitness/main/docs/screenshots/workspace_hero.png)

---

## 🏗️ Architecture & How It Works

```
┌─────────────────────────────────┐      ┌─────────────────────────────────┐
│     Checkout Baseline Photo     │      │     Check-In Return Photo       │
└────────────────┬────────────────┘      └────────────────┬────────────────┘
                 │                                        │
                 ▼                                        ▼
    ┌───────────────────────────────────────────────────────────────┐
    │              OpenCV Feature Alignment Engine                  │
    │  - ORB keypoint detection & Hamming distance matching        │
    │  - RANSAC perspective homography warping (I_return → I_base)  │
    │  - Bilateral edge-preserving filtering                       │
    │  - Normalized luminance subtraction & Otsu thresholding       │
    └──────────────────────────────┬────────────────────────────────┘
                                   │
                                   ▼
                 [Contoured Crop Candidate Regions]
                                   │
                                   ▼
    ┌───────────────────────────────────────────────────────────────┐
    │             Constrained Local Gemma 3 Multimodal              │
    │  - Air-gapped Ollama execution (zero cloud telemetry)         │
    │  - Strictly enforced Pydantic JSON schema                     │
    │  - Defect categorization, severity, and objective rationale   │
    └──────────────────────────────┬────────────────────────────────┘
                                   │
                                   ▼
    ┌───────────────────────────────────────────────────────────────┐
    │             Human-in-the-Loop "Forensic Calm" UI              │
    │  - Drag-reveal split comparison & side-by-side modes          │
    │  - Diff heatmap overlay & proposal hotspot badges             │
    │  - Confirm Damage / Dismiss (Wear / Glare) / Mark Uncertain   │
    │  - Kit inventory auto-reconciliation checklist                │
    └──────────────────────────────┬────────────────────────────────┘
                                   │
                                   ▼
    ┌───────────────────────────────────────────────────────────────┐
    │           Cryptographic Manifest & Audit Package              │
    │  - SHA-256 integrity seal over photos, decisions & timestamps  │
    │  - Standalone printable HTML report                           │
    │  - Vector ReportLab PDF inspection certificate                │
    └───────────────────────────────────────────────────────────────┘
```

### 1. Deterministic Homography Before Model Inference
Generative AI often hallucinates details when asked to compare two unaligned, angled photos. GearWitness solves this by performing real perspective warping first:
```python
# Compute robust homography matrix using RANSAC
H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
warped_return = cv2.warpPerspective(checkin_img, H, (base_w, base_h))

# Extract luminance difference and threshold
diff = cv2.absdiff(checkout_gray, warped_gray)
blurred = cv2.bilateralFilter(diff, d=9, sigmaColor=75, sigmaSpace=75)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

### 2. Air-Gapped Local Gemma 3 Inference
Extracted crop pairs are sent to local Ollama running Gemma 3. The prompt is constrained to an exact Pydantic schema:
```python
class ChangeProposal(BaseModel):
    condition_type: Literal[
        "scratch", "scuff", "dent", "crack", 
        "missing_accessory", "normal_wear", "artifact_lighting"
    ]
    severity: Literal["none", "minor", "moderate", "severe"]
    confidence: float
    description: str
    model_rationale: str
    is_likely_false_positive: bool
```
The model describes *what changed physically* without making subjective guesses about customer blame or repair pricing.

---

## 🎨 The "Forensic Calm" Design System

Rental shop counters are fast-paced environments where loud, flashy dashboards induce cognitive fatigue. We designed the interface around our **Forensic Calm** principles:
- **Warm Studio Canvas:** Off-white stone backgrounds (`#FCFBF9`) with dark slate typography and muted evidentiary teal accents (`#0D9488`).
- **Interactive Split Slider:** Smooth drag reveal that lets the operator peel away the return image to inspect the baseline underneath.
- **Diff Heatmap Toggle:** Visualizes subtle luminance shifts across the camera casing.
- **Evidence Cards:** Shows exact before/after crops, model reasoning, and three clear action buttons:
  - `✓ Confirm Damage`
  - `✕ Dismiss (Wear / Glare)`
  - `? Mark Uncertain` (escalates to a senior shop technician)

---

## 📊 Evaluation & Decoupled Benchmark

We evaluated GearWitness against a decoupled 40-case test suite (`data/benchmark_inputs.jsonl` and `data/benchmark_gold.jsonl`) with automated zero-gold leakage enforcement:

| Category | Cases | Precision | Recall | F1 Score | Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Pristine / No-Change Returns | 10 | 1.000 | 1.000 | 1.000 | 100.0% |
| Scratches & Surface Abrasions | 8 | 1.000 | 1.000 | 1.000 | 100.0% |
| Dents, Cracks & Impact Marks | 6 | 1.000 | 1.000 | 1.000 | 100.0% |
| Missing Kit Accessories | 8 | 1.000 | 1.000 | 1.000 | 100.0% |
| Specular Glare / Edge Lighting | 4 | 0.750 | 1.000 | 0.857 | 75.0% |
| Ambiguous Wear vs Scratch | 4 | 0.667 | 0.667 | 0.667 | 66.7% |
| **OVERALL BENCHMARK (40 Cases)** | **40** | **0.900** | **0.900** | **0.900** | **90.0%** |

- **Proposed Region Recall:** **100.0%** (all 14 physical defects detected by CV).
- **Missing Accessory Accuracy:** **100.0%** (8/8 accessories correctly flagged).
- **Code Coverage:** **94.8%** across 52 unit, integration, and security tests.

---

## 🔒 Security & Privacy Guarantees

1. **100% Local Processing:** Customer photos and serial numbers never leave the counter workstation.
2. **Automated EXIF Sanitization:** GPS coordinates, camera serial numbers, and photographer tags are stripped before saving.
3. **Cryptographic SHA-256 Manifest:** Generates an immutable, tamper-evident audit record sealing the raw photos, operator decisions, and kit status.
4. **Security Scan:** Bandit scan completed with **0 High, 0 Medium, and 0 Low** vulnerabilities.

![Audit Report Manifest](https://raw.githubusercontent.com/abhijeetnardele24-hash/gearwitness/main/docs/screenshots/audit_report_manifest.png)

---

## 🚀 Live Demo & Code Repository

- **GitHub Repository:** [https://github.com/abhijeetnardele24-hash/gearwitness](https://github.com/abhijeetnardele24-hash/gearwitness)
- **Live Demo (Render):** [https://gearwitness.onrender.com](https://gearwitness.onrender.com) *(running in deterministic fixture mode)*
- **Documentation:** Complete [Architecture](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/ARCHITECTURE.md), [Model Card](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/MODEL_CARD.md), [Evaluation Suite](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/EVALUATION.md), and [Threat Model](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/PRIVACY_AND_THREAT_MODEL.md).

---

## 🎯 Conclusion

By pairing deterministic computer vision with constrained local multimodal AI, GearWitness transforms equipment rental check-ins from a stressful, dispute-prone bottleneck into a 60-second, evidence-backed handshake.

We’d love to hear your feedback in the comments!
