import React, { useState, useRef } from "react";
import {
  Camera,
  CheckCircle,
  AlertCircle,
  Upload,
  X,
  ChevronRight,
  ShieldCheck,
  RotateCcw,
} from "lucide-react";
import { CaptureView, Inspection } from "../types";
import { uploadMedia, fetchInspection } from "../api";

interface GuidedCaptureModalProps {
  inspectionId: string;
  isOpen: boolean;
  onClose: () => void;
  onInspectionUpdated: (inspection: Inspection) => void;
}

interface AngleGuide {
  view: CaptureView;
  title: string;
  description: string;
  instructions: string;
}

const ANGLE_GUIDES: AngleGuide[] = [
  {
    view: "front",
    title: "1. Front Mount & Controls",
    description: "Align lens mount / front housing directly facing lens at eye-level.",
    instructions: "Ensure cap is removed or clean. Check front dial, buttons, and sensor glass.",
  },
  {
    view: "back",
    title: "2. Back Display & Articulation",
    description: "Rear LCD screen unfolded, thumb dial, and rear command buttons.",
    instructions: "Screen powered off or on neutral display to highlight micro-scratches.",
  },
  {
    view: "top",
    title: "3. Top Plate & Hotshoe",
    description: "Cold/hot shoe rails, top LCD, audio handle locking pins.",
    instructions: "Capture straight-down 90° angle. Inspect shoe bracket for bending.",
  },
  {
    view: "accessories",
    title: "4. Accessories & Kit Layout",
    description: "Flat-lay arrangement of all batteries, chargers, cables, and media.",
    instructions: "Lay items separated by 2 inches on contrasting mat. Avoid overlapping.",
  },
  {
    view: "detail",
    title: "5. Detail / Macro Close-Up",
    description: "Targeted close-up of high-wear touchpoints, grip rubber, and ports.",
    instructions: "Open port rubber doors (HDMI, USB-C, Audio) to verify pin integrity.",
  },
];

