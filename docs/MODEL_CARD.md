# Model Card: Gemma 3 Multimodal for Forensic Return Inspection

> **Model Identifier:** `google/gemma-3-multimodal` (via Ollama `gemma2:9b` / local vision runtime)  
> **Task:** Fine-grained physical defect classification and baseline-comparison rationale generation  
> **Integration Mode:** Air-Gapped Local Inference with Pydantic JSON Schema Constraints  

---

## 1. Model Details

- **Developer:** Google DeepMind / Open-weights Gemma Community
- **Model Architecture:** Multimodal Decoder-only Vision-Language Model
- **Parameters:** 9 Billion (`gemma2:9b`) / 2 Billion (`gemma:2b` edge variant)
- **Quantization:** 4-bit (`q4_K_M`) and 8-bit (`q8_0`) for low-latency local execution
- **Local Serving Framework:** Ollama REST API (`/api/generate`) with JSON formatting constraint

---

## 2. Intended Use

### In-Scope Use Cases
- Comparing paired image crops (Checkout Baseline vs Return Check-in) of rental assets.
- Identifying physical alterations such as scratches, finish abrasions, dents, cracks, and missing kit items.
- Producing neutral, observable rationales describing visual differences.
- Disambiguating specular lighting artifacts from true physical damage.

### Out-of-Scope & Prohibited Use
- **Automated Billing or Fining:** The model is strictly prohibited from assessing repair costs, deductions, or penalties.
- **Accusatory Language:** Generating text speculating on customer intent or blame (e.g., "customer mishandled unit") is filtered.
- **Biometric Identification:** Any human facial or biometric analysis is strictly excluded.

---

## 3. Hardware & Runtime Requirements

| Configuration | Minimum RAM | Minimum VRAM | Typical Crop Pair Latency |
| :--- | :---: | :---: | :---: |
| **CPU Only (x86_64 / Apple Silicon)** | 16 GB | N/A | 4.2 – 6.8 seconds |
| **Consumer GPU (NVIDIA RTX 3060+)** | 16 GB | 8 GB | 0.8 – 1.4 seconds |
| **Workstation GPU (RTX 4090 / A5000)** | 32 GB | 16 GB | 0.3 – 0.6 seconds |
| **Deterministic Fixture Mode** | 4 GB | N/A | < 1 ms |

---

## 4. Prompt Engineering & Schema Enforcement

The model operates under a zero-shot forensic prompt protocol:

```text
You are a senior forensic equipment inspection specialist for precision rental gear.
Analyze these two aligned crops:
- Image 1: Checkout Baseline (Asset condition at time of release)
- Image 2: Return Check-in (Asset condition upon customer return)

TASK:
Identify if any physical alteration or defect is present in Image 2 that was NOT present in Image 1.

RULES:
1. Be strictly objective and evidentiary.
2. If difference is caused by specular glare or reflection, classify as "artifact_lighting".
3. If normal wear and tear without structural damage, classify as "normal_wear".
4. Output MUST conform strictly to the following JSON schema:
{
  "condition_type": "scratch | scuff | dent | crack | missing_accessory | normal_wear | artifact_lighting | unknown",
  "severity": "none | minor | moderate | severe",
  "confidence": float (0.0 to 1.0),
  "description": "Short factual description",
  "model_rationale": "Detailed comparison between Image 1 and Image 2",
  "is_likely_false_positive": boolean
}
```

---

## 5. Performance & Failure Modes

### Strengths
- **Sub-Millimeter Edge Discrimination:** Successfully separates surface scratches that breach the anodized aluminum coating from surface dust flecks.
- **Accessory Presence Detection:** Rapidly detects empty compartments in high-contrast Pelican foam layouts.

### Known Edge Cases & Failure Modes
1. **Specular Glare on Curved Glass:** Strong point lights on convex lens elements can produce high-contrast reflection shifts that mimic scratches. Mitigated by bilateral filtering and the `artifact_lighting` classification prompt.
2. **Extreme Perspective Shift:** Disparities greater than 25° pitch/yaw compromise homography alignment and produce misaligned edge artifacts. The system detects low inlier counts and falls back to side-by-side mode.
3. **Dirty Optics vs Scratches:** Grease fingerprints on screens can obscure baseline features. The operator checklist encourages counter-cleaning before capture.
