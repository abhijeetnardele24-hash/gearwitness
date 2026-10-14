import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceTray } from "../components/EvidenceTray";
import { ChangeProposal } from "../types";

const mockProposals: ChangeProposal[] = [
  {
    id: "prop_01",
    inspection_id: "insp_demo",
    capture_view: "front",
    bounding_box: { x: 0.25, y: 0.3, width: 0.15, height: 0.1 },
    condition_type: "scratch",
    severity: "moderate",
    confidence: 0.92,
    description: "Deep gouge across top mounting plate",
    model_rationale: "High contrast linear surface defect matching physical scratch.",
    operator_decision: "pending",
  },
];

describe("EvidenceTray Component", () => {
  it("renders proposals and handles decision clicks", () => {
    const handleDecide = vi.fn();
    const handleSelect = vi.fn();
    const handleJump = vi.fn();

    render(
      <EvidenceTray
        proposals={mockProposals}
        selectedProposalId={null}
        onSelectProposal={handleSelect}
        onDecideProposal={handleDecide}
        onJumpToView={handleJump}
      />
    );

    expect(screen.getByText(/Deep gouge across top mounting plate/i)).toBeInTheDocument();
    expect(screen.getByText("92%")).toBeInTheDocument();

    const confirmBtn = screen.getByRole("button", { name: /Confirm damage/i });
    fireEvent.click(confirmBtn);

    expect(handleDecide).toHaveBeenCalledWith("prop_01", "confirmed", undefined);
  });
});
