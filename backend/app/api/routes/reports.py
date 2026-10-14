import tempfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from backend.app.models.database import repo
from backend.app.models.schemas import ExportManifest
from backend.app.services.report_generator import (
    generate_export_manifest,
    render_html_report,
    render_pdf_report,
)

router = APIRouter(prefix="/inspections", tags=["Reports & Export"])


@router.get("/{inspection_id}/manifest", response_model=ExportManifest)
def get_manifest(inspection_id: str):
    """Generates a tamper-evident SHA-256 JSON export manifest."""
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return generate_export_manifest(insp)


@router.get("/{inspection_id}/report.html", response_class=HTMLResponse)
def get_html_report(inspection_id: str):
    """Renders a printable HTML inspection report."""
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    manifest = generate_export_manifest(insp)
    return HTMLResponse(content=render_html_report(insp, manifest))


@router.get("/{inspection_id}/report.pdf")
def get_pdf_report(inspection_id: str):
    """Generates and downloads a formal PDF inspection packet."""
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    manifest = generate_export_manifest(insp)

    temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    temp_pdf.close()
    render_pdf_report(insp, manifest, temp_pdf.name)

    return FileResponse(
        temp_pdf.name,
        media_type="application/pdf",
        filename=f"GearWitness_Report_{insp.asset_name.replace(' ', '_')}_{insp.id}.pdf",
    )
