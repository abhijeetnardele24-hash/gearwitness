import React from "react";
import { HealthResponse } from "../types";

interface HeaderProps {
  health: HealthResponse | null;
  onOpenCapture: () => void;
  onOpenReport: () => void;
  onRefresh: () => void;
  isApproved: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  onOpenCapture,
  onOpenReport,
  onRefresh,
  isApproved,
}) => {
  const isFixture = health?.app_mode === "fixture";
  const isOllamaConnected = health?.ollama_connected ?? false;

  return (
    <header className="site-header" role="banner">
      <div className="header-left">
        <div className="brand-logo" aria-hidden="true">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        </div>
        <div>
          <div className="brand-title-wrap">
            <span className="brand-title">GearWitness</span>
            <span className="brand-version">v0.1.0</span>
          </div>
          <span className="brand-subtitle">Local AI Return Inspection · Forensic Calm</span>
        </div>
      </div>

      <div className="header-center">
        <div className="mode-badge-wrap" role="status" aria-label="Operating Mode">
          <span className={`status-indicator ${isFixture ? "status-fixture" : "status-local"}`} />
          <span className="mode-label">
            MODE: <strong>{isFixture ? "DETERMINISTIC FIXTURE" : "LOCAL INFERENCE"}</strong>
          </span>
          <span className="model-info">
            {isFixture
              ? "Synthetic Studio Fixtures"
              : isOllamaConnected
              ? `Ollama · ${health?.model_name || "Gemma 3"}`
              : "Ollama Offline (Fallback)"}
          </span>
        </div>
      </div>

      <div className="header-right">
        <button
          className="btn btn-secondary"
          onClick={onRefresh}
          title="Refresh Data"
          id="btn-refresh"
          aria-label="Refresh inspection data"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
          Refresh
        </button>

        <button
          className="btn btn-secondary"
          onClick={onOpenCapture}
          id="btn-guided-capture"
          aria-label="Open guided 5-point capture assistant"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
            <circle cx="12" cy="13" r="4" />
          </svg>
          Guided Capture
        </button>

        <button
          className="btn btn-primary"
          onClick={onOpenReport}
          id="btn-export-report"
          aria-label="Export audit report and verified manifest"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
          {isApproved ? "Verified Report" : "Review & Export"}
        </button>
      </div>
    </header>
  );
};
