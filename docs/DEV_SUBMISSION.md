---
title: "GearWitness: Privacy-First Local AI Return Inspection for Equipment Rentals"
published: false
description: "An air-gapped forensic inspection workstation for camera and equipment rentals pairing OpenCV homography with local Gemma 3 multimodal vision and a strict human decision boundary."
tags: "devchallenge, hf26challenge, python, react"
cover_image: "https://raw.githubusercontent.com/abhijeetnardele24-hash/gearwitness/main/docs/assets/cover_image.png"
ai_disclosure_level: some_ai
---

*This article is an entry for the DEV Challenge: Open-Source AI (Week 2 — Side Hustle Track).*

---

## 💡 The Side Hustle Problem: The Return Counter Dilemma

For independent camera rental shops, community equipment libraries, and creators running gear-rental side hustles, the return check-in is the most friction-heavy point in daily operations.

When an expensive cinema camera kit, lighting package, or precision drone is returned, operators face an operational trade-off:
1. **Spend 15–20 minutes inspecting every port, switch, and accessory under a loupe**, keeping customers waiting and creating an uncomfortable, adversarial dynamic at the counter.
2. **Rush the check-in to clear the counter**, discovering days later that a lens element has a hairline scuff or an expensive custom tether cable was left behind on a shoot.
3. **Turn to proprietary cloud inspection APIs**, which risks exposing client project names, customer identities, equipment serial numbers, and unreleased shoot media to third-party cloud platforms with ongoing per-image inference fees.

We built **GearWitness** to give equipment operators a fast, private, and predictable tool for return inspections.

---

## 🎯 Target Audience & Value Proposition (Week 2 Side Hustle Focus)

- **Who Pays & Adopts:** Independent photo/video rental shops, freelance equipment-share side hustles, community tool/gear libraries, and university media loan centers.
- **Direct Practical Value:**
  - **Quicker Counter Check-ins:** Fast alignment and automated delta highlighting reduce manual visual scanning time.
  - **Fewer Missed Accessories:** Template-aligned flat-lay analysis flags missing caps, batteries, and cables before the customer walks out the door.
  - **Calmer, Evidence-Based Conversations:** Paired visual comparisons and objective rationales shift disputes away from subjective memory into shared visual evidence.
- **Predictable Cost & Privacy:** Built entirely on open-source, local components (OpenCV, Gemma 3, Ollama, FastAPI, and SQLite). Running on-premises means zero per-token cloud billing, zero subscription lock-in, and zero cloud data leakage.

---

## 🛠️ What is GearWitness?

**GearWitness** is a local return inspection station that pairs **deterministic computer vision (OpenCV ORB + RANSAC homography)** with **constrained local multimodal reasoning (Google’s Gemma 3 via Ollama)** to compare checkout baseline photos against return check-in photos.

Crucially, GearWitness enforces a **strict human decision boundary**:
- **The software has no automatic charging capability.** It cannot assess fines, bill credit cards, or unilaterally issue repair invoices.
- All potential defects are presented as **Change Proposals** with side-by-side cropped visual evidence, allowing the operator to confirm genuine damage, dismiss benign glare with one click, or escalate edge cases to senior technicians.

