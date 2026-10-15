import io

from PIL import Image


def test_api_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app_mode"] == "fixture"
    assert data["ollama_connected"] is False
    assert data["model_available"] is False
    assert "Fixture" in data["model_name"]
    assert data["target_model"] == "gemma3:4b"
    assert "version" in data


def test_api_list_assets(client, reset_repo):
    res = client.get("/api/v1/assets")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 2
    assert any(a["name"] == "Sony FX3 Cinema Kit" for a in data)


def test_api_get_asset_detail(client, reset_repo):
    res = client.get("/api/v1/assets/asset_fx3_cinema")
    assert res.status_code == 200
    data = res.json()
    assert data["serial_number"] == "4892011"
    assert len(data["kit_items"]) >= 5


def test_api_get_asset_not_found(client, reset_repo):
    res = client.get("/api/v1/assets/non_existent_id")
    assert res.status_code == 404


def test_api_create_asset(client, reset_repo):
    payload = {
        "name": "DJI Ronin RS3 Pro Gimbal",
        "category": "Stabilizers",
        "serial_number": "RS3-99120",
        "kit_items": [
            {"name": "Gimbal Body", "quantity": 1},
            {"name": "Focus Motor", "quantity": 1},
        ],
    }
    res = client.post("/api/v1/assets", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["name"] == "DJI Ronin RS3 Pro Gimbal"
    assert len(created["kit_items"]) == 2


def test_api_list_and_get_inspections(client, reset_repo):
    res = client.get("/api/v1/inspections")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1

    hero_res = client.get("/api/v1/inspections/insp_hero_demo")
    assert hero_res.status_code == 200
    hero_data = hero_res.json()
    assert hero_data["customer_reference"] == "CUST-7749-BERLIN"
    assert len(hero_data["proposals"]) >= 3


def test_api_get_inspection_not_found(client, reset_repo):
    res = client.get("/api/v1/inspections/non_existent_insp")
    assert res.status_code == 404


def test_api_create_inspection(client, reset_repo):
    payload = {
        "asset_id": "asset_fx3_cinema",
        "customer_reference": "CUST-TEST-99",
        "notes": "Weekend wedding shoot",
    }
    res = client.post("/api/v1/inspections", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["customer_reference"] == "CUST-TEST-99"
    assert created["status"] == "created"


def test_api_create_inspection_invalid_asset(client, reset_repo):
    payload = {
        "asset_id": "invalid_asset_id",
        "customer_reference": "CUST-FAIL",
    }
    res = client.post("/api/v1/inspections", json=payload)
    assert res.status_code == 400


def test_api_upload_media_success(client, reset_repo):
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("test_upload.jpg", buf, "image/jpeg")}
    data = {"capture_view": "front", "is_checkout": "true"}

    res = client.post("/api/v1/inspections/insp_hero_demo/upload", files=files, data=data)
    assert res.status_code == 200
    evidence = res.json()
    assert evidence["mime_type"] == "image/jpeg"
    assert evidence["width"] == 200
    assert evidence["height"] == 200


def test_api_upload_media_invalid_inspection(client, reset_repo):
    img = Image.new("RGB", (100, 100), color=(50, 50, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    files = {"file": ("test.jpg", buf, "image/jpeg")}
    data = {"capture_view": "front", "is_checkout": "true"}
    res = client.post("/api/v1/inspections/invalid_id/upload", files=files, data=data)
    assert res.status_code == 404


def test_api_upload_media_invalid_file_type(client, reset_repo):
    bad_file = io.BytesIO(b"NOT_AN_IMAGE_FILE_DATA")
    files = {"file": ("bad.exe", bad_file, "application/octet-stream")}
    data = {"capture_view": "front", "is_checkout": "true"}
    res = client.post("/api/v1/inspections/insp_hero_demo/upload", files=files, data=data)
    assert res.status_code == 400


def test_api_analyze_inspection_endpoint(client, reset_repo):
    res = client.post("/api/v1/inspections/insp_hero_demo/analyze")
    assert res.status_code == 200
    data = res.json()
    assert len(data["proposals"]) >= 1


def test_api_analyze_inspection_not_found(client, reset_repo):
    res = client.post("/api/v1/inspections/non_existent_id/analyze")
    assert res.status_code == 404


def test_api_review_proposal_decision(client, reset_repo):
    patch_payload = {
        "decision": "confirmed",
        "operator_notes": "Confirmed scratch matches physical return inspection.",
    }
    res = client.patch(
        "/api/v1/inspections/insp_hero_demo/proposals/prop_01_scratch",
        json=patch_payload,
    )
    assert res.status_code == 200
    updated = res.json()
    assert updated["operator_decision"] == "confirmed"
    assert "Confirmed scratch" in updated["operator_notes"]


def test_api_review_proposal_not_found(client, reset_repo):
    res = client.patch(
        "/api/v1/inspections/insp_hero_demo/proposals/non_existent_prop",
        json={"decision": "confirmed"},
    )
    assert res.status_code == 404


def test_api_checklist_item_toggle(client, reset_repo):
    res = client.patch(
        "/api/v1/inspections/insp_hero_demo/checklist/kit_04",
        json={"is_present_checkin": False},
    )
    assert res.status_code == 200
    assert res.json()["is_present_checkin"] is False


def test_api_checklist_item_not_found(client, reset_repo):
    res = client.patch(
        "/api/v1/inspections/insp_hero_demo/checklist/non_existent_item",
        json={"is_present_checkin": False},
    )
    assert res.status_code == 404


def test_api_get_manifest(client, reset_repo):
    res = client.get("/api/v1/inspections/insp_hero_demo/manifest")
    assert res.status_code == 200
    manifest = res.json()
    assert manifest["inspection_id"] == "insp_hero_demo"
    assert "manifest_hash_sha256" in manifest
    assert len(manifest["manifest_hash_sha256"]) == 64


def test_api_get_manifest_not_found(client, reset_repo):
    res = client.get("/api/v1/inspections/non_existent/manifest")
    assert res.status_code == 404


def test_api_get_html_report(client, reset_repo):
    res = client.get("/api/v1/inspections/insp_hero_demo/report.html")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "GearWitness Inspection Evidence Packet" in res.text


def test_api_get_html_report_not_found(client, reset_repo):
    res = client.get("/api/v1/inspections/non_existent/report.html")
    assert res.status_code == 404


def test_api_get_pdf_report(client, reset_repo):
    res = client.get("/api/v1/inspections/insp_hero_demo/report.pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000


def test_api_get_pdf_report_not_found(client, reset_repo):
    res = client.get("/api/v1/inspections/non_existent/report.pdf")
    assert res.status_code == 404
