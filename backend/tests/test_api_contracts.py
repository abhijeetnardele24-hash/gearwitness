"""
Contract test suite verifying the exact frontend client API calls:
1. POST /api/v1/inspections/{id}/proposals/{prop_id}/decision -> returns complete Inspection
2. POST /api/v1/inspections/{id}/checklist/{item_id} -> returns complete Inspection
3. POST /api/v1/inspections/{id}/approve -> enforces 0 unresolved proposals and verified checklist items
4. GET /api/v1/reports/{id}/manifest -> returns ExportManifest
5. GET /api/v1/reports/{id}/html -> returns HTML
6. GET /api/v1/reports/{id}/pdf -> returns PDF bytes
"""

from starlette.testclient import TestClient


def test_contract_proposal_decision_post_returns_inspection(client: TestClient, reset_repo):
    insp_id = "insp_hero_demo"
    prop_id = "prop_01_scratch"

    res = client.post(
        f"/api/v1/inspections/{insp_id}/proposals/{prop_id}/decision",
        json={"decision": "confirmed", "notes": "Operator verified deep gouge on top plate"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == insp_id
    assert "proposals" in data
    # Find the target proposal
    prop = next(p for p in data["proposals"] if p["id"] == prop_id)
    assert prop["operator_decision"] == "confirmed"
    assert "Operator verified" in prop["operator_notes"]


def test_contract_checklist_post_returns_inspection(client: TestClient, reset_repo):
    insp_id = "insp_hero_demo"
    item_id = "kit_04"

    res = client.post(
        f"/api/v1/inspections/{insp_id}/checklist/{item_id}",
        json={"is_present_checkin": False},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == insp_id
    assert "kit_checklist" in data
    item = next(i for i in data["kit_checklist"] if i["id"] == item_id)
    assert item["is_present_checkin"] is False


def test_contract_approval_workflow_enforces_preconditions(client: TestClient, reset_repo):
    insp_id = "insp_hero_demo"

    # Step 1: Attempt to approve before resolving proposals
    res_premature = client.post(f"/api/v1/inspections/{insp_id}/approve")
    assert res_premature.status_code == 400
    assert "proposals remain unresolved" in res_premature.json()["detail"]

    # Step 2: Resolve all 3 seeded proposals
    for prop_id, decision in [
        ("prop_01_scratch", "confirmed"),
        ("prop_02_glare", "dismissed"),
        ("prop_03_cable", "confirmed"),
    ]:
        res = client.post(
            f"/api/v1/inspections/{insp_id}/proposals/{prop_id}/decision",
            json={"decision": decision, "notes": f"Resolved as {decision}"},
        )
        assert res.status_code == 200

    # Step 3: Approve now that all proposals are resolved and hero checklist items are verified
    res_approved = client.post(f"/api/v1/inspections/{insp_id}/approve")
    assert res_approved.status_code == 200
    approved_data = res_approved.json()
    assert approved_data["status"] == "approved"


def test_contract_reports_frontend_urls(client: TestClient, reset_repo):
    insp_id = "insp_hero_demo"

    # Manifest
    res_manifest = client.get(f"/api/v1/reports/{insp_id}/manifest")
    assert res_manifest.status_code == 200
    manifest = res_manifest.json()
    assert "manifest_digest_sha256" in manifest
    assert "source_media_hashes" in manifest

    # HTML
    res_html = client.get(f"/api/v1/reports/{insp_id}/html")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert "GearWitness Inspection Report" in res_html.text

    # PDF
    res_pdf = client.get(f"/api/v1/reports/{insp_id}/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF")
