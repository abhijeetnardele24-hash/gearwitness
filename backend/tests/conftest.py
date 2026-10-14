import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.database import repo


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def reset_repo():
    """Resets repository data before test execution."""
    with repo._get_connection() as conn:
        conn.execute("DELETE FROM kit_items")
        conn.execute("DELETE FROM proposals")
        conn.execute("DELETE FROM media")
        conn.execute("DELETE FROM inspections")
        conn.execute("DELETE FROM assets")
        repo._seed_default_data(conn)
    return repo
