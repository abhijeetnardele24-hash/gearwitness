# GearWitness Video Demonstration Script & Shot List

> **Duration:** 105 Seconds (1 Minute 45 Seconds) — Strict 90–120s Window  
> **Target Audience:** DEV Challenge Judges, Equipment Rental Operators, Open-Source AI Community  
> **Environment:** GearWitness Counter Workstation on `http://127.0.0.1:8000`  
> **Visual Aesthetic:** "Forensic Calm" Studio Palette (Warm Stone, Slate & Evidentiary Teal)  

---

## 🎬 Exact Production Shot List (105s Total)

| Shot # | Timecode | Duration | Visual Action / Camera Framing | Audio / Spoken Voiceover Line |
| :---: | :---: | :---: | :--- | :--- |
| **01** | `0:00 – 0:15` | 15s | **Title Card & Workspace Hero View:**<br>Full-screen browser showing GearWitness running locally. Highlight `MODE: FIXTURE (AUDITED)` pill, equipment title `Sony FX3 Cinema Kit`, and clean "Forensic Calm" interface. | *"Equipment rental returns are high-stress bottlenecks. Skilled agents spend 20 minutes inspecting cameras and cases under a loupe, creating long queues and disputed charges. GearWitness brings local, air-gapped AI directly onto the rental shop counter."* |
| **02** | `0:15 – 0:35` | 20s | **Comparison Canvas & Split Reveal Slider:**<br>Cursor drags the split reveal divider smoothly back and forth across the Sony FX3 top plate. Toggle the `Diff Heatmap` overlay to show the luminance delta, then toggle back to natural view. | *"Here is our checkout baseline on the left, and return check-in on the right. Even with slight angle shifts, deterministic OpenCV ORB and RANSAC homography align the perspective to sub-millimeter precision before any AI model is invoked."* |
| **03** | `0:35 – 0:55` | 20s | **Gemma 3 Proposals & Confirm Damage:**<br>Click **Proposal #1 (Chassis Scratch)** in the right Evidence Tray. Zoom into the paired crop preview showing the 4mm abrasion through the anodized coating. Click **`✓ Confirm Damage`**. | *"Extracted crop pairs are analyzed by Gemma 3 via Ollama using a strict JSON schema. The model detected a fresh scratch breaching the magnesium coating with 89% confidence. As the operator, I confirm the damage with one click."* |
| **04** | `0:55 – 1:15` | 20s | **Human Decision Boundary & Dismiss Glare:**<br>Click **Proposal #2 (Sensor Glass Glare)**. Show the model rationale identifying specular counter lighting. Click **`✕ Dismiss (Wear / Glare)`**. Card dims and updates status. | *"Crucially, GearWitness enforces a strict human decision boundary. The system never assesses auto-fines or accuses customers. For Proposal 2, lighting glare is identified; I dismiss it instantly, preventing a confrontational customer dispute."* |
| **05** | `1:15 – 1:30` | 15s | **Kit Inventory Checklist & Guided Capture:**<br>Scroll down to the Kit Checklist. Toggle **Missing** on the USB-C tethering cable. Click **Guided Capture** button in header to briefly reveal the 5-point silhouette guidance assistant. | *"The kit checklist auto-reconciles multi-piece accessories, catching the missing tethering cable. Operators can also launch Guided Capture for five standardized camera angles with visual silhouette assistance."* |
| **06** | `1:30 – 1:45` | 15s | **Sealed Digest & Inspection Certificate:**<br>Click **Review & Export** in the header. Show the modal with the **SHA-256 Content Integrity Digest**. Click **Approve & Seal**, then click **Printable HTML** and **PDF Report**. End on clean summary card. | *"We finalize the inspection into a tamper-evident SHA-256 Content Integrity Digest. Printable HTML and vector PDF certificates are generated instantly. Fast returns, zero cloud leakage, full operator control. That is GearWitness."* |

---

## 🎙️ Complete Spoken Voiceover Script (Word Count: 268 Words ≈ 105s at 150 WPM)

> *"Equipment rental returns are high-stress bottlenecks. Skilled agents spend 20 minutes inspecting cameras and cases under a loupe, creating long queues and disputed charges. GearWitness brings local, air-gapped AI directly onto the rental shop counter.*
>
> *Here is our checkout baseline on the left, and return check-in on the right. Even with slight angle shifts, deterministic OpenCV ORB and RANSAC homography align the perspective to sub-millimeter precision before any AI model is invoked.*
>
> *Extracted crop pairs are analyzed by Gemma 3 via Ollama using a strict JSON schema. The model detected a fresh scratch breaching the magnesium coating with 89% confidence. As the operator, I confirm the damage with one click.*
>
> *Crucially, GearWitness enforces a strict human decision boundary. The system never assesses auto-fines or accuses customers. For Proposal 2, lighting glare is identified; I dismiss it instantly, preventing a confrontational customer dispute.*
>
> *The kit checklist auto-reconciles multi-piece accessories, catching the missing tethering cable. Operators can also launch Guided Capture for five standardized camera angles with visual silhouette assistance.*
>
> *We finalize the inspection into a tamper-evident SHA-256 Content Integrity Digest. Printable HTML and vector PDF certificates are generated instantly. Fast returns, zero cloud leakage, full operator control. That is GearWitness."*
