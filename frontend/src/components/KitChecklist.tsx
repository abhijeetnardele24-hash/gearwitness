import React from "react";
import { KitItem } from "../types";

interface KitChecklistProps {
  items: KitItem[];
  onToggleItem: (itemId: string, isPresent: boolean) => void;
}

export const KitChecklist: React.FC<KitChecklistProps> = ({ items, onToggleItem }) => {
  const missingCount = items.filter(
    (item) => item.is_present_checkin === false
  ).length;
  const verifiedCount = items.filter(
    (item) => item.is_present_checkin === true
  ).length;

  return (
    <section className="kit-checklist-section" aria-label="Kit Inventory & Accessory Checklist">
      <div className="checklist-header">
        <div>
          <h2 className="section-title">Kit Inventory Checklist</h2>
          <span className="checklist-subtitle">
            {verifiedCount} of {items.length} returned · {missingCount} missing
          </span>
        </div>
      </div>

      <div className="checklist-items-table" role="table" aria-label="Kit items">
        <div className="table-header-row" role="row">
          <div className="col-item" role="columnheader">Item Name</div>
          <div className="col-qty" role="columnheader">Qty</div>
          <div className="col-serial" role="columnheader">Serial / Part #</div>
          <div className="col-status" role="columnheader">Return Status</div>
          <div className="col-action" role="columnheader">Action</div>
        </div>

        {items.map((item) => {
          const isMissing = item.is_present_checkin === false;
          const isPresent = item.is_present_checkin === true;
          const isUnchecked = item.is_present_checkin === null || item.is_present_checkin === undefined;

          return (
            <div
              key={item.id}
              className={`table-row ${isMissing ? "item-missing" : isPresent ? "item-present" : ""}`}
              role="row"
              id={`kit-row-${item.id}`}
            >
              <div className="col-item" role="cell">
                <span className="item-name">{item.name}</span>
                {item.description && (
                  <span className="item-desc text-muted">{item.description}</span>
                )}
              </div>

              <div className="col-qty font-mono" role="cell">
                x{item.quantity}
              </div>

              <div className="col-serial font-mono text-muted" role="cell">
                {item.serial_or_part_no || "—"}
              </div>

              <div className="col-status" role="cell">
                {isPresent && (
                  <span className="badge-pill pill-present">✓ Present</span>
                )}
                {isMissing && (
                  <span className="badge-pill pill-missing">✕ MISSING</span>
                )}
                {isUnchecked && (
                  <span className="badge-pill pill-pending">○ Unverified</span>
                )}
              </div>

              <div className="col-action" role="cell">
                <div className="toggle-btn-group">
                  <button
                    className={`btn-toggle ${isPresent ? "selected-present" : ""}`}
                    onClick={() => onToggleItem(item.id, true)}
                    title="Mark Returned"
                    aria-label={`Mark ${item.name} as returned`}
                    id={`toggle-present-${item.id}`}
                  >
                    Returned
                  </button>
                  <button
                    className={`btn-toggle ${isMissing ? "selected-missing" : ""}`}
                    onClick={() => onToggleItem(item.id, false)}
                    title="Mark Missing"
                    aria-label={`Mark ${item.name} as missing`}
                    id={`toggle-missing-${item.id}`}
                  >
                    Missing
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
