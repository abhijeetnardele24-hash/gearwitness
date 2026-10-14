import React, { useState } from "react";
import { CaptureView } from "../types";

interface GuidedCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadMock?: (view: CaptureView, isCheckout: boolean) => void;
}

interface AngleGuide {
  view: CaptureView;
  title: string;
  description: string;
  instructions: string;
  silhouetteIcon: string;
}

const ANGLE_GUIDES: AngleGuide[] = [
  {
    view: "front",
    title: "1. Front Mount & Controls",
    description: "Align lens mount / front housing directly facing lens at eye-level.",
    instructions: "Ensure cap is removed or clean. Check front dial, buttons, and sensor glass.",
    silhouetteIcon: "📷",
  },
  {
    view: "back",
    title: "2. Back Display & Articulation",
    description: "Rear LCD screen unfolded, thumb dial, and rear command buttons.",
    instructions: "Screen powered off or on neutral display to highlight micro-scratches.",
    silhouetteIcon: "🔲",
  },
  {
    view: "top",
    title: "3. Top Plate & Hotshoe",
    description: "Cold/hot shoe rails, top LCD, audio handle locking pins.",
    instructions: "Capture straight-down 90° angle. Inspect shoe bracket for bending.",
    silhouetteIcon: "⬆️",
  },
  {
    view: "accessories",
    title: "4. Accessories & Kit Layout",
    description: "Flat-lay arrangement of all batteries, chargers, cables, and media.",
    instructions: "Lay items separated by 2 inches on contrasting mat. Avoid overlapping.",
    silhouetteIcon: "🔌",
  },
  {
    view: "detail",
    title: "5. Detail / Macro Close-Up",
    description: "Targeted close-up of high-wear touchpoints, grip rubber, and ports.",
    instructions: "Open port rubber doors (HDMI, USB-C, Audio) to verify pin integrity.",
    silhouetteIcon: "🔍",
  },
];

export const GuidedCaptureModal: React.FC<GuidedCaptureModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [selectedAngle, setSelectedAngle] = useState<CaptureView>("front");
  const [capturePhase, setCapturePhase] = useState<"checkout" | "checkin">("checkin");

  if (!isOpen) return null;

  const currentGuide = ANGLE_GUIDES.find((g) => g.view === selectedAngle) || ANGLE_GUIDES[0];

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="capture-title">
      <div className="modal-content capture-modal">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <h2 id="capture-title" className="modal-title">
              Standard 5-Point Return Capture Guide
            </h2>
            <span className="modal-subtitle">
              Ensures reproducible camera geometry for sub-millimeter homography alignment
            </span>
          </div>
          <button
            className="btn btn-icon btn-sm"
            onClick={onClose}
            aria-label="Close dialog"
            id="btn-close-capture-modal"
          >
            ✕
          </button>
        </div>

        <div className="modal-body">
          {/* Phase Switcher (Checkout vs Return) */}
          <div className="phase-switcher-bar">
            <span className="phase-label">Capture Mode:</span>
            <div className="btn-group">
              <button
                className={`btn btn-sm ${capturePhase === "checkout" ? "btn-primary" : "btn-secondary"}`}
                onClick={() => setCapturePhase("checkout")}
              >
                1. Baseline Checkout
              </button>
              <button
                className={`btn btn-sm ${capturePhase === "checkin" ? "btn-primary" : "btn-secondary"}`}
                onClick={() => setCapturePhase("checkin")}
              >
                2. Return Check-in
              </button>
            </div>
          </div>

          <div className="capture-workspace">
            {/* Left: 5-Point Step Selector */}
            <div className="angles-step-list" role="tablist" aria-label="Angle Selection">
              {ANGLE_GUIDES.map((guide) => (
                <button
                  key={guide.view}
                  role="tab"
                  aria-selected={selectedAngle === guide.view}
                  className={`angle-step-card ${selectedAngle === guide.view ? "active" : ""}`}
                  onClick={() => setSelectedAngle(guide.view)}
                  id={`angle-step-${guide.view}`}
                >
                  <span className="angle-icon">{guide.silhouetteIcon}</span>
                  <div className="angle-text">
                    <span className="angle-name">{guide.title}</span>
                    <span className="angle-desc-short">{guide.description}</span>
                  </div>
                </button>
              ))}
            </div>

            {/* Right: Active Guide Guidance */}
            <div className="angle-detail-pane">
              <div className="angle-detail-header">
                <h3>{currentGuide.title}</h3>
                <span className="target-pill font-mono">Angle ID: {currentGuide.view}</span>
              </div>

              <div className="alignment-guideline-box">
                <div className="reticle-frame">
                  <div className="reticle-corner top-left" />
                  <div className="reticle-corner top-right" />
                  <div className="reticle-corner bottom-left" />
                  <div className="reticle-corner bottom-right" />
                  <div className="reticle-center-crosshair">+</div>
                  <div className="reticle-icon-silhouette">
                    {currentGuide.silhouetteIcon}
                  </div>
                  <div className="reticle-overlay-text">
                    ALIGN SUBJECT WITHIN RECTANGLE
                  </div>
                </div>
              </div>

              <div className="guidance-instructions">
                <h4>Alignment Protocol</h4>
                <p>{currentGuide.instructions}</p>
                <ul>
                  <li>Keep camera parallel to the subject plane (within ±10° pitch/yaw).</li>
                  <li>Diffuse overhead lighting prevents harsh specularity and false glare flags.</li>
                  <li>Full resolution 1080p+ photo is automatically stripped of GPS EXIF tags locally.</li>
                </ul>
              </div>

              <div className="capture-action-row">
                <div className="file-input-wrapper">
                  <button className="btn btn-primary" id="btn-mock-capture">
                    📷 Snap or Upload Photo ({currentGuide.view.toUpperCase()})
                  </button>
                  <span className="hint-text text-muted">
                    Photo will be matched against baseline homography instantly.
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
};
