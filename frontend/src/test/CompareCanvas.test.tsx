import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { CompareCanvas } from "../components/CompareCanvas";
import { Inspection } from "../types";

const mockInspection: Inspection = {
  id: "insp_demo_canvas",
  asset_id: "asset_01",
  asset_name: "Sony FX3 Cinema Kit",
  serial_number: "4892011",
  customer_reference: "CUST-7749-BERLIN",
  status: "review_ready",
  media: [
    {
      id: "m_co_front",
      filename: "front_checkout.jpg",
      storage_path: "data/fixtures/sony_fx3_front_checkout.jpg",
      public_url: "/fixtures/sony_fx3_front_checkout.jpg",
      sha256_hash: "hash1",
      file_size_bytes: 1024,
      mime_type: "image/jpeg",
      width: 1920,
      height: 1080,
      capture_view: "front",
      captured_at: new Date().toISOString(),
      is_checkout: true,
    },
    {
      id: "m_ci_front",
      filename: "front_checkin.jpg",
      storage_path: "data/fixtures/sony_fx3_front_checkin.jpg",
      public_url: "/fixtures/sony_fx3_front_checkin.jpg",
      sha256_hash: "hash2",
      file_size_bytes: 1024,
      mime_type: "image/jpeg",
      width: 1920,
      height: 1080,
      capture_view: "front",
      captured_at: new Date().toISOString(),
      is_checkout: false,
    },
  ],
  proposals: [
    {
      id: "prop_01",
      inspection_id: "insp_demo_canvas",
      capture_view: "front",
      bounding_box: { x: 0.25, y: 0.3, width: 0.15, height: 0.1 },
      condition_type: "scratch",
      severity: "moderate",
      confidence: 0.92,
      description: "Deep gouge across top mounting plate",
      model_rationale: "Surface defect detected",
      operator_decision: "pending",
    },
  ],
  kit_checklist: [],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

describe("CompareCanvas Component", () => {
  it("renders reveal mode slider, watermark labels, and proposal hotspots", () => {
    const handleSelectProposal = vi.fn();
    const handleSelectView = vi.fn();

    render(
      <CompareCanvas
        inspection={mockInspection}
        activeView="front"
        onSelectView={handleSelectView}
        selectedProposalId={null}
        onSelectProposal={handleSelectProposal}
      />
    );

    expect(screen.getByText("BASELINE (CHECKOUT)")).toBeInTheDocument();
    expect(screen.getByText("RETURN (CHECK-IN)")).toBeInTheDocument();

    const hotspot = screen.getByRole("button", { name: /Select proposal #1/i });
    expect(hotspot).toBeInTheDocument();

    // Verify normalized coordinates (0.25 -> 25%)
    expect(hotspot).toHaveStyle("left: 25%");
    expect(hotspot).toHaveStyle("top: 30%");
    expect(hotspot).toHaveStyle("width: 15%");
    expect(hotspot).toHaveStyle("height: 10%");

    fireEvent.click(hotspot);
    expect(handleSelectProposal).toHaveBeenCalledWith("prop_01");
  });

  it("supports keyboard control on reveal slider", () => {
    render(
      <CompareCanvas
        inspection={mockInspection}
        activeView="front"
        onSelectView={vi.fn()}
        selectedProposalId={null}
        onSelectProposal={vi.fn()}
      />
    );

    const slider = screen.getByRole("slider", { name: "Comparison Divider Position" });
    expect(slider).toHaveAttribute("aria-valuenow", "50");

    fireEvent.keyDown(slider, { key: "ArrowLeft" });
    expect(slider).toHaveAttribute("aria-valuenow", "45");

    fireEvent.keyDown(slider, { key: "ArrowRight" });
    expect(slider).toHaveAttribute("aria-valuenow", "50");
  });
});
