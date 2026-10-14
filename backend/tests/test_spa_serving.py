from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_spa_root_serves_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "GearWitness" in res.text

def test_spa_client_side_route_serves_html():
    res = client.get("/inspections/insp_hero_demo")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "GearWitness" in res.text

def test_spa_unknown_api_returns_404():
    res = client.get("/api/v1/nonexistent_route")
    assert res.status_code == 404
