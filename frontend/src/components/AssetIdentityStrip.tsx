import React from "react";
import { Inspection } from "../types";

interface AssetIdentityStripProps {
  inspection: Inspection;
  onRunAnalysis: () => void;
  isAnalyzing: boolean;
}

export const AssetIdentityStrip: React.FC<AssetIdentityStripProps> = ({
  inspection,
  onRunAnalysis,
  isAnalyzing,
}) => {
  const steps = [
    { label: "1. Baseline Checkout", done: !!inspection.checkout_timestamp },
    { label: "2. Check-in Return", done: !!inspection.checkin_timestamp },
    {
      label: "3. CV & Vision Alignment",
      done: inspection.status === "review_ready" || inspection.status === "approved",
    },
    { label: "4. Operator Review", done: inspection.status === "approved" },
  ];

  const totalProposals = inspection.proposals.length;
  const confirmedCount = inspection.proposals.filter(
    (p) => p.operator_decision === "confirmed"
  ).length;
  const dismissedCount = inspection.proposals.filter(
    (p) => p.operator_decision === "dismissed"
  ).length;
  const uncertainCount = inspection.proposals.filter(
    (p) => p.operator_decision === "uncertain"
  ).length;
  const pendingCount = inspection.proposals.filter(
    (p) => p.operator_decision === "pending"
  ).length;

  return (
    <section className="asset-identity-strip" aria-label="Asset & Inspection Identity">
      <div className="asset-meta-main">
        <div className="asset-headline">
          <h1 className="asset-title" id="asset-title">{inspection.asset_name}</h1>
          <span className={`status-badge status-${inspection.status}`}>
            {inspection.status === "approved"
              ? "APPROVED & SIGNED"
              : inspection.status === "review_ready"
              ? "OPERATOR REVIEW"
              : inspection.status.toUpperCase()}
          </span>
        </div>

        <div className="meta-grid">
          <div className="meta-item">
            <span className="meta-label">Serial Number</span>
            <span className="meta-value font-mono" id="val-serial">{inspection.serial_number}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Rental Ref</span>
            <span className="meta-value font-mono" id="val-rental-ref">{inspection.customer_reference}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Checkout Date</span>
            <span className="meta-value">
              {inspection.checkout_timestamp
                ? new Date(inspection.checkout_timestamp).toLocaleDateString()
                : "N/A"}
            </span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Return Date</span>
            <span className="meta-value">
              {inspection.checkin_timestamp
                ? new Date(inspection.checkin_timestamp).toLocaleDateString()
                : "Pending"}
            </span>
          </div>
        </div>
      </div>

      <div className="strip-divider" aria-hidden="true" />

      <div className="proposal-tally">
        <div className="tally-item">
          <span className="tally-count font-mono" id="tally-total">{totalProposals}</span>
          <span className="tally-label">Proposals</span>
        </div>
        <div className="tally-item confirmed">
          <span className="tally-count font-mono" id="tally-confirmed">{confirmedCount}</span>
          <span className="tally-label">Confirmed</span>
        </div>
        <div className="tally-item dismissed">
          <span className="tally-count font-mono" id="tally-dismissed">{dismissedCount}</span>
          <span className="tally-label">Dismissed</span>
        </div>
        <div className="tally-item uncertain">
          <span className="tally-count font-mono" id="tally-uncertain">{uncertainCount}</span>
          <span className="tally-label">Uncertain</span>
        </div>
        <div className="tally-item pending">
          <span className="tally-count font-mono" id="tally-pending">{pendingCount}</span>
          <span className="tally-label">Pending</span>
        </div>
      </div>

      <div className="strip-actions">
        <div className="pipeline-steps" aria-label="Inspection Workflow Steps">
          {steps.map((st, i) => (
            <div key={i} className={`step-badge ${st.done ? "step-done" : "step-pending"}`}>
              {st.done ? "✓" : "○"} {st.label}
            </div>
          ))}
        </div>

        {inspection.status !== "approved" && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={onRunAnalysis}
            disabled={isAnalyzing}
            id="btn-re-run-cv"
            aria-label="Re-run Computer Vision and Multimodal Analysis"
          >
            {isAnalyzing ? "Analyzing..." : "Re-run Alignment"}
          </button>
        )}
      </div>
    </section>
  );
};
