import React, { useState } from "react";
import { ChangeProposal, ProposalDecision } from "../types";

interface EvidenceTrayProps {
  proposals: ChangeProposal[];
  selectedProposalId: string | null;
  onSelectProposal: (id: string) => void;
  onDecideProposal: (proposalId: string, decision: ProposalDecision, notes?: string) => void;
  onJumpToView: (view: ChangeProposal["capture_view"]) => void;
}

export const EvidenceTray: React.FC<EvidenceTrayProps> = ({
  proposals,
  selectedProposalId,
  onSelectProposal,
  onDecideProposal,
  onJumpToView,
}) => {
  const [filter, setFilter] = useState<"all" | "pending" | "confirmed" | "dismissed">("all");
  const [editingNotes, setEditingNotes] = useState<Record<string, string>>({});

  const filteredProposals = proposals.filter((p) => {
    if (filter === "all") return true;
    return p.operator_decision === filter;
  });

  const getImgSrc = (path?: string) => {
    if (!path) return "";
    if (path.startsWith("http") || path.startsWith("/")) return path;
    return `/${path}`;
  };

  const handleDecision = (id: string, decision: ProposalDecision) => {
    const note = editingNotes[id];
    onDecideProposal(id, decision, note);
  };

  return (
    <section className="evidence-tray-section" aria-label="AI Change Proposals & Evidence Tray">
      <div className="tray-header">
        <div className="tray-title-wrap">
          <h2 className="section-title">Change Proposals ({proposals.length})</h2>
          <span className="tray-subtitle">AI-flagged anomalies requiring human verification</span>
        </div>

        <div className="tray-filters" role="group" aria-label="Filter proposals">
          <button
            className={`filter-pill ${filter === "all" ? "active" : ""}`}
            onClick={() => setFilter("all")}
          >
            All ({proposals.length})
          </button>
          <button
            className={`filter-pill ${filter === "pending" ? "active" : ""}`}
            onClick={() => setFilter("pending")}
          >
            Pending ({proposals.filter((p) => p.operator_decision === "pending").length})
          </button>
          <button
            className={`filter-pill ${filter === "confirmed" ? "active" : ""}`}
            onClick={() => setFilter("confirmed")}
          >
            Confirmed ({proposals.filter((p) => p.operator_decision === "confirmed").length})
          </button>
          <button
            className={`filter-pill ${filter === "dismissed" ? "active" : ""}`}
            onClick={() => setFilter("dismissed")}
          >
            Dismissed ({proposals.filter((p) => p.operator_decision === "dismissed").length})
          </button>
        </div>
      </div>

      <div className="proposals-list" role="list">
        {filteredProposals.length === 0 ? (
          <div className="empty-tray-message">
            <p>No proposals match the selected filter.</p>
          </div>
        ) : (
          filteredProposals.map((prop, idx) => {
            const isSelected = prop.id === selectedProposalId;
            const currentNote =
              editingNotes[prop.id] !== undefined
                ? editingNotes[prop.id]
                : prop.operator_notes || "";

            return (
              <div
                key={prop.id}
                role="listitem"
                className={`proposal-card ${prop.operator_decision} ${
                  isSelected ? "selected" : ""
                }`}
                onClick={() => onSelectProposal(prop.id)}
                id={`proposal-card-${prop.id}`}
              >
                {/* Card Top Row */}
                <div className="card-top-row">
                  <div className="card-id-badges">
                    <span className="proposal-number font-mono">#{idx + 1}</span>
                    <button
                      className="view-jump-badge capitalize"
                      onClick={(e) => {
                        e.stopPropagation();
                        onJumpToView(prop.capture_view);
                      }}
                      title="Jump to this view on canvas"
                    >
                      {prop.capture_view} ↗
                    </button>
                    <span className={`condition-tag condition-${prop.condition_type}`}>
                      {prop.condition_type.replace("_", " ").toUpperCase()}
                    </span>
                    <span className={`severity-tag severity-${prop.severity}`}>
                      {prop.severity}
                    </span>
                  </div>

                  <div className="confidence-pill" title="Model confidence score">
                    <span>Confidence:</span>
                    <strong className="font-mono">{Math.round(prop.confidence * 100)}%</strong>
                  </div>
                </div>

                {/* Description & AI Rationale */}
                <div className="card-body">
                  <h3 className="proposal-desc">{prop.description}</h3>
                  <div className="rationale-box">
                    <span className="rationale-prefix">Model Observation:</span>
                    <span className="rationale-text">{prop.model_rationale}</span>
                  </div>

                  {/* Crop previews (if available) */}
                  {(prop.checkout_crop_path || prop.checkin_crop_path) && (
                    <div className="crop-previews">
                      {prop.checkout_crop_path && (
                        <div className="crop-item">
                          <span className="crop-label">Baseline</span>
                          <img
                            src={getImgSrc(prop.checkout_crop_path)}
                            alt="Baseline crop"
                            className="crop-img"
                          />
                        </div>
                      )}
                      {prop.checkin_crop_path && (
                        <div className="crop-item">
                          <span className="crop-label">Return</span>
                          <img
                            src={getImgSrc(prop.checkin_crop_path)}
                            alt="Return crop"
                            className="crop-img"
                          />
                        </div>
                      )}
                    </div>
                  )}

                  {/* Operator Notes Input */}
                  <div className="operator-notes-field">
                    <input
                      type="text"
                      placeholder="Add operator notes / explanation..."
                      className="input-notes"
                      value={currentNote}
                      onChange={(e) =>
                        setEditingNotes({
                          ...editingNotes,
                          [prop.id]: e.target.value,
                        })
                      }
                      onClick={(e) => e.stopPropagation()}
                      onBlur={() => {
                        if (currentNote !== (prop.operator_notes || "")) {
                          onDecideProposal(prop.id, prop.operator_decision, currentNote);
                        }
                      }}
                      aria-label="Operator notes for proposal"
                    />
                  </div>
                </div>

                {/* Decision Actions Bar */}
                <div className="card-actions" onClick={(e) => e.stopPropagation()}>
                  <button
                    className={`btn btn-sm action-confirm ${
                      prop.operator_decision === "confirmed" ? "active" : ""
                    }`}
                    onClick={() => handleDecision(prop.id, "confirmed")}
                    id={`btn-confirm-${prop.id}`}
                    aria-label={`Confirm damage for proposal ${idx + 1}`}
                  >
                    ✓ Confirm Damage
                  </button>

                  <button
                    className={`btn btn-sm action-dismiss ${
                      prop.operator_decision === "dismissed" ? "active" : ""
                    }`}
                    onClick={() => handleDecision(prop.id, "dismissed")}
                    id={`btn-dismiss-${prop.id}`}
                    aria-label={`Dismiss proposal ${idx + 1} as normal wear or artifact`}
                  >
                    ✕ Dismiss (Wear / Glare)
                  </button>

                  <button
                    className={`btn btn-sm action-uncertain ${
                      prop.operator_decision === "uncertain" ? "active" : ""
                    }`}
                    onClick={() => handleDecision(prop.id, "uncertain")}
                    id={`btn-uncertain-${prop.id}`}
                    aria-label={`Mark proposal ${idx + 1} as uncertain for supervisor`}
                  >
                    ? Mark Uncertain
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
};
