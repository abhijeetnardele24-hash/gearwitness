import React, { useState, useRef, useEffect, useCallback } from "react";
import { Inspection, CaptureView } from "../types";

interface CompareCanvasProps {
  inspection: Inspection;
  activeView: CaptureView;
  onSelectView: (view: CaptureView) => void;
  selectedProposalId: string | null;
  onSelectProposal: (id: string) => void;
}

export const CompareCanvas: React.FC<CompareCanvasProps> = ({
  inspection,
  activeView,
  onSelectView,
  selectedProposalId,
  onSelectProposal,
}) => {
  const [sliderPos, setSliderPos] = useState<number>(50); // 0 to 100%
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [layoutMode, setLayoutMode] = useState<"reveal" | "side_by_side">("reveal");
  const [showHeatmap, setShowHeatmap] = useState<boolean>(false);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Available views present in inspection media
  const availableViews: CaptureView[] = Array.from(
    new Set(inspection.media.map((m) => m.capture_view))
  ) as CaptureView[];

  // Fallback views if none
  const viewsToDisplay: CaptureView[] =
    availableViews.length > 0 ? availableViews : ["front", "accessories"];

  // Find media for active view
  const checkoutMedia = inspection.media.find(
    (m) => m.capture_view === activeView && m.is_checkout
  );
  const checkinMedia = inspection.media.find(
    (m) => m.capture_view === activeView && !m.is_checkout
  );

  const getImgSrc = (path?: string) => {
    if (!path) return "";
    if (path.startsWith("http") || path.startsWith("/")) return path;
    return `/${path}`;
  };

  const checkoutSrc = getImgSrc(checkoutMedia?.storage_path);
  const checkinSrc = getImgSrc(checkinMedia?.storage_path);

  // Proposals for this view
  const viewProposals = inspection.proposals.filter(
    (p) => p.capture_view === activeView
  );

  // Handle Dragging
  const handlePointerDown = () => setIsDragging(true);
  const handlePointerUp = useCallback(() => setIsDragging(false), []);

  const handlePointerMove = useCallback(
    (e: PointerEvent) => {
      if (!isDragging || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      const percentage = (x / rect.width) * 100;
      setSliderPos(Math.round(percentage));
    },
    [isDragging]
  );

  useEffect(() => {
    window.addEventListener("pointerup", handlePointerUp);
    window.addEventListener("pointermove", handlePointerMove);
    return () => {
      window.removeEventListener("pointerup", handlePointerUp);
      window.removeEventListener("pointermove", handlePointerMove);
    };
  }, [handlePointerUp, handlePointerMove]);

  return (
    <section className="compare-canvas-section" aria-label="Visual Inspection Comparison Canvas">
      {/* Top Toolbar */}
      <div className="canvas-toolbar">
        {/* View Switcher Tabs */}
        <div className="view-tabs" role="tablist" aria-label="Select Camera Angle">
          {viewsToDisplay.map((view) => {
            const hasProposals = inspection.proposals.some(
              (p) => p.capture_view === view && p.operator_decision === "pending"
            );
            return (
              <button
                key={view}
                role="tab"
                aria-selected={activeView === view}
                className={`view-tab ${activeView === view ? "active" : ""}`}
                onClick={() => onSelectView(view)}
                id={`tab-view-${view}`}
              >
                <span className="capitalize">{view}</span>
                {hasProposals && <span className="tab-dot" title="Pending proposals" />}
              </button>
            );
          })}
        </div>

        {/* Display Mode & Overlays */}
        <div className="canvas-controls">
          <div className="btn-group" role="group" aria-label="Comparison Mode">
            <button
              className={`btn btn-sm ${layoutMode === "reveal" ? "btn-primary" : "btn-secondary"}`}
              onClick={() => setLayoutMode("reveal")}
              title="Drag Reveal Split Slider"
              id="mode-split-reveal"
            >
              Split Reveal
            </button>
            <button
              className={`btn btn-sm ${layoutMode === "side_by_side" ? "btn-primary" : "btn-secondary"}`}
              onClick={() => setLayoutMode("side_by_side")}
              title="Side-by-Side Comparison"
              id="mode-side-by-side"
            >
              Side-by-Side
            </button>
          </div>

          <label className="checkbox-toggle" title="Highlight luminance & texture differences">
            <input
              type="checkbox"
              checked={showHeatmap}
              onChange={(e) => setShowHeatmap(e.target.checked)}
              id="toggle-heatmap"
            />
            <span>Diff Heatmap</span>
          </label>

          <div className="zoom-controls" aria-label="Zoom Controls">
            <button
              className="btn btn-icon btn-sm"
              onClick={() => setZoomLevel((z) => Math.max(1, z - 0.25))}
              disabled={zoomLevel <= 1}
              title="Zoom Out"
              aria-label="Zoom Out"
            >
              -
            </button>
            <span className="zoom-label font-mono">{Math.round(zoomLevel * 100)}%</span>
            <button
              className="btn btn-icon btn-sm"
              onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.25))}
              disabled={zoomLevel >= 2.5}
              title="Zoom In"
              aria-label="Zoom In"
            >
              +
            </button>
            {zoomLevel > 1 && (
              <button
                className="btn btn-sm btn-ghost"
                onClick={() => setZoomLevel(1)}
                title="Reset Zoom"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Canvas Viewport */}
      <div
        className={`canvas-viewport ${layoutMode}`}
        ref={containerRef}
        id="compare-viewport"
      >
        {layoutMode === "reveal" ? (
          <div
            className="reveal-container"
            style={{ transform: `scale(${zoomLevel})`, transformOrigin: "center center" }}
          >
            {/* Background Layer: CHECK-IN RETURN */}
            <div className="reveal-layer checkin-layer">
              <img
                src={checkinSrc}
                alt={`Check-in return photo of ${activeView}`}
                className="canvas-image"
                id="img-checkin"
              />
              <span className="layer-watermark checkin-watermark">
                RETURN (CHECK-IN)
              </span>

              {/* Proposals Hotspots on Return Image */}
              {viewProposals.map((prop, idx) => {
                const isSelected = prop.id === selectedProposalId;
                return (
                  <button
                    key={prop.id}
                    className={`proposal-hotspot ${prop.operator_decision} ${
                      isSelected ? "selected" : ""
                    }`}
                    style={{
                      left: `${prop.bounding_box.x}%`,
                      top: `${prop.bounding_box.y}%`,
                      width: `${prop.bounding_box.width}%`,
                      height: `${prop.bounding_box.height}%`,
                    }}
                    onClick={() => onSelectProposal(prop.id)}
                    title={`Proposal #${idx + 1}: ${prop.description} (${prop.operator_decision})`}
                    aria-label={`Select proposal #${idx + 1} ${prop.description}`}
                  >
                    <span className="hotspot-badge">{idx + 1}</span>
                  </button>
                );
              })}

              {/* Heatmap Simulation Layer */}
              {showHeatmap && (
                <div
                  className="heatmap-overlay"
                  aria-hidden="true"
                  style={{
                    opacity: 0.45,
                    mixBlendMode: "color-dodge",
                  }}
                />
              )}
            </div>

            {/* Foreground Layer: CHECKOUT BASELINE (Clipped by slider) */}
            <div
              className="reveal-layer checkout-layer"
              style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
            >
              <img
                src={checkoutSrc}
                alt={`Baseline checkout photo of ${activeView}`}
                className="canvas-image"
                id="img-checkout"
              />
              <span className="layer-watermark checkout-watermark">
                BASELINE (CHECKOUT)
              </span>
            </div>

            {/* Draggable Divider Handle */}
            <div
              className="slider-divider"
              style={{ left: `${sliderPos}%` }}
              onPointerDown={handlePointerDown}
              role="slider"
              tabIndex={0}
              aria-valuenow={sliderPos}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Comparison Divider Position"
              onKeyDown={(e) => {
                if (e.key === "ArrowLeft") setSliderPos((s) => Math.max(0, s - 5));
                if (e.key === "ArrowRight") setSliderPos((s) => Math.min(100, s + 5));
              }}
            >
              <div className="slider-handle">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </div>
            </div>
          </div>
        ) : (
          /* Side-by-Side Mode */
          <div
            className="side-by-side-container"
            style={{ transform: `scale(${zoomLevel})`, transformOrigin: "center center" }}
          >
            <div className="side-panel">
              <div className="panel-header">BASELINE (CHECKOUT)</div>
              <div className="image-wrapper">
                <img
                  src={checkoutSrc}
                  alt={`Baseline checkout view of ${activeView}`}
                  className="canvas-image"
                />
              </div>
            </div>

            <div className="side-panel">
              <div className="panel-header">RETURN (CHECK-IN)</div>
              <div className="image-wrapper">
                <img
                  src={checkinSrc}
                  alt={`Check-in return view of ${activeView}`}
                  className="canvas-image"
                />
                {viewProposals.map((prop, idx) => {
                  const isSelected = prop.id === selectedProposalId;
                  return (
                    <button
                      key={prop.id}
                      className={`proposal-hotspot ${prop.operator_decision} ${
                        isSelected ? "selected" : ""
                      }`}
                      style={{
                        left: `${prop.bounding_box.x}%`,
                        top: `${prop.bounding_box.y}%`,
                        width: `${prop.bounding_box.width}%`,
                        height: `${prop.bounding_box.height}%`,
                      }}
                      onClick={() => onSelectProposal(prop.id)}
                      title={`Proposal #${idx + 1}: ${prop.description}`}
                      aria-label={`Select proposal #${idx + 1}`}
                    >
                      <span className="hotspot-badge">{idx + 1}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="canvas-footer-hint">
        <span>💡 Drag the divider to inspect changes. Click numbered boxes to review proposal details.</span>
        <span className="font-mono text-muted">
          Active View: {activeView.toUpperCase()} · Proposals in view: {viewProposals.length}
        </span>
      </div>
    </section>
  );
};
