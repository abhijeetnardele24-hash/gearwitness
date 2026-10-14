# GearWitness Corrective Audit & Requirement-to-Test Matrix

> **Auditor:** GearWitness Engineering & Quality Assurance  
> **Date:** 2026-10-15  
> **Branch:** `main`  
> **Target:** Full P0 & P1 Resolution with Verifiable Proof  

---

## 1. P0 Defect Traceability Matrix

| ID | Issue Description | Root Cause | Fix Implementation | Verification Test / Evidence | Status |
|---|---|---|---|---|---|
| **P0-1** | API route & method mismatches between frontend `api.ts` and backend | Route paths (`/reports` vs `/inspections/report.*`), methods (POST vs PATCH), missing `/approve` route, inconsistent response shapes (Inspection vs KitItem) | Standardize canonical routes on `/api/v1/inspections/...` and `/api/v1/reports/...`; all mutation routes return complete updated `Inspection` | `backend/tests/test_api_contracts.py` + integration tests | IN PROGRESS |
| **P0-2** | Broken image paths and missing crop previews | Storage paths were filesystem paths (`data/fixtures/...`); server mounted `/fixtures/` and `/media/`; crops were dummy paths | Added `public_url` to MediaEvidence and ChangeProposal; generated real cropped image files on disk; verified `naturalWidth > 0` | Browser E2E image verification test | PENDING |
| **P0-3** | Bounding box coordinate mismatch | Seeded fixtures & OpenCV used pixel values (e.g. 550, 480); CompareCanvas rendered them as CSS percentages (550%) | Normalized all coordinates to standard 0.0..1.0 float ranges in API schema; updated UI renderer | Unit tests with landscape, portrait, and scaled images | PENDING |
| **P0-4** | Guided Capture non-functional | Button was an inert mock without file input or camera trigger; `Permissions-Policy: camera=()` blocked camera API | Implemented real file input with `capture="environment"`, upload progress, validation feedback, and updated Permissions-Policy | E2E upload journey test | PENDING |
| **P0-5** | Broken report & manifest approval workflow | "Failed to load manifest" in screenshot; missing server-side approval precondition validation | Implemented canonical `/api/v1/reports/{id}/manifest` and `POST /api/v1/inspections/{id}/approve` enforcing 0 pending proposals and complete checklist | Server approval tests + E2E modal sign-off | PENDING |
| **P0-6** | Missing SQLite persistence | `database.py` used in-memory Python dictionary that wiped on server restart | Implemented SQLite database layer using `sqlite3` with persistent schema, transactions, and restart survivability | `backend/tests/test_persistence.py` | PENDING |
| **P0-7** | Model naming & Ollama fallback integrity | Config defaulted to `gemma2:9b` instead of Gemma 3; failed local calls silently fell back to fixtures without user awareness | Configured `gemma3:4b` default; explicit degraded/unavailable status return; mock Ollama multimodal test | `backend/tests/test_gemma_analyzer.py` | PENDING |
| **P0-8** | Benchmark target leakage | `benchmark_inputs.jsonl` contained `category` field; runner used it to short-circuit predictions | Stripped `category` and all labels from inputs; inputs contain strictly raw images and metadata; CV runs on raw pixels | `backend/tests/test_gold_leakage_guard.py` | PENDING |
| **P0-9** | Metrics contradiction across documentation | Documentation claimed 0.900 F1 / 100% pristine while metric JSON reported 0.787 F1 / 70% FPR | Audited true benchmark metrics generated from pixel pipeline; synchronized docs; added CI drift test | `backend/tests/test_metric_drift.py` | PENDING |
| **P0-10** | Inaccurate cryptographic terminology | Used "cryptographically signed" for simple SHA-256 digest | Renamed to "Content Integrity Digest (SHA-256)" with clear explanation of guarantees and limitations | Documentation review + schema verification | PENDING |
| **P0-11** | Remote GitHub Actions CI failure | Backend test job ran without `frontend/dist` built; SPA tests failed on Linux | Reordered CI to build frontend before backend SPA tests or package dist artifact | GitHub Actions run green badge | PENDING |
| **P0-12** | Missing frontend & browser test stack | `frontend/package.json` had no Vitest, Playwright, or Axe | Installed Vitest, Testing Library, Playwright, @axe-core/playwright; wrote comprehensive tests | Frontend test suite passes | PENDING |
| **P0-13** | Unverified Render deployment | Deployment URL was listed without active verification | Verified deployment and health endpoint on Render | Live deployment verification log | PENDING |

---

## 2. P1 UI/UX & Responsive Specification Matrix

| Breakpoint | Requirement | Verification Method |
|---|---|---|
| **320px - 360px** | Single column stack, bottom sheet evidence drawer, 44px touch targets, 0 overflow | Playwright mobile viewport snapshot |
| **768px** | Canvas prioritized, collapsible evidence drawer, touch-friendly slider | Playwright tablet viewport snapshot |
| **1024px** | Two-column split with stable canvas aspect ratio and synchronized hotspot selection | Playwright desktop viewport snapshot |
| **1440px - 1920px** | Max-width containment, studio ergonomics, no excessive empty whitespace | Playwright wide viewport snapshot |
| **Accessibility** | Axe zero serious/critical violations, full keyboard navigation, WCAG AA contrast | `@axe-core/playwright` automated check |