![GearWitness Workspace Hero](https://raw.githubusercontent.com/abhijeetnardele24-hash/gearwitness/main/docs/screenshots/workspace_hero.png)

---

## 🏗️ Technical Architecture & Open Innovation

GearWitness is built on modular, replaceable open-source components:

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
    │           Forensic Manifest & Inspection Report               │
    │  - SHA-256 tamper-evident digest over photos & decisions      │
    │  - Standalone printable HTML report                           │
    │  - Vector ReportLab PDF inspection report                     │
    └───────────────────────────────────────────────────────────────┘
```

![Forensic Operator Workflow: Five-Stage Inspection Pipeline](https://raw.githubusercontent.com/abhijeetnardele24-hash/gearwitness/main/docs/assets/forensic_operator_workflow.png)

### 1. Deterministic Homography Before Model Inference
Generative vision models can hallucinate differences when presented with unaligned, slightly rotated photos. GearWitness eliminates this by performing planar perspective rectification first:

```python
# Compute robust homography matrix using RANSAC
H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
warped_return = cv2.warpPerspective(checkin_img, H, (base_w, base_h))

# Extract luminance difference and threshold
diff = cv2.absdiff(checkout_gray, warped_gray)
blurred = cv2.bilateralFilter(diff, d=9, sigmaColor=75, sigmaSpace=75)
_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

### 2. Constrained Local Gemma 3 Multimodal Inference
Aligned crop pairs are evaluated locally by `gemma3:4b` running via Ollama (`>=0.6.0`). The model is strictly constrained to a Pydantic schema:

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
```

The prompt instructs the model to describe *physical, observable deltas* without accusatory language or speculation regarding customer fault.

---

## 🎨 The "Forensic Calm" Design System

Counter desks are busy workspaces where neon alerts and noisy dashboards create stress. GearWitness is styled with a **Forensic Calm** palette:
- **Warm Studio Canvas:** Off-white stone surfaces (`#FCFBF9`) with dark slate typography and muted evidentiary teal accents (`#0D9488`).
- **Interactive Split Slider:** Smooth drag reveal that lets the operator peel away the return image to inspect the baseline underneath.
- **Diff Heatmap Toggle:** Visualizes subtle luminance shifts across the equipment casing.
- **Action-Oriented Evidence Cards:** Every proposal provides clear operator actions:
  - `✓ Confirm Damage`
  - `✕ Dismiss (Wear / Glare)`
  - `? Mark Uncertain` (escalates to senior technician)

---

## 📊 Evaluation & Synthetic Fixture Benchmark

We evaluated GearWitness using a decoupled 40-case test suite (`data/benchmark_inputs.jsonl` and `data/benchmark_gold.jsonl`) with automated zero-gold leakage enforcement. Prediction code runs with zero access to ground truth labels.

The reproducible results recorded in `data/evaluation_metrics.json` are:

| Metric | Deterministic CV Baseline (Pixels) | GearWitness Fixture Pipeline (CV + Deterministic Classifier) |
| :--- | :---: | :---: |
| **Evaluated Cases** | 40 synthetic matched pairs | 40 synthetic matched pairs |
| **True Positives (Damage Detected)** | 24 | 24 |
| **False Positives (Flagged for Review)** | 13 | 13 |
| **False Negatives (Missed Defects)** | 0 | 0 |
| **True Negatives (Clean Confirmed)** | 3 | 3 |
| **Proposed Region Precision** | 0.649 | 0.649 |
| **Proposed Region Recall** | **1.000** (24/24) | **1.000** (24/24) |
| **F1 Score** | **0.787** | **0.787** |
| **No-Change False-Positive Rate** | **0.700** (7/10) | **0.700** (7/10) |
| **Missing Accessory Accuracy** | **1.000** (8/8) | **1.000** (8/8) |

### Key Benchmark Takeaways:
1. **100% Recall Safety Net:** Zero physical damage went undetected across the 40 test cases ($FN = 0$).
2. **Why Gemma and Human Review Are Necessary:** The 0.700 false-positive rate on pristine, no-change returns illustrates the inherent sensitivity of raw pixel-level subtraction to harmless lighting shifts. This high sensitivity is deliberate for safety (catching all real damage), and directly motivates pairing CV with multimodal Gemma reasoning and mandatory human operator confirmation to dismiss harmless glare.
3. **Architectural Safety Invariant (0 Auto-Charges):** The software has no automatic charging capability. Zero automated charges is an architectural invariant, not a statistical metric.
4. **Automated Quality Suite:** 77 automated tests pass across Python pytest (61 tests, >92% coverage), Vitest (10 tests), and Playwright E2E/Axe accessibility (6 tests, 0 serious/critical violations).

---

## 🔒 Security, Privacy & Integrity Guarantees

1. **Local On-Premises Processing:** Customer photos and serial numbers remain on the local counter workstation.
2. **Automated EXIF Sanitization:** GPS coordinates, camera serial numbers, and device tags are scrubbed before storage.
3. **Tamper-Evident SHA-256 Digest:** Generates a SHA-256 Content Integrity Digest binding raw photo hashes, bounding box coordinates, and operator decisions into a finalized manifest. *(Note: A SHA-256 digest is tamper-evident only when compared with a trusted previously stored digest; it is not a digital signature, timestamp authority, or proof of custody).*
4. **Security Scan:** Bandit scan completed with **0 High, 0 Medium, and 0 Low** vulnerabilities.

![Audit Report Manifest](https://raw.githubusercontent.com/abhijeetnardele24-hash/gearwitness/main/docs/screenshots/audit_report_manifest.png)

---

## ⚠️ Accurate Limitations

- **Extreme Perspective Disparities:** If a return photo is captured at an angle greater than 25° off-axis relative to baseline, feature matching can degrade, requiring the operator to switch to side-by-side mode or recapture using Guided Capture.
- **Specular Glare:** Highly polished optics and curved chrome can trigger localized luminance deltas under differing lighting angles.
- **Runtime Model Status:** Live Gemma 3 inference requires an installed local Ollama runtime (`>=0.6.0`) with `gemma3:4b` pulled. When offline, GearWitness operates in reproducible fixture mode with full operator review functionality.

---

## 🚀 Live Demo & Code Repository

- **GitHub Repository:** [https://github.com/abhijeetnardele24-hash/gearwitness](https://github.com/abhijeetnardele24-hash/gearwitness)
- **Hosted Demo (Render):** [https://gearwitness.onrender.com](https://gearwitness.onrender.com) *(Live public deployment; the free instance may need a short cold-start after inactivity.)*
- **Documentation:** Complete [Architecture](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/ARCHITECTURE.md), [Model Card](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/MODEL_CARD.md), [Evaluation Suite](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/EVALUATION.md), and [Threat Model](https://github.com/abhijeetnardele24-hash/gearwitness/blob/main/docs/PRIVACY_AND_THREAT_MODEL.md).

---

## 🎯 Conclusion

By grounding local multimodal vision with deterministic OpenCV registration and keeping the human operator firmly in control, GearWitness turns equipment rental check-ins into a fast, transparent, and evidence-backed exchange.
