import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { GuidedCaptureModal } from "../components/GuidedCaptureModal";

describe("GuidedCaptureModal Component", () => {
  it("renders 5-point capture angles and instructions", () => {
    render(
      <GuidedCaptureModal
        inspectionId="insp_demo"
        isOpen={true}
        onClose={vi.fn()}
        onInspectionUpdated={vi.fn()}
      />
    );

    expect(screen.getByText("Standard 5-Point Return Capture Guide")).toBeInTheDocument();
    expect(screen.getAllByText(/1\. Front Mount & Controls/i)[0]).toBeInTheDocument();
    expect(screen.getByText(/2\. Back Display & Articulation/i)).toBeInTheDocument();
    expect(screen.getByText(/3\. Top Plate & Hotshoe/i)).toBeInTheDocument();
    expect(screen.getByText(/4\. Accessories & Kit Layout/i)).toBeInTheDocument();
    expect(screen.getByText(/5\. Detail \/ Macro Close-Up/i)).toBeInTheDocument();
  });

  it("handles phase switching and angle selection", () => {
    render(
      <GuidedCaptureModal
        inspectionId="insp_demo"
        isOpen={true}
        onClose={vi.fn()}
        onInspectionUpdated={vi.fn()}
      />
    );

    const baselineBtn = screen.getByRole("button", { name: /1\. Baseline Checkout/i });
    fireEvent.click(baselineBtn);
    expect(baselineBtn).toHaveClass("btn-primary");

    const backStep = screen.getByRole("tab", { name: /2\. Back Display/i });
    fireEvent.click(backStep);
    expect(screen.getByText("Angle ID: back")).toBeInTheDocument();
  });

  it("rejects non-image files with clear error banner", async () => {
    render(
      <GuidedCaptureModal
        inspectionId="insp_demo"
        isOpen={true}
        onClose={vi.fn()}
        onInspectionUpdated={vi.fn()}
      />
    );

    const fileInput = document.getElementById("capture-file-input") as HTMLInputElement;
    const maliciousFile = new File(["malicious binary"], "bad.exe", { type: "application/x-msdownload" });

    fireEvent.change(fileInput, { target: { files: [maliciousFile] } });

    await waitFor(() => {
      expect(screen.getByText(/Please select a valid image file/i)).toBeInTheDocument();
    });
  });
});
