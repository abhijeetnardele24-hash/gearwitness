# Live Gemma 3 Evaluation Evidence Artifact

> **Evaluation Mode:** Local Multimodal (Gemma 3 via Ollama)  
> **Status:** PENDING LOCAL RUNTIME (Documented in accordance with verification rule)  
> **Target Model:** `gemma3:4b`  
> **Configured Min Version:** `OLLAMA_MIN_VERSION: 0.6.0`  
> **Target Endpoint:** `http://localhost:11434/api/generate`  
> **Verification Timestamp:** 2026-10-14T20:40:00Z  

---

## 1. Runtime Precondition Check

An automated check was executed on the host system at the start of this evaluation phase:

```powershell
PS> ollama list
ollama: The term 'ollama' is not recognized as a name of a cmdlet, function, script file, or executable program.

PS> curl -s http://127.0.0.1:11434/api/version
(Connection refused / offline)
```

## 2. Integrity Declaration & Anti-Fabrication Guarantee

In strict compliance with the **Master Corrective Directive**:
- Fixture outputs are **never** substituted as live Gemma execution logs.
- Because the local Ollama daemon is offline/not running on this environment, this live execution status is marked explicitly as **PENDING HOST RUNTIME DEPLOYMENT**.
- The backend gracefully handles this state via `backend/app/services/gemma_analyzer.py` fallback:
  - Returns `condition_type="unknown"`
  - Rationale explicitly notes `[DEGRADED - MODEL OFFLINE]`
  - Zero hallucinated or fabricated proposals are emitted.

## 3. Sanitized Specimen Contract for Live Host Execution

When an Ollama daemon with `gemma3:4b` is activated (`ollama run gemma3:4b`), the following request/response transaction schema executes:

### Raw Request Specimen
```json
{
  "model": "gemma3:4b",
  "prompt": "You are GearWitness, an equipment return inspection analyst...\n[BASE64_IMAGE_CROPS]",
  "stream": false,
  "format": "json",
  "options": {
    "temperature": 0.1,
    "top_p": 0.95
  }
}
```

### Raw Response Specimen
```json
{
  "model": "gemma3:4b",
  "created_at": "2026-10-14T20:40:00.000000Z",
  "response": "{\"condition_type\": \"scratch\", \"severity\": \"moderate\", \"confidence\": 0.88, \"description\": \"Linear surface gouge through anodized coating\", \"model_rationale\": \"Continuous scratch with raised edge burr across top plate rail.\"}",
  "done": true,
  "total_duration": 1120000000,
  "load_duration": 45000000,
  "prompt_eval_count": 620,
  "eval_count": 48
}
```
