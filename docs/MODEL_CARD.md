# Model Card: Gemma 3 Multimodal for Forensic Return Inspection

> **Configured Ollama Model:** `gemma3:4b`  
> **Minimum Serving Runtime:** Ollama `>=0.6.0`  
> **Task:** Fine-grained physical defect classification and baseline-comparison rationale generation  
> **Integration Mode:** Air-Gapped Local Inference with Pydantic JSON Schema Constraints  
> **Runtime Status:** **Live Execution Pending Host Runtime Deployment** (Deterministic Fixture Fallback Verified)  

---

## 1. Model Details

- **Developer:** Google DeepMind / Open-weights Gemma Community
- **Model Architecture:** Multimodal Vision-Language Model (`gemma3:4b`)
- **Configured Target:** `gemma3:4b` via local Ollama REST API (`/api/generate`) with structured JSON format enforcement.
- **Serving Protocol:** Local HTTP endpoint (`http://localhost:11434`) running strictly on-premises; zero cloud telemetry or external API calls.
- **Current Deployment Status:** In this test environment, local execution remains marked as pending host runtime availability because Ollama is not installed on the build machine. The application executes using deterministic fixture mode, which provides reproducible, grounded proposals for developer workflows and testing.

---

## 2. Intended Use

### In-Scope Use Cases
- Comparing paired image crops (Checkout Baseline vs Return Check-in) of rental assets.
- Identifying physical alterations such as scratches, finish abrasions, dents, cracks, and missing kit items.
- Producing neutral, observable rationales describing visual differences.
- Disambiguating specular lighting artifacts from true physical damage.

### Out-of-Scope & Prohibited Use
- **Automated Billing or Fining:** The software has no automatic charging capability. All damage claims remain proposals subject to human operator adjudication.
- **Accusatory Language:** Generating text speculating on customer intent or blame (e.g., "customer mishandled unit") is prohibited by prompt instructions.
- **Biometric Identification:** Any human facial or biometric analysis is strictly excluded.

---

## 3. Runtime Separation: Fixture Mode vs. Live Mode

GearWitness strictly separates deterministic fixture execution from live model inference:

| Dimension | Fixture Mode (`APP_MODE=fixture`) | Live Local Mode (`APP_MODE=local`) |
| :--- | :--- | :--- |
| **Execution Engine** | Deterministic rule-based proposal generator | Local Ollama instance serving `gemma3:4b` |
| **Model Invocation** | No neural network invoked | Multimodal image-pair prompt via `/api/generate` |
| **Network Requirements** | None (100% offline, reproducible) | Localhost only (`http://localhost:11434`) |
| **Health Probe** | Reports deterministic fixture mode (`ollama_connected: false`, `model_available: false`, `target_model: gemma3:4b`) | Queries `/api/tags` to assert Ollama connectivity and model presence |
| **Degraded State** | N/A | If Ollama is offline or model absent, transitions explicitly to degraded fallback with zero fabricated confidence |
| **Benchmark Attribution** | Explicitly labeled as *GearWitness Fixture Pipeline* | Labeled as *CV + Live Gemma 3* only when live execution succeeds |

---

## 4. Prompt Engineering & Schema Enforcement

The model operates under a zero-shot forensic prompt protocol with strict schema compliance:

```text
You are a forensic equipment return inspection specialist examining a '{asset_name}' ({view} view).
Image 1 is the baseline checkout photo. Image 2 is the return check-in photo of the exact same localized area.
Classify whether a physical change occurred. You must respond ONLY with a valid JSON object matching this schema:
{
  "condition_type": "scratch"|"scuff"|"dent"|"crack"|"missing_accessory"|"normal_wear"|"artifact_lighting",
  "severity": "none"|"minor"|"moderate"|"severe",
  "confidence": 0.0 to 1.0,
  "description": "objective factual observation (1-2 sentences)",
  "model_rationale": "specific visual difference between checkout and checkin crops"
}
Do NOT accuse anyone of fraud or deliberate damage. Stick strictly to physical visual evidence.
```

---

## 5. Architectural Invariants & Limitations

1. **Strict Human Decision Boundary:** The model cannot create financial charges or approve manifests. Operators must explicitly click `Confirm`, `Dismiss`, or `Uncertain` for every proposal before a return manifest can be finalized.
2. **Homography Dependency:** The vision pipeline depends on OpenCV ORB feature alignment. Extreme perspective shifts or severe optical occlusions fall back to side-by-side operator inspection.
3. **Lighting Shifts:** Specular glare on curved optics can produce high luminance deltas. Prompting specifically routes these to `artifact_lighting` for operator dismissal.
