import React, { useState, useEffect, useCallback } from "react";
import { Header } from "./components/Header";
import { AssetIdentityStrip } from "./components/AssetIdentityStrip";
import { CompareCanvas } from "./components/CompareCanvas";
import { EvidenceTray } from "./components/EvidenceTray";
import { KitChecklist } from "./components/KitChecklist";
import { ReportModal } from "./components/ReportModal";
import { GuidedCaptureModal } from "./components/GuidedCaptureModal";
import {
  HealthResponse,
  Inspection,
  CaptureView,
  ProposalDecision,
} from "./types";
import {
  fetchHealth,
  fetchInspections,
  fetchInspection,
  decideProposal,
  updateChecklistItem,
  triggerAnalysis,
} from "./api";

export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [currentInspection, setCurrentInspection] = useState<Inspection | null>(null);
  const [activeView, setActiveView] = useState<CaptureView>("front");
  const [selectedProposalId, setSelectedProposalId] = useState<string | null>(null);

  const [isReportOpen, setIsReportOpen] = useState<boolean>(false);
  const [isCaptureOpen, setIsCaptureOpen] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const [h, list] = await Promise.all([fetchHealth(), fetchInspections()]);
      setHealth(h);
      setInspections(list);
      if (list.length > 0) {
        // Prefer hero demo if present
        const hero = list.find((i) => i.id === "insp_hero_demo") || list[0];
        setCurrentInspection(hero);
      }
    } catch (err: any) {
      console.error("Load error:", err);
      setErrorMsg(err.message || "Failed to connect to GearWitness backend.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle Proposal Decision
  const handleDecideProposal = async (
    proposalId: string,
    decision: ProposalDecision,
    notes?: string
  ) => {
    if (!currentInspection) return;
    try {
      const updated = await decideProposal(
        currentInspection.id,
        proposalId,
        decision,
        notes
      );
      setCurrentInspection(updated);
      setInspections((prev) =>
        prev.map((i) => (i.id === updated.id ? updated : i))
      );
    } catch (err: any) {
      alert(`Decision error: ${err.message}`);
    }
  };

  // Handle Kit Checklist Toggle
  const handleToggleKitItem = async (itemId: string, isPresent: boolean) => {
    if (!currentInspection) return;
    try {
      const updated = await updateChecklistItem(
        currentInspection.id,
        itemId,
        isPresent
      );
      setCurrentInspection(updated);
      setInspections((prev) =>
        prev.map((i) => (i.id === updated.id ? updated : i))
      );
    } catch (err: any) {
      alert(`Checklist error: ${err.message}`);
    }
  };

  // Re-run CV / Analysis
  const handleRunAnalysis = async () => {
    if (!currentInspection) return;
    setIsAnalyzing(true);
    try {
      const updated = await triggerAnalysis(currentInspection.id);
      setCurrentInspection(updated);
      setInspections((prev) =>
        prev.map((i) => (i.id === updated.id ? updated : i))
      );
    } catch (err: any) {
      alert(`Analysis error: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Inspection Switcher
  const handleSwitchInspection = async (id: string) => {
    try {
      const full = await fetchInspection(id);
      setCurrentInspection(full);
      setActiveView("front");
      setSelectedProposalId(null);
    } catch (err: any) {
      alert(`Could not switch inspection: ${err.message}`);
    }
  };

  if (isLoading) {
    return (
      <div className="app-loading-screen" role="status">
        <div className="loading-spinner" />
        <h2>GearWitness Forensic Return Station</h2>
        <p className="text-muted">Loading local models, OpenCV pipeline & test fixtures...</p>
      </div>
    );
  }

  if (errorMsg || !currentInspection) {
    return (
      <div className="app-error-screen" role="alert">
        <h2>GearWitness Backend Unavailable</h2>
        <p>{errorMsg || "No active inspections found."}</p>
        <button className="btn btn-primary" onClick={loadData}>
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="gearwitness-app-layout">
      {/* Global Header */}
      <Header
        health={health}
        onOpenCapture={() => setIsCaptureOpen(true)}
        onOpenReport={() => setIsReportOpen(true)}
        onRefresh={loadData}
        isApproved={currentInspection.status === "approved"}
      />

      {/* Multiple Inspection Selector (if more than 1) */}
      {inspections.length > 1 && (
        <nav className="inspection-selector-bar" aria-label="Active Inspections">
          <span className="selector-label">Active Rental Inspections:</span>
          <div className="selector-pills">
            {inspections.map((insp) => (
              <button
                key={insp.id}
                className={`insp-pill ${insp.id === currentInspection.id ? "active" : ""}`}
                onClick={() => handleSwitchInspection(insp.id)}
                id={`pill-insp-${insp.id}`}
              >
                <strong>{insp.asset_name}</strong>
                <span className="pill-ref font-mono">({insp.customer_reference})</span>
                <span className={`pill-status-dot dot-${insp.status}`} />
              </button>
            ))}
          </div>
        </nav>
      )}

      {/* Main Forensic Workspace */}
      <main className="main-workspace" id="main-content">
        {/* Asset Identity & Status Strip */}
        <AssetIdentityStrip
          inspection={currentInspection}
          onRunAnalysis={handleRunAnalysis}
          isAnalyzing={isAnalyzing}
        />

        {/* 2-Column Split: Visual Compare on Left, Evidence & Checklist on Right */}
        <div className="workspace-split-columns">
          {/* Left Column: Visual Compare Canvas */}
          <div className="column-canvas">
            <CompareCanvas
              inspection={currentInspection}
              activeView={activeView}
              onSelectView={setActiveView}
              selectedProposalId={selectedProposalId}
              onSelectProposal={setSelectedProposalId}
            />
          </div>

          {/* Right Column: AI Proposals Tray & Kit Checklist */}
          <div className="column-evidence">
            <EvidenceTray
              proposals={currentInspection.proposals}
              selectedProposalId={selectedProposalId}
              onSelectProposal={setSelectedProposalId}
              onDecideProposal={handleDecideProposal}
              onJumpToView={(view) => setActiveView(view)}
            />

            <KitChecklist
              items={currentInspection.kit_checklist}
              onToggleItem={handleToggleKitItem}
            />
          </div>
        </div>
      </main>

      {/* Modals */}
      <ReportModal
        inspection={currentInspection}
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        onInspectionUpdated={(updated) => {
          setCurrentInspection(updated);
          setInspections((prev) =>
            prev.map((i) => (i.id === updated.id ? updated : i))
          );
        }}
      />

      <GuidedCaptureModal
        inspectionId={currentInspection.id}
        isOpen={isCaptureOpen}
        onClose={() => setIsCaptureOpen(false)}
        onInspectionUpdated={(updated) => {
          setCurrentInspection(updated);
          setInspections((prev) =>
            prev.map((i) => (i.id === updated.id ? updated : i))
          );
        }}
      />
    </div>
  );
};
