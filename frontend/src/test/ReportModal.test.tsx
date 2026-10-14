import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ReportModal } from "../components/ReportModal";
import { Inspection } from "../types";
import * as api from "../api";

const mockInspection: Inspection = {
  id: "insp_demo_report",
  asset_id: "asset_01",
  asset_name: "Sony FX3 Cinema Kit",
  serial_number: "4892011",
  customer_reference: "CUST-7749-BERLIN",
  status: "review_ready",
  media: [],
  proposals: [],
  kit_checklist: [],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const mockManifest = {
  inspection_id: "insp_demo_report",
  asset_name: "Sony FX3 Cinema Kit",
  serial_number: "4892011",
  customer_reference: "CUST-7749-BERLIN",
  checkout_timestamp: new Date().toISOString(),
  checkin_timestamp: new Date().toISOString(),
  generated_at: new Date().toISOString(),
  gearwitness_version: "0.1.0",
  app_mode: "fixture",
  model_used: "gemma3:4b",
  source_media_hashes: { front_checkout: "abcdef123456" },
  total_proposals: 2,
  confirmed_proposals: 1,
  dismissed_proposals: 1,
  uncertain_proposals: 0,
  checklist_status: { "Camera Body": true },
  disclaimer: "Human decision support only.",
  manifest_hash_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
};

describe("ReportModal Component", () => {
  it("loads and displays manifest metrics and content integrity digest", async () => {
    vi.spyOn(api, "fetchManifest").mockResolvedValue(mockManifest as any);

    render(
      <ReportModal
        inspection={mockInspection}
        isOpen={true}
        onClose={vi.fn()}
        onInspectionUpdated={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("SHA-256 CONTENT INTEGRITY DIGEST")).toBeInTheDocument();
    });

    expect(screen.getByText("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")).toBeInTheDocument();
    expect(screen.getByText("Export JSON")).toBeInTheDocument();
    expect(screen.getByText("View HTML")).toBeInTheDocument();
    expect(screen.getByText("Download PDF")).toBeInTheDocument();
  });

  it("handles server-side approval gate and shows error when unresolved", async () => {
    vi.spyOn(api, "fetchManifest").mockResolvedValue(mockManifest as any);
    vi.spyOn(api, "approveInspection").mockRejectedValue(
      new Error("Cannot approve: 1 proposal unresolved.")
    );

    render(
      <ReportModal
        inspection={mockInspection}
        isOpen={true}
        onClose={vi.fn()}
        onInspectionUpdated={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("SHA-256 CONTENT INTEGRITY DIGEST")).toBeInTheDocument();
    });

    const approveBtn = screen.getByRole("button", { name: /Approve & Seal Manifest/i });
    fireEvent.click(approveBtn);

    await waitFor(() => {
      expect(screen.getByText(/Cannot approve: 1 proposal unresolved/i)).toBeInTheDocument();
    });
  });

  it("handles manifest load failure with actionable retry", async () => {
    vi.spyOn(api, "fetchManifest").mockRejectedValueOnce(new Error("Network timeout"));

    render(
      <ReportModal
        inspection={mockInspection}
        isOpen={true}
        onClose={vi.fn()}
        onInspectionUpdated={vi.fn()}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Unable to Compile Manifest")).toBeInTheDocument();
    });

    expect(screen.getByText("Retry Compilation")).toBeInTheDocument();
  });
});
