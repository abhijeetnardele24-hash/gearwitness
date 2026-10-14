import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { KitChecklist } from "../components/KitChecklist";
import { KitItem } from "../types";

const mockItems: KitItem[] = [
  {
    id: "kit_01",
    name: "Sony FX3 Camera Body",
    quantity: 1,
    is_present_checkout: true,
    is_present_checkin: true,
  },
  {
    id: "kit_02",
    name: "USB-C 10Gbps Tether Cable",
    quantity: 1,
    is_present_checkout: true,
    is_present_checkin: false,
  },
];

describe("KitChecklist Component", () => {
  it("renders checklist items with proper status badges and handles toggling", () => {
    const handleToggle = vi.fn();

    render(<KitChecklist items={mockItems} onToggleItem={handleToggle} />);

    expect(screen.getByText("Sony FX3 Camera Body")).toBeInTheDocument();
    expect(screen.getByText("USB-C 10Gbps Tether Cable")).toBeInTheDocument();
    expect(screen.getByText(/✓ Present/i)).toBeInTheDocument();
    expect(screen.getByText(/✕ MISSING/i)).toBeInTheDocument();

    const returnedBtn = screen.getByRole("button", { name: /Mark USB-C 10Gbps Tether Cable as returned/i });
    fireEvent.click(returnedBtn);

    expect(handleToggle).toHaveBeenCalledWith("kit_02", true);
  });
});
