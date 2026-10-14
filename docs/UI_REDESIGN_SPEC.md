# GearWitness UI Redesign Specification — "Forensic Calm"

> **Design Paradigm:** Forensic Calm  
> **Target Audience:** Equipment rental operations managers, checkout technicians, forensic inspection operators.  
> **Core Aesthetic:** Camera-production engineering workstation (Arri/Sony Cine/RED utility software influence). Warm slate, deep charcoal, signal amber, verification teal, subdued neutral surfaces.  
> **Zero Tolerance:** No purple gradients, neon glows, emoji UI icons, decorative marketing fluff, fake charts, or glassmorphism wallpaper.

---

## 1. User Jobs & Core Workflows

1. **Intake & Verification:** Confirm equipment kit identity, checkout timestamp, customer reference, and return custody state.
2. **Visual Forensic Comparison:** Interrogate matched-pair photographs (checkout vs checkin) across capture views (front, back, top, accessories, detail) using Reveal Slider, Side-by-Side, Difference Heatmap, and synchronized pan/zoom.
3. **Change Proposal Review:** Inspect localized crops, assess severity/confidence/rationale, attach operator notes, and make explicit tripartite decisions:
   - **Confirm Damage:** Acknowledge new damage attributable to current rental.
   - **Dismiss (Artifact):** Reject benign artifacts (specular reflections, dust, baseline wear).
   - **Uncertain (Escalate):** Route to supervisor / depot lead for physical bench test.
4. **Kit Accessory Reconciliation:** Verify presence of physical cables, chargers, caps, and batteries against checkout checklist.
5. **Sealed Manifest & Export:** Once 100% of proposals and checklist items are verified, generate SHA-256 sealed forensic return manifest with PDF/HTML download.

---

## 2. Information Architecture & Layout Strategy

### Desktop Breakpoint ($\ge 1024\text{px}$)
- **Top Command Bar (56px):** Brand identifier, Active Inspection Selector, App Mode Badge (`FIXTURE` / `LOCAL` / `CV-ONLY`), System Health, Privacy Indicator (`Local Air-Gapped`), and primary workflow action.
- **Workflow Stepper (40px):** Capture (4/4) → Align (OK) → Review (3 proposals) → Export (Sealed).
- **Split Workstation Body:**
  - **Main Canvas Area (65% width):** High-precision comparison viewport, tool toolbar (Reveal, Split, Heatmap, 100%, Fit, Zoom In/Out, Reset), normalized coordinate bounding box overlays.
  - **Evidence Rail (35% width):** Proposal cards, side-by-side thumbnail crops, severity pills, model rationale, decision actions, and kit checklist drawer.

### Mobile & Tablet Breakpoints ($320\text{px} - 768\text{px}$)
- **Compact Header:** GearWitness mark, Mode tag, Menu/Switch inspection sheet.
- **Single-Column Vertical Flow:** Canvas viewport pinned with responsive aspect-ratio container.
- **Bottom Drawer / Sheet:** Swipable / scrollable evidence cards with 44px minimum tap targets.
- **Sticky Bottom Action Bar:** Primary stepper progression / Approve button.

---

## 3. Design Tokens & Typography

### Typography
- **Primary Body & UI:** `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, sans-serif.
- **Technical & Hash Data:** `JetBrains Mono`, `Consolas`, monospace (used for SHA-256 hashes, serial numbers, coordinates).

### Color Tokens
- `--bg-canvas`: `#0d1117` (Deep neutral studio dark)
- `--bg-surface`: `#161b22` (Card and panel background)
- `--bg-surface-elevated`: `#21262d` (Hover states, dialog surfaces)
- `--border-subtle`: `#30363d` (Delicate structural seams)
- `--border-strong`: `#484f58` (Active tabs, focus rings)
- `--text-primary`: `#f0f6fc` (High-contrast content)
- `--text-secondary`: `#8b949e` (Labels, metadata, captions)
- `--text-muted`: `#6e7681` (Placeholder, disabled states)
- `--accent-teal`: `#2dd4bf` (Verified states, approved badges, pristine)
- `--accent-amber`: `#f59e0b` (Damage proposals, operator warnings, review ready)
- `--accent-red`: `#ef4444` (Severe damage, missing accessories)
- `--accent-blue`: `#38bdf8` (Active inspection selection, focus bounds)

### Motion & Transitions
- Micro-transitions: `150ms cubic-bezier(0.16, 1, 0.3, 1)` for button hovers, tabs, and toggles.
- Modal / Drawer transitions: `200ms ease-out`.
- Full respect for `prefers-reduced-motion: reduce`.

---

## 4. Component Library Architecture

1. **`CommandHeader.tsx`:** Clean dark navigation bar with real health status and mode indicator.
2. **`WorkflowStepper.tsx`:** Visual representation of pipeline lifecycle.
3. **`CompareCanvas.tsx`:** SVG/Canvas overlay over responsive image viewport. Real normalized coordinates $(x, y, w, h \in [0..1])$ correctly mapped to bounding box rectangles without percentage blowups.
4. **`EvidenceTray.tsx`:** Proposal cards with real crop URLs, decision buttons (`Confirm`, `Dismiss`, `Uncertain`), and Kit checklist toggles.
5. **`GuidedCaptureModal.tsx`:** Modal with real HTML5 `<input type="file" accept="image/*" capture="environment">`, upload progress, validation, and camera view advancement.
6. **`ReportModal.tsx`:** Forensic manifest viewer, approval gate, and PDF/HTML print/download triggers.
7. **Design System Primitives:** Reusable `Button`, `Badge`, `IconButton`, `Skeleton` using Lucide icons.

---

## 5. Verification & Acceptance Criteria

- [x] Zero emoji icons in UI (all replaced with Lucide React icons).
- [x] Natural image aspect ratio preservation with zero broken image icons (`naturalWidth > 0`).
- [x] Coordinates rendered strictly using normalized $[0.0..1.0]$ floats mapped directly to display dimensions.
- [x] Guided capture modal provides actual file upload to `/api/v1/inspections/{id}/media`.
- [x] Passing Axe Core accessibility scan with zero serious or critical violations.
- [x] Responsive layout tested and verified at 320px, 768px, and 1280px.
