# GearWitness Corrective Master Prompt

Copy the complete block below into the engineering agent.

```text
You are taking over an existing repository:

Local path: C:\Users\Abhijeet Nardele\OneDrive\Desktop\devpost project\gearwitness
GitHub: https://github.com/abhijeetnardele24-hash/gearwitness
Current audited commit: d74ff60d4a09c3e974cfbab69d73fb40421ea293

MISSION

Repair and finish GearWitness as a genuinely working, competition-grade Hacktoberfest Week 2 product. Do not trust the previous “100% complete” report. Inspect every relevant implementation, test, artifact, screenshot, claim, and deployed URL yourself. Work autonomously until all attainable requirements pass. Do not repeatedly ask permission for routine coding, commands, dependency installation, testing, commits, pushes, or deployment. Do not answer with a new plan and stop; execute the plan.

Do not modify or delete RelayZero or AmbientOps. Work only inside gearwitness. Preserve useful existing work, but replace weak or incorrect implementation when necessary.

The current release is NO-GO. The following defects were independently confirmed and are mandatory P0 repairs.

P0 — BROKEN PRODUCT CONTRACTS

1. Fix frontend/backend route and method mismatches.
   - frontend/src/api.ts sends proposal decisions to POST /api/v1/inspections/{inspectionId}/proposals/{proposalId}/decision, while the backend exposes PATCH /api/v1/inspections/{inspectionId}/proposals/{proposalId}.
   - The frontend sends checklist changes with POST and expects a complete Inspection; the backend exposes PATCH and returns a single KitItem.
   - The frontend requests /api/v1/reports/{id}/manifest, /html and /pdf; the backend exposes /api/v1/inspections/{id}/manifest, /report.html and /report.pdf.
   - The frontend calls POST /api/v1/inspections/{id}/approve, but no backend approval route exists.
   - Create one canonical typed API contract. Make every client call and server response consistent. Prefer returning the updated complete Inspection after mutations so state cannot drift.
   - Add contract/integration tests that exercise the exact browser API calls, not only isolated backend routes.

2. Fix every broken image and crop.
   - Fixture MediaEvidence stores filesystem paths such as data/fixtures/file.jpg, but the server mounts them at /fixtures/file.jpg.
   - Uploaded and derived media require safe /media/... URLs; never expose raw filesystem paths to the browser.
   - Add a backend public_url field or a single tested media URL mapper. Do not make the frontend guess from storage_path.
   - Evidence crops must be real crop images and must load successfully.
   - Add browser assertions that every visible image has naturalWidth > 0 and that the page contains zero broken image icons.

3. Fix coordinate semantics.
   - OpenCV and seeded fixtures use pixel bounding boxes, while CompareCanvas renders x/y/width/height as percentages. Current values such as x=550 become 550%, placing hotspots outside the image.
   - Choose and document one representation: normalized 0..1 coordinates is preferred for API/UI, while image processing can retain pixels internally.
   - Convert using the source image dimensions exactly once. Test portrait, landscape, resized, and letterboxed images.

4. Make Guided Capture functional.
   - The current “Snap or Upload Photo” button has no click behavior, file input, camera capture, upload request, preview, progress, retry, or completion state.
   - Implement actual mobile-friendly capture/upload using input accept="image/*" and capture="environment" where supported. A getUserMedia enhancement is optional, not required.
   - Connect it to the existing safe upload endpoint, show preview and file-validation feedback, persist the returned media, refresh the inspection, and advance each capture step.
   - The current Permissions-Policy camera=() blocks browser camera APIs. Align the policy with the implemented design while keeping camera access opt-in and same-origin only.

5. Repair report and approval workflow.
   - The committed screenshot shows “Failed to load manifest.” This must never appear in final evidence.
   - Implement approval only when all proposals are resolved and checklist items have explicit return states. Enforce this on the server, not only in the UI.
   - Show actionable errors, retry, and focus management. Do not leave console-only failures.
   - Verify JSON, HTML, and PDF exports from the browser and validate downloaded content.

6. Add persistence.
   - backend/app/models/database.py claims SQLite but is an in-memory dictionary seeded on every process start.
   - Implement real SQLite persistence with migrations or a small explicit schema layer. Assets, inspections, media, proposals, decisions, checklist state, and report status must survive a restart.
   - Make fixture seeding idempotent and limited to fixture mode.

P0 — MODEL AND EVALUATION INTEGRITY

7. Correct the model.
   - The configuration defaults to gemma2:9b, which is not the claimed Gemma 3 multimodal vision model.
   - Use an actual Ollama multimodal Gemma 3 variant, preferably gemma3:4b for accessible local hardware, and document the minimum supported Ollama version.
   - Verify the actual request shape against the current Ollama API. Add a mock-server integration test that confirms two images and strict JSON output are sent correctly.
   - Local mode must not silently convert a failed model request into a successful fixture proposal. Return an explicit degraded/unavailable state, show it in the UI, and require an operator choice to use deterministic CV-only analysis.
   - Never claim live Gemma execution or latency without a saved raw request/response artifact, model digest/version, hardware details, and timestamp.

8. Rebuild the evaluation honestly.
   - benchmark_inputs.jsonl currently contains a category field such as no_change, scratch_scuff, or missing_accessory. That is a target label and violates the claim that inputs contain zero gold labels.
   - evaluation_runner.py uses item["category"] directly to generate the deterministic baseline. This is target leakage, not model evaluation.
   - Remove category and every target-derived feature from prediction inputs. Load category only from gold during scoring.
   - Strengthen the leakage guard to reject category, target class, expected view/result, filenames encoding labels, and any other predictive shortcut.
   - Ensure file ordering and case IDs do not encode labels usable by predictors.
   - Run the real CV pipeline on pixels for all predictions. Fixture classification based only on view and crop index is not a meaningful model benchmark.
   - Keep synthetic data clearly labeled synthetic. Do not call it “physical,” “expert-annotated,” or a real user evaluation.
   - Add external/self-shot real examples only if provenance and consent are available; otherwise state the limitation clearly.

9. Correct every metric and claim.
   - Committed data/evaluation_metrics.json reports the hybrid system at precision 0.649, recall 1.0, F1 0.787, and no-change false-positive rate 0.7.
   - docs/EVALUATION.md, README.md, the DEV draft, and the handoff instead claim overall 0.900, pristine accuracy 100%, and a much lower false-positive rate. These documents contradict the evidence.
   - After repairing the benchmark, generate documentation tables directly from the metrics artifact. Add a CI drift test that fails when documented metrics differ from the JSON source of truth.
   - Remove unverified 0.8–1.4 second GPU latency, “15–20 minutes to 60 seconds,” “sub-millimeter precision,” legal/insurance usefulness, and other unsupported claims unless measured with a reproducible artifact.

10. Use accurate integrity language.
    - A SHA-256 digest alone is not a cryptographic signature and is not independently tamper-proof when an attacker can alter both content and digest.
    - Rename current functionality to “content integrity digest” and explain its exact limitation.
    - If implementing optional Ed25519 signing, keep private keys out of Git, expose the public key and verification procedure, test valid/invalid signatures, and clearly distinguish signed from unsigned manifests.
    - Never use “cryptographically verified,” “immutable,” “signed,” or “legally grounded” unless the implementation and threat model support the exact wording.

P0 — CI, DEPLOYMENT, AND TEST COVERAGE

11. Fix remote CI.
    - GitHub Actions run 38628367468 is red: on Linux, SPA tests fail because frontend/dist does not exist in the backend job. The root returns JSON and a client-side route returns 404.
    - Make CI deterministic from a clean clone. Either build the frontend before SPA tests or separate SPA packaging tests into a job with a built frontend artifact.
    - Use frontend/package-lock.json as the setup-node cache dependency path.
    - CI is not green until the remote GitHub run passes, not merely local Windows tests.

12. Add the missing frontend and browser test stack.
    - frontend/package.json currently has no Vitest, Testing Library, Playwright, or axe dependencies/scripts.
    - Add component tests for loading, error, mode status, proposal decisions, checklist updates, report retry, capture upload, and accessible modal behavior.
    - Add Playwright tests that start the production-like app and exercise the complete fixture journey.
    - Add axe checks with zero serious or critical violations and no blanket rule disabling.
    - Fail tests on console errors, page errors, failed API responses, broken images, or unexpected 4xx/5xx responses.

13. Verify deployment instead of naming a target URL.
    - render.yaml existing in Git does not prove deployment.
    - Verify https://gearwitness.onrender.com from a clean browser. Record timestamp, commit SHA, /api/v1/health response, app mode, and a successful hero flow.
    - If deployment does not exist, create/fix it if authenticated. If authentication is the only blocker, complete all code and provide exactly one external action.
    - Do not call the URL live until it returns the application successfully.

P1 — PREMIUM PRODUCT AND UI REBUILD

Before editing UI code, write docs/UI_REDESIGN_SPEC.md containing a concise design plan: user jobs, information hierarchy, layout at each breakpoint, design tokens, typography, interaction states, accessibility behavior, and screenshot acceptance criteria. Then implement it; do not stop after writing the plan.

Design goal: a distinctive professional evidence workstation called “Forensic Calm.” It should feel closer to premium camera-production software or a modern inspection tool than a generic SaaS/admin dashboard.

Preserve the useful warm-stone, charcoal, teal, and amber direction, but rebuild the hierarchy and interactions:

- Use a compact command header with product identity, explicit FIXTURE/LOCAL/CV-ONLY mode, model health, privacy state, and one primary action.
- Use a clear inspection navigator that works for one or many returns without a crowded pill bar.
- Make the before/after canvas the dominant visual surface. Render the real images at a correct aspect ratio; never show an unexplained black void.
- Support reveal, side-by-side, heatmap, fit, 100%, zoom/pan, and reset. Controls must have tooltips and keyboard equivalents.
- Keep hotspots correctly attached to the image under zoom, resize, and letterboxing.
- Use a focused evidence review rail on desktop and an accessible bottom sheet/drawer on mobile.
- Each evidence card must show exact before/after crops, source view, severity, confidence with meaning, observable rationale, operator note, and three unmistakable decisions.
- Make Confirm, Dismiss, and Uncertain semantically distinct without relying on color alone.
- Show workflow progress as Capture → Align → Review → Export with actual backend-derived state.
- Turn capture into a guided stepper with preview, retake/replace, upload progress, validation, and completion indicators.
- Make the final report experience visually credible and printable.

Design-system rules:

- Replace emoji UI icons with Lucide icons already installed. Use icons consistently through shared components.
- Create reusable Button, IconButton, Badge, SegmentedControl, Dialog/Drawer, Toast, EmptyState, Skeleton, and Status components instead of page-local variants.
- Use semantic tokens for color, spacing, radius, elevation, typography, and motion.
- Use Plus Jakarta Sans or another intentional humanist sans, with JetBrains Mono only for hashes/technical identifiers.
- Keep motion subtle: 120–220 ms, opacity/transform only, and respect prefers-reduced-motion.
- No purple gradients, glass-card wallpaper, neon glow, giant marketing typography inside the workbench, excessive shadows, fake charts, emoji navigation, or generic “AI assistant” chat UI.
- Do not hide application failures behind polished visuals.

Responsive requirements:

- 320 and 360 px: one-column capture/review, sticky bottom primary action, evidence drawer, readable cards, no squeezed multi-button rows.
- 768 px: canvas first, evidence below or in an accessible drawer.
- 1024 px and above: canvas/evidence split with stable image area.
- 1440 and 1920 px: controlled max widths and useful density, not stretched whitespace.
- Verify landscape mobile and 200% browser zoom.
- No horizontal document overflow. Internal intentional scrollers require labels and keyboard access.

Accessibility requirements:

- WCAG 2.1 AA contrast.
- Dialog focus trap, Escape close, focus restoration, labelled titles/descriptions, and background inertness.
- Keyboard-operable slider, zoom, tabs, evidence selection, and decision controls.
- Live announcements for upload, analysis, errors, and decisions.
- Minimum 44×44 px touch targets on mobile.
- Never show error feedback only through alert() or console.error(). Use accessible inline alerts/toasts with recovery actions.

P1 — END-TO-END ACCEPTANCE SCENARIO

The final Playwright hero test and demo must perform this exact flow from a clean fixture-mode start:

1. Open GearWitness with zero console/page errors.
2. Verify mode and model labels are truthful.
3. Create or select the fixture inspection.
4. Open Guided Capture.
5. Upload a checkout image and return image through the real browser controls.
6. Confirm both images render with naturalWidth > 0.
7. Run analysis and observe a real loading/progress state.
8. Display correctly placed hotspots and working before/after crops.
9. Dismiss the lighting artifact, confirm the scratch, and confirm/mark the missing accessory.
10. Toggle a checklist item and verify persistence after reload.
11. Block approval while any proposal is pending.
12. Complete review, approve, and display a successfully loaded manifest.
13. Download and validate JSON and PDF; open the HTML report.
14. Restart the backend and verify the inspection and decisions persist.
15. Capture clean screenshots at 360, 768, 1440, and 1920 widths.

QUALITY GATES

- Ruff passes.
- Type checking passes.
- Bandit has no unresolved high/medium findings.
- Backend tests pass with >=85% core coverage.
- Frontend lint, TypeScript, component tests, and production build pass.
- Playwright complete workflow passes on Chromium.
- Axe reports zero serious/critical violations.
- Docker build and container health test pass.
- CI passes remotely on GitHub.
- Render app and health endpoint are verified.
- Git working tree is clean and origin/main contains the final commit.

DOCUMENTATION AND SUBMISSION ARTIFACT REPAIR

- Delete or replace every screenshot containing broken images, broken crops, “Failed to load manifest,” overflow, or other errors.
- Produce a truthful screenshot set at multiple breakpoints plus the working capture, evidence review, unavailable-model, and report states.
- Update README, ARCHITECTURE, MODEL_CARD, EVALUATION, PRIVACY_AND_THREAT_MODEL, DEMO_SCRIPT, DEV_SUBMISSION, and SUBMISSION_CHECKLIST from verified behavior only.
- DEV front matter must use no more than four tags and must include hf26challenge. The current five-tag string is invalid for this requirement.
- Describe fixture mode prominently. Never imply synthetic fixture output is live Gemma output.
- Keep AI disclosure honest.
- Do not publish the DEV article or submit the challenge entry.

WORKING METHOD

- Begin by reproducing every confirmed issue.
- Create a requirement-to-test matrix in docs/CORRECTIVE_AUDIT.md.
- Repair P0 correctness before visual polish.
- Use the sequence reuse → extend → create → validate for frontend components.
- Make small, meaningful commits. Do not force-push.
- Run secret scanning before pushing.
- After each major phase, run the relevant tests; at the end, run everything from a clean clone/build state.
- Do not report percentages or GO status until the evidence supports them.

FINAL RESPONSE FORMAT

Return only an evidence-backed handoff containing:

1. Final repository URL, branch, and commit SHA.
2. Remote GitHub Actions run URL and green status.
3. Verified Render URL and health response.
4. Exact commands and pass/fail counts for backend, frontend, E2E, accessibility, security, Docker, and evaluation.
5. Correct final evaluation metrics copied from the generated artifact.
6. Proof that benchmark inputs contain no target labels and predictions do not read gold/category.
7. Proof of real Gemma 3 multimodal request support, or an explicit unverified blocker with no live claims.
8. Paths to new screenshots and the DEV article draft.
9. A table closing every P0/P1 item with file/test evidence.
10. Remaining user-only actions.
11. Final GO/NO-GO verdict.

Do not respond with “ready to proceed.” Start repairing the repository immediately and continue until it is genuinely release-ready or one narrowly defined external blocker remains.
```
