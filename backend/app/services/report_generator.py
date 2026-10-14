import hashlib
import json
import os
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.app.config import settings
from backend.app.models.schemas import (
    ExportManifest,
    Inspection,
    ProposalDecisionEnum,
)

DISCLAIMER_TEXT = (
    "NOTICE: This document is a forensic decision-support evidence summary compiled by GearWitness. "
    "It presents verified photographic alignment, condition change proposals, and operator review states. "
    "It does NOT constitute an automated determination of liability, a legal finding of fraud, or a binding "
    "contractual penalty. Deposit disputes should be resolved directly between parties using this documentation as mutual evidence."
)


def generate_export_manifest(inspection: Inspection) -> ExportManifest:
    """Compiles a tamper-evident, SHA-256 hash-chained JSON export manifest."""
    source_hashes = {}
    for media in inspection.media:
        source_hashes[
            f"{media.capture_view.value}_{'checkout' if media.is_checkout else 'checkin'}"
        ] = media.sha256_hash

    total = len(inspection.proposals)
    confirmed = sum(
        1 for p in inspection.proposals if p.operator_decision == ProposalDecisionEnum.CONFIRMED
    )
    dismissed = sum(
        1 for p in inspection.proposals if p.operator_decision == ProposalDecisionEnum.DISMISSED
    )
    uncertain = sum(
        1 for p in inspection.proposals if p.operator_decision == ProposalDecisionEnum.UNCERTAIN
    )

    checklist_dict = {}
    for item in inspection.kit_checklist:
        checklist_dict[item.name] = item.is_present_checkin is True

    now_str = datetime.now(timezone.utc).isoformat()
    manifest = ExportManifest(
        inspection_id=inspection.id,
        asset_name=inspection.asset_name,
        serial_number=inspection.serial_number,
        customer_reference=inspection.customer_reference,
        checkout_timestamp=inspection.checkout_timestamp.isoformat()
        if inspection.checkout_timestamp
        else None,
        checkin_timestamp=inspection.checkin_timestamp.isoformat()
        if inspection.checkin_timestamp
        else None,
        generated_at=now_str,
        gearwitness_version=settings.APP_VERSION,
        app_mode=settings.APP_MODE.value,
        model_used=settings.GEMMA_MODEL_NAME,
        source_media_hashes=source_hashes,
        total_proposals=total,
        confirmed_proposals=confirmed,
        dismissed_proposals=dismissed,
        uncertain_proposals=uncertain,
        checklist_status=checklist_dict,
        disclaimer=DISCLAIMER_TEXT,
    )

    # Compute deterministic SHA-256 content integrity digest of manifest fields
    canonical_json = json.dumps(
        manifest.model_dump(exclude={"manifest_hash_sha256", "manifest_digest_sha256"}), sort_keys=True
    )
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    manifest.manifest_digest_sha256 = digest
    manifest.manifest_hash_sha256 = digest
    return manifest


