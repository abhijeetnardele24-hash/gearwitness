# Live Gemma 3 Evaluation Evidence Artifact

> **Evaluation Mode:** Local Multimodal (Gemma 3 via Ollama)  
> **Status:** PENDING HOST RUNTIME DEPLOYMENT (Transparently documented per verification rules)  
> **Target Model:** `gemma3:4b`  
> **Configured Min Version:** `OLLAMA_MIN_VERSION: 0.6.0`  
> **Target Endpoint:** `http://localhost:11434/api/generate`  
> **Audit Date:** 2026-10-15  

---

## 1. Runtime Environment Check

An automated probe was performed on the current evaluation host:

```powershell
PS> where.exe ollama
INFO: Could not find files for the given pattern(s).

PS> curl -s http://127.0.0.1:11434/api/version
(No local server listening on port 11434)
```

**Result:** Ollama is not installed or running in this host environment.

---

## 2. Integrity Declaration & Anti-Fabrication Guarantee

In strict compliance with the project guidelines:
1. **Zero Fabrication:** Fixture data, synthetic runs, or hypothetical sample JSON outputs are **never** presented as live model execution logs. No fabricated specimen response is recorded here.
2. **Current System State:** Live Gemma 3 execution remains **PENDING HOST RUNTIME DEPLOYMENT**.
3. **Graceful Host Fallback:** When `APP_MODE=live` is configured without an active Ollama instance, the backend (`backend/app/services/gemma_analyzer.py`):
   - Catches connection failures cleanly without crashing.
   - Sets condition type to `unknown`.
   - Records rationale explicitly as `[DEGRADED - MODEL OFFLINE] Connection to Ollama failed.`.
   - Emits zero hallucinated findings.
4. **Mocked Unit Test Verification:** Offline handling, error degradation, and schema validation are verified via unit tests in `backend/tests/test_gemma_analyzer.py`:
   - `test_gemma_health_local_mode_offline`: PASSED
   - `test_gemma_health_fixture_mode`: PASSED
   - `test_encode_image_base64`: PASSED

---

## 3. Operator Instructions for Live Gemma 3 Activation

When deploying GearWitness to a workstation with GPU or Apple Silicon hardware:

1. **Install Ollama (>= 0.6.0):**
   ```bash
   # Download from https://ollama.ai/
   ollama --version
   ```

2. **Pull Gemma 3 Multimodal Model:**
   ```bash
   ollama pull gemma3:4b
   ```

3. **Launch GearWitness in Live Mode:**
   ```bash
   APP_MODE=live uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
   ```

4. **Verify Live Inference:**
   Check `http://127.0.0.1:8000/api/v1/health`. The response will report:
   ```json
   {
     "status": "healthy",
     "app_mode": "live",
     "ollama_connected": true,
     "model_name": "gemma3:4b",
     "model_available": true
   }
   ```