export const GuidedCaptureModal: React.FC<GuidedCaptureModalProps> = ({
  inspectionId,
  isOpen,
  onClose,
  onInspectionUpdated,
}) => {
  const [selectedAngle, setSelectedAngle] = useState<CaptureView>("front");
  const [capturePhase, setCapturePhase] = useState<"checkout" | "checkin">("checkin");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const currentGuide = ANGLE_GUIDES.find((g) => g.view === selectedAngle) || ANGLE_GUIDES[0];
  const currentIndex = ANGLE_GUIDES.findIndex((g) => g.view === selectedAngle);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null);
    setUploadSuccess(false);
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    if (!file.type.startsWith("image/")) {
      setErrorMessage("Please select a valid image file (JPEG, PNG, WebP).");
      return;
    }

    if (file.size > 25 * 1024 * 1024) {
      setErrorMessage("Image exceeds 25 MB file size limit.");
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setErrorMessage(null);

    try {
      await uploadMedia(
        inspectionId,
        selectedFile,
        selectedAngle,
        capturePhase === "checkout"
      );
      setUploadSuccess(true);
      const updatedInsp = await fetchInspection(inspectionId);
      onInspectionUpdated(updatedInsp);

      // Advance to next angle if not at last step
      if (currentIndex < ANGLE_GUIDES.length - 1) {
        setTimeout(() => {
          setSelectedAngle(ANGLE_GUIDES[currentIndex + 1].view);
          setSelectedFile(null);
          setPreviewUrl(null);
          setUploadSuccess(false);
        }, 1200);
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to upload image. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRetake = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setUploadSuccess(false);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div
      className="modal-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="capture-title"
    >
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
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Phase Switcher (Checkout vs Return) */}
          <div className="phase-switcher-bar">
            <span className="phase-label">Capture Phase:</span>
            <div className="btn-group">
              <button
                className={`btn btn-sm ${
                  capturePhase === "checkout" ? "btn-primary" : "btn-secondary"
                }`}
                onClick={() => {
                  setCapturePhase("checkout");
                  handleRetake();
                }}
              >
                1. Baseline Checkout
              </button>
              <button
                className={`btn btn-sm ${
                  capturePhase === "checkin" ? "btn-primary" : "btn-secondary"
                }`}
                onClick={() => {
                  setCapturePhase("checkin");
                  handleRetake();
                }}
              >
                2. Return Check-in
              </button>
            </div>
          </div>

          <div className="capture-workspace">
            {/* Left: 5-Point Step Selector */}
            <div className="angles-step-list" role="tablist" aria-label="Angle Selection">
              {ANGLE_GUIDES.map((guide, idx) => (
                <button
                  key={guide.view}
                  role="tab"
                  aria-selected={selectedAngle === guide.view}
                  className={`angle-step-card ${
                    selectedAngle === guide.view ? "active" : ""
                  }`}
                  onClick={() => {
                    setSelectedAngle(guide.view);
                    handleRetake();
                  }}
                  id={`angle-step-${guide.view}`}
                >
                  <span className="angle-icon">
                    <Camera size={18} />
                  </span>
                  <div className="angle-text">
                    <span className="angle-name">{guide.title}</span>
                    <span className="angle-desc-short">{guide.description}</span>
                  </div>
                  {idx < currentIndex && (
                    <span className="step-complete-icon text-teal">
                      <CheckCircle size={14} />
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Right: Active Guide Guidance */}
            <div className="angle-detail-pane">
              <div className="angle-detail-header">
                <h3>{currentGuide.title}</h3>
                <span className="target-pill font-mono">Angle ID: {currentGuide.view}</span>
              </div>

              {/* Viewport Reticle / Image Preview */}
              <div className="alignment-guideline-box">
                {previewUrl ? (
                  <div className="preview-container">
                    <img
                      src={previewUrl}
                      alt={`Preview for ${currentGuide.view}`}
                      className="capture-preview-img"
                    />
                    {uploadSuccess && (
                      <div className="upload-success-overlay">
                        <CheckCircle size={32} className="text-teal" />
                        <span>Uploaded & Recorded</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="reticle-frame">
                    <div className="reticle-corner top-left" />
                    <div className="reticle-corner top-right" />
                    <div className="reticle-corner bottom-left" />
                    <div className="reticle-corner bottom-right" />
                    <div className="reticle-center-crosshair">+</div>
                    <div className="reticle-icon-silhouette">
                      <Camera size={36} />
                    </div>
                    <div className="reticle-overlay-text">
                      ALIGN SUBJECT WITHIN RECTANGLE
                    </div>
                  </div>
                )}
              </div>

              {errorMessage && (
                <div className="upload-error-banner" role="alert">
                  <AlertCircle size={16} />
                  <span>{errorMessage}</span>
                </div>
              )}

              <div className="guidance-instructions">
                <h4>Alignment Protocol</h4>
                <p>{currentGuide.instructions}</p>
                <ul>
                  <li>Keep camera parallel to the subject plane (within ±10° pitch/yaw).</li>
                  <li>Diffuse overhead lighting prevents harsh specularity and false glare flags.</li>
                  <li>
                    <ShieldCheck size={14} className="inline mr-1" />
                    EXIF metadata is stripped on server ingest for privacy.
                  </li>
                </ul>
              </div>

              {/* Real Input Capture Action */}
              <div className="capture-action-row">
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  capture="environment"
                  ref={fileInputRef}
                  style={{ display: "none" }}
                  onChange={handleFileSelect}
                  id="capture-file-input"
                />

                {!selectedFile ? (
                  <button
                    className="btn btn-primary"
                    id="btn-mock-capture"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Camera size={16} className="mr-2" />
                    Snap or Upload Photo ({currentGuide.view.toUpperCase()})
                  </button>
                ) : (
                  <div className="selected-file-controls">
                    <button
                      className="btn btn-success"
                      onClick={handleUpload}
                      disabled={isUploading || uploadSuccess}
                      id="btn-confirm-upload"
                    >
                      {isUploading ? (
                        "Uploading & Aligning..."
                      ) : uploadSuccess ? (
                        <>
                          <CheckCircle size={16} className="mr-1" /> Complete
                        </>
                      ) : (
                        <>
                          <Upload size={16} className="mr-1" /> Submit Photo
                        </>
                      )}
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={handleRetake}
                      disabled={isUploading}
                    >
                      <RotateCcw size={14} className="mr-1" /> Retake
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close Guide
          </button>
          {currentIndex < ANGLE_GUIDES.length - 1 && (
            <button
              className="btn btn-secondary"
              onClick={() => {
                setSelectedAngle(ANGLE_GUIDES[currentIndex + 1].view);
                handleRetake();
              }}
            >
              Skip to Next <ChevronRight size={14} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