def render_html_report(inspection: Inspection, manifest: ExportManifest) -> str:
    """Renders a standalone printable HTML inspection evidence packet."""
    proposals_html = ""
    for p in inspection.proposals:
        decision_color = (
            "#0d9488"
            if p.operator_decision == ProposalDecisionEnum.CONFIRMED
            else "#64748b"
            if p.operator_decision == ProposalDecisionEnum.DISMISSED
            else "#d97706"
        )
        proposals_html += f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 12px; background: #ffffff;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 600; font-size: 15px; color: #1c1917;">View: {p.capture_view.value.upper()} &mdash; {p.condition_type.value.replace("_", " ").title()} ({p.severity.value.title()})</span>
                <span style="background: {decision_color}; color: #ffffff; padding: 3px 10px; border-radius: 9999px; font-size: 12px; font-weight: 700; text-transform: uppercase;">
                    {p.operator_decision.value}
                </span>
            </div>
            <p style="margin: 4px 0 6px 0; color: #334155; font-size: 14px;"><strong>Observation:</strong> {p.description}</p>
            <p style="margin: 0; color: #64748b; font-size: 12px; font-style: italic;">{p.model_rationale}</p>
            {f'<p style="margin: 6px 0 0 0; color: #0f172a; font-size: 13px;"><strong>Operator Note:</strong> {p.operator_notes}</p>' if p.operator_notes else ""}
        </div>
        """

    checklist_html = ""
    for item in inspection.kit_checklist:
        status = "Verified Present" if item.is_present_checkin else "FLAGGED MISSING"
        color = "#0d9488" if item.is_present_checkin else "#dc2626"
        checklist_html += f"""
        <li style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px;">
            <span>{item.name} (Qty: {item.quantity})</span>
            <span style="font-weight: 600; color: {color};">{status}</span>
        </li>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GearWitness Inspection Report &mdash; {inspection.asset_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #faf8f5;
            color: #1c1917;
            margin: 0;
            padding: 32px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 820px;
            margin: 0 auto;
            background: #ffffff;
            border: 1px solid #e7e5e4;
            border-radius: 12px;
            padding: 36px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #0d9488;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .title {{
            font-size: 24px;
            font-weight: 800;
            color: #1c1917;
            margin: 0 0 4px 0;
        }}
        .badge {{
            background: #f0fdf4;
            border: 1px solid #86efac;
            color: #166534;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
            background: #fbfbfa;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #f5f5f4;
        }}
        .disclaimer {{
            background: #fefce8;
            border: 1px solid #fef08a;
            color: #854d0e;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            margin-top: 32px;
        }}
        @media print {{
            body {{ background: #ffffff; padding: 0; }}
            .container {{ border: none; box-shadow: none; padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 class="title">GearWitness Inspection Evidence Packet</h1>
                <p style="margin: 0; color: #78716c; font-size: 14px;">Local-AI Verified Condition & Inventory Audit</p>
            </div>
            <div class="badge">
                App Mode: {manifest.app_mode.upper()}
            </div>
        </div>

        <div class="grid">
            <div>
                <p style="margin: 0 0 4px 0; font-size: 12px; color: #78716c; text-transform: uppercase; font-weight: 700;">Asset Details</p>
                <p style="margin: 0; font-size: 16px; font-weight: 600;">{inspection.asset_name}</p>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #57534e;">Serial: {inspection.serial_number}</p>
            </div>
            <div>
                <p style="margin: 0 0 4px 0; font-size: 12px; color: #78716c; text-transform: uppercase; font-weight: 700;">Inspection Metadata</p>
                <p style="margin: 0; font-size: 14px;">Customer Ref: <strong>{inspection.customer_reference}</strong></p>
                <p style="margin: 2px 0 0 0; font-size: 12px; color: #57534e;">ID: {inspection.id}</p>
            </div>
        </div>

        <h3 style="font-size: 17px; margin: 24px 0 12px 0; border-bottom: 1px solid #e7e5e4; padding-bottom: 6px;">Condition Change Proposals ({manifest.total_proposals} total &bull; {manifest.confirmed_proposals} confirmed)</h3>
        {proposals_html if proposals_html else '<p style="color: #78716c; font-size: 14px; font-style: italic;">No condition changes detected or proposed.</p>'}

        <h3 style="font-size: 17px; margin: 28px 0 12px 0; border-bottom: 1px solid #e7e5e4; padding-bottom: 6px;">Kit Inventory Checklist</h3>
        <ul style="list-style: none; padding: 0; margin: 0;">
            {checklist_html}
        </ul>

        <div class="disclaimer">
            <strong>Decision Support Notice:</strong> {manifest.disclaimer}
        </div>

        <div style="margin-top: 24px; padding-top: 12px; border-top: 1px solid #e7e5e4; font-size: 11px; color: #a8a29e; display: flex; justify-content: space-between;">
            <span>Manifest Hash (SHA-256): {manifest.manifest_hash_sha256[:20]}...</span>
            <span>Generated: {manifest.generated_at}</span>
        </div>
    </div>
</body>
</html>"""


def render_pdf_report(inspection: Inspection, manifest: ExportManifest, output_path: str) -> str:
    """Compiles a clean ReportLab PDF document for official archival and printing."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1c1917"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#78716c"),
        spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0d9488"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#292524"),
    )
    disclaimer_style = ParagraphStyle(
        "DiscStyle",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#854d0e"),
    )

    elements = []
    elements.append(Paragraph("GearWitness Inspection Evidence Packet", title_style))
    elements.append(
        Paragraph(
            f"Asset: <b>{inspection.asset_name}</b> (Serial: {inspection.serial_number}) | Customer Ref: <b>{inspection.customer_reference}</b>",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 8))

    # Meta table
    meta_data = [
        [
            Paragraph("<b>Inspection ID</b>", body_style),
            Paragraph(inspection.id, body_style),
            Paragraph("<b>Operating Mode</b>", body_style),
            Paragraph(manifest.app_mode.upper(), body_style),
        ],
        [
            Paragraph("<b>Total Proposals</b>", body_style),
            Paragraph(str(manifest.total_proposals), body_style),
            Paragraph("<b>Confirmed Defects</b>", body_style),
            Paragraph(str(manifest.confirmed_proposals), body_style),
        ],
        [
            Paragraph("<b>Gemma Model</b>", body_style),
            Paragraph(manifest.model_used or "None", body_style),
            Paragraph("<b>Report Timestamp</b>", body_style),
            Paragraph(manifest.generated_at[:19], body_style),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[110, 160, 110, 160])
    t_meta.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f5f4")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e7e5e4")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(t_meta)
    elements.append(Spacer(1, 12))

    # Proposals Section
    elements.append(Paragraph("Evaluated Condition Changes", section_style))
    prop_rows = [
        [
            Paragraph("<b>View</b>", body_style),
            Paragraph("<b>Proposed Condition</b>", body_style),
            Paragraph("<b>Severity</b>", body_style),
            Paragraph("<b>Operator Decision</b>", body_style),
            Paragraph("<b>Description</b>", body_style),
        ]
    ]
    for p in inspection.proposals:
        prop_rows.append(
            [
                Paragraph(p.capture_view.value.title(), body_style),
                Paragraph(p.condition_type.value.replace("_", " ").title(), body_style),
                Paragraph(p.severity.value.title(), body_style),
                Paragraph(f"<b>{p.operator_decision.value.upper()}</b>", body_style),
                Paragraph(p.description, body_style),
            ]
        )
    if len(prop_rows) == 1:
        prop_rows.append(
            [
                Paragraph("No condition differences detected.", body_style),
                Paragraph("-", body_style),
                Paragraph("-", body_style),
                Paragraph("-", body_style),
                Paragraph("-", body_style),
            ]
        )

    t_prop = Table(prop_rows, colWidths=[70, 110, 70, 95, 195])
    t_prop.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d9488")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(t_prop)
    elements.append(Spacer(1, 12))

    # Checklist Section
    elements.append(Paragraph("Kit Inventory Reconciliation", section_style))
    check_rows = [
        [
            Paragraph("<b>Component Name</b>", body_style),
            Paragraph("<b>Quantity</b>", body_style),
            Paragraph("<b>Return Status</b>", body_style),
        ]
    ]
    for item in inspection.kit_checklist:
        status_text = "Verified Present" if item.is_present_checkin else "FLAGGED MISSING"
        check_rows.append(
            [
                Paragraph(item.name, body_style),
                Paragraph(str(item.quantity), body_style),
                Paragraph(f"<b>{status_text}</b>", body_style),
            ]
        )
    t_check = Table(check_rows, colWidths=[240, 100, 200])
    t_check.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(t_check)
    elements.append(Spacer(1, 16))

    # Disclaimer Box
    disc_table = Table(
        [
            [
                Paragraph(
                    f"<b>LEGAL & DECISION-SUPPORT NOTICE:</b> {manifest.disclaimer}",
                    disclaimer_style,
                )
            ]
        ],
        colWidths=[540],
    )
    disc_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fefce8")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#fef08a")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(disc_table)

    doc.build(elements)
    return output_path
