import {
  HealthResponse,
  Inspection,
  ExportManifest,
  ProposalDecision,
} from "./types";

const API_BASE = "/api/v1";

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchInspections(): Promise<Inspection[]> {
  const res = await fetch(`${API_BASE}/inspections`);
  if (!res.ok) throw new Error(`Failed to fetch inspections: ${res.statusText}`);
  return res.json();
}

export async function fetchInspection(id: string): Promise<Inspection> {
  const res = await fetch(`${API_BASE}/inspections/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch inspection ${id}: ${res.statusText}`);
  return res.json();
}

export async function decideProposal(
  inspectionId: string,
  proposalId: string,
  decision: ProposalDecision,
  notes?: string
): Promise<Inspection> {
  const res = await fetch(
    `${API_BASE}/inspections/${inspectionId}/proposals/${proposalId}/decision`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, notes }),
    }
  );
  if (!res.ok) throw new Error(`Failed to update proposal decision: ${res.statusText}`);
  return res.json();
}

export async function updateChecklistItem(
  inspectionId: string,
  itemId: string,
  isPresent: boolean
): Promise<Inspection> {
  const res = await fetch(
    `${API_BASE}/inspections/${inspectionId}/checklist/${itemId}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_present_checkin: isPresent }),
    }
  );
  if (!res.ok) throw new Error(`Failed to update checklist item: ${res.statusText}`);
  return res.json();
}

export async function triggerAnalysis(inspectionId: string): Promise<Inspection> {
  const res = await fetch(`${API_BASE}/inspections/${inspectionId}/analyze`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Analysis failed: ${res.statusText}`);
  return res.json();
}

export async function approveInspection(inspectionId: string): Promise<Inspection> {
  const res = await fetch(`${API_BASE}/inspections/${inspectionId}/approve`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Approval failed: ${res.statusText}`);
  return res.json();
}

export async function fetchManifest(inspectionId: string): Promise<ExportManifest> {
  const res = await fetch(`/api/v1/reports/${inspectionId}/manifest`);
  if (!res.ok) throw new Error(`Failed to fetch manifest: ${res.statusText}`);
  return res.json();
}

export function getReportHtmlUrl(inspectionId: string): string {
  return `/api/v1/reports/${inspectionId}/html`;
}

export function getReportPdfUrl(inspectionId: string): string {
  return `/api/v1/reports/${inspectionId}/pdf`;
}
