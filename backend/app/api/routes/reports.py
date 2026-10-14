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

reports_router = APIRouter(prefix="/reports", tags=["Reports & Export"])
inspections_reports_router = APIRouter(prefix="/inspections", tags=["Reports & Export (Alias)"])


def _get_manifest_obj(inspection_id: str) -> ExportManifest:
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return generate_export_manifest(insp)


def _get_html_response(inspection_id: str) -> HTMLResponse:
    insp = repo.get_inspection(inspection_id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    manifest = generate_export_manifest(insp)
    return HTMLResponse(content=render_html_report(insp, manifest))


def _get_pdf_response(inspection_id: str) -> FileResponse:
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


# Canonical Routes: /reports/{id}/...
@reports_router.get("/{inspection_id}/manifest", response_model=ExportManifest)
def get_manifest_canonical(inspection_id: str):
    return _get_manifest_obj(inspection_id)


@reports_router.get("/{inspection_id}/html", response_class=HTMLResponse)
def get_html_report_canonical(inspection_id: str):
    return _get_html_response(inspection_id)


@reports_router.get("/{inspection_id}/pdf")
def get_pdf_report_canonical(inspection_id: str):
    return _get_pdf_response(inspection_id)


# Aliases under /inspections/{id}/...
@inspections_reports_router.get("/{inspection_id}/manifest", response_model=ExportManifest)
def get_manifest_alias(inspection_id: str):
    return _get_manifest_obj(inspection_id)


@inspections_reports_router.get("/{inspection_id}/report.html", response_class=HTMLResponse)
def get_html_report_alias1(inspection_id: str):
    return _get_html_response(inspection_id)


@inspections_reports_router.get("/{inspection_id}/html", response_class=HTMLResponse)
def get_html_report_alias2(inspection_id: str):
    return _get_html_response(inspection_id)


@inspections_reports_router.get("/{inspection_id}/report.pdf")
def get_pdf_report_alias1(inspection_id: str):
    return _get_pdf_response(inspection_id)


@inspections_reports_router.get("/{inspection_id}/pdf")
def get_pdf_report_alias2(inspection_id: str):
    return _get_pdf_response(inspection_id)
