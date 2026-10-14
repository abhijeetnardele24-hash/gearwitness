import React, { useState, useEffect } from "react";
import { Inspection, ExportManifest } from "../types";
import { fetchManifest, approveInspection, getReportHtmlUrl, getReportPdfUrl } from "../api";

interface ReportModalProps {
  inspection: Inspection;
  isOpen: boolean;
  onClose: () => void;
  onInspectionUpdated: (inspection: Inspection) => void;
}

export const ReportModal: React.FC<ReportModalProps> = ({
  inspection,
  isOpen,
  onClose,
  onInspectionUpdated,
}) => {
  const [manifest, setManifest] = useState<ExportManifest | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [isApproving, setIsApproving] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      fetchManifest(inspection.id)
        .then((m) => setManifest(m))
        .catch((err) => console.error("Manifest error:", err))
        .finally(() => setLoading(false));
    }
  }, [isOpen, inspection.id]);

  if (!isOpen) return null;

  const handleApprove = async () => {
    setIsApproving(true);
    try {
      const updated = await approveInspection(inspection.id);
      onInspectionUpdated(updated);
      const newManifest = await fetchManifest(inspection.id);
      setManifest(newManifest);
    } catch (err) {
      console.error("Approval error:", err);
    } finally {
      setIsApproving(false);
    }
  };

  const handleDownloadManifestJson = () => {
    if (!manifest) return;
    const blob = new Blob([JSON.stringify(manifest, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `gearwitness_manifest_${inspection.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const isApproved = inspection.status === "approved";

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal-content report-modal">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <h2 id="modal-title" className="modal-title">
              Audit Report & Evidence Manifest
            </h2>
            <span className="modal-subtitle">
              Cryptographically verified inspection package for {inspection.asset_name}
            </span>
          </div>
          <button
            className="btn btn-icon btn-sm"
            onClick={onClose}
            aria-label="Close dialog"
            id="btn-close-modal"
          >
            ✕
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div className="loading-state">Generating verification manifest...</div>
          ) : manifest ? (
            <>
              {/* Summary Metrics Grid */}
              <div className="manifest-metrics-grid">
                <div className="metric-box">
                  <span className="metric-number font-mono">{manifest.total_proposals}</span>
                  <span className="metric-label">Total Proposals</span>
                </div>
                <div className="metric-box confirmed">
                  <span className="metric-number font-mono">{manifest.confirmed_proposals}</span>
                  <span className="metric-label">Confirmed Damages</span>
                </div>
                <div className="metric-box dismissed">
                  <span className="metric-number font-mono">{manifest.dismissed_proposals}</span>
                  <span className="metric-label">Dismissed (Wear / Glare)</span>
                </div>
                <div className="metric-box uncertain">
                  <span className="metric-number font-mono">{manifest.uncertain_proposals}</span>
                  <span className="metric-label">Uncertain (Review)</span>
                </div>
              </div>

              {/* SHA-256 Manifest Hash Box */}
              <div className="hash-verification-box">
                <div className="hash-header">
                  <span className="hash-badge">SHA-256 MANIFEST INTEGRITY HASH</span>
                  <span className="hash-mode">Mode: {manifest.app_mode.toUpperCase()}</span>
                </div>
                <code className="hash-value" id="val-manifest-hash">
                  {manifest.manifest_hash_sha256 || "Pending final sign-off"}
                </code>
                <p className="hash-note">
                  This SHA-256 hash seals the checkout vs return media hashes, operator decisions, and kit reconciliation into a tamper-evident audit record.
                </p>
              </div>

              {/* Source Evidence Hashes */}
              <div className="evidence-hashes-list">
                <h4 className="hashes-title">Source Media Cryptographic Hashes</h4>
                <div className="hashes-scroll font-mono">
                  {Object.entries(manifest.source_media_hashes).map(([view, hash]) => (
                    <div key={view} className="hash-row">
                      <span className="hash-view-label">{view}:</span>
                      <span className="hash-view-code">{hash}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strict Legal Disclaimer */}
              <div className="legal-disclaimer-box" role="note">
                <strong className="disclaimer-title">HUMAN DECISION BOUNDARY & LEGAL DISCLAIMER</strong>
                <p className="disclaimer-text">{manifest.disclaimer}</p>
              </div>
            </>
          ) : (
            <div>Failed to load manifest.</div>
          )}
        </div>

        <div className="modal-footer">
          <div className="footer-left">
            {!isApproved ? (
              <button
                className="btn btn-success"
                onClick={handleApprove}
                disabled={isApproving}
                id="btn-approve-signoff"
              >
                {isApproving ? "Signing Manifest..." : "✓ Approve & Seal Manifest"}
              </button>
            ) : (
              <span className="badge-pill pill-present font-bold">
                ✓ Manifest Approved & Sealed
              </span>
            )}
          </div>

          <div className="footer-right">
            <button
              className="btn btn-secondary"
              onClick={handleDownloadManifestJson}
              id="btn-download-json"
            >
              Export JSON Manifest
            </button>
            <a
              href={getReportHtmlUrl(inspection.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
              id="btn-view-html-report"
            >
              Printable HTML Report ↗
            </a>
            <a
              href={getReportPdfUrl(inspection.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              id="btn-download-pdf-report"
            >
              Download PDF Report ↓
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
