# GearWitness Video Demonstration Script

> **Duration:** 2 Minutes 45 Seconds  
> **Target Audience:** Hackathon Judges, DEV Community, Rental Operations Managers  
> **Setting:** GearWitness Counter Workstation on `http://127.0.0.1:8000`  

---

## Act 1: The Rental Counter Dilemma (0:00 – 0:35)

- **[Visual]:** Opening title slide with the GearWitness cover image and logo.
- **[Voiceover]:**  
  *"Every equipment rental business—from high-end cinema rental houses in Hollywood to neighborhood camera co-ops—dreads the return counter. A client walks in with a $15,000 cinema package. There are five cases, twenty cables, three lenses, and a tight deadline. The rental agent has two choices: hold up the line for 20 minutes with a magnifying glass, or rush the check-in and discover a scratched front dial or missing $200 cable hours after the client has left."*
- **[Visual]:** Cut to GearWitness running in the browser. Highlight the "Forensic Calm" aesthetic: warm stone palette, crisp slate typography, and clear status indicators.

---

## Act 2: Deterministic Alignment & Multi-Angle Comparison (0:35 – 1:20)

- **[Visual]:** Point cursor to the **Asset Identity Strip**.  
  Show the Sony FX3 Cinema Kit (`Serial #4892011`, `Rental Ref #RN-2026-8941`).
- **[Voiceover]:**  
  *"This is GearWitness. It’s an air-gapped, privacy-first return inspection station powered by local computer vision and Google’s Gemma 3 multimodal model. Notice that nothing is sent to the cloud. Customer serial numbers, photos, and project names remain 100% on this local counter computer."*
- **[Visual]:** Drag the split reveal slider across the Sony FX3 camera body.
- **[Voiceover]:**  
  *"Here’s the baseline checkout photo on the left, and the return photo on the right. Even if the customer returned the camera at a slightly different angle, our OpenCV ORB and RANSAC homography engine aligns the perspective within sub-millimeter precision."*
- **[Visual]:** Toggle **Diff Heatmap** on. Show the red/amber contour highlighting the anomalous front dial region. Switch to **Side-by-Side** mode, then back to Split Reveal.

---

## Act 3: AI Proposals & Human Decision Boundary (1:20 – 2:05)

- **[Visual]:** Move cursor to the **Evidence Tray** on the right column. Click on **Proposal #1 (Front Dial Scratch)**.
- **[Voiceover]:**  
  *"The CV engine identified an anomaly and passed the crop pair to Gemma 3 running locally on Ollama. The model identified a fresh scratch breaching the anodized coating, rated it Minor severity with 89% confidence, and provided an objective rationale."*
- **[Visual]:** Click **`✓ Confirm Damage`**. The card badge turns green.
- **[Visual]:** Click on **Proposal #2 (Sensor Glass Glare)**.
- **[Voiceover]:**  
  *"Here is Proposal #2. The model correctly classified this highlight as lighting glare rather than a physical scratch. Because GearWitness enforces a strict human decision boundary, the system never auto-charges the customer. I simply click `✕ Dismiss (Wear / Glare)`."*
- **[Visual]:** Scroll down to the **Kit Inventory Checklist**. Click the **Missing** button on the HDMI 4K Cable.
- **[Voiceover]:**  
  *"The accessory flat-lay check confirmed that the HDMI cable wasn't returned in the Pelican case. With one click, the inventory checklist is updated."*

---

## Act 4: Cryptographic Audit Manifest & Sign-Off (2:05 – 2:45)

- **[Visual]:** Click **Review & Export** in the top right.
- **[Voiceover]:**  
  *"Now we click Review & Export. GearWitness compiles a complete audit manifest sealed with a cryptographic SHA-256 hash. This seals the raw hashes of the photos, the operator’s decisions, and the kit checklist into a tamper-evident record."*
- **[Visual]:** Click **`✓ Approve & Seal Manifest`**.
- **[Visual]:** Click **Printable HTML Report ↗** and **Download PDF Report ↓**. Show the clean vector report with company branding, itemized defects, and legal disclaimer.
- **[Voiceover]:**  
  *"Both printable HTML and PDF certificates are ready instantly. Fast check-ins, zero disputes, zero cloud privacy risks. That is GearWitness."*
- **[Visual]:** Final slide with GitHub repository link:  
  `https://github.com/abhijeetnardele24-hash/gearwitness`
