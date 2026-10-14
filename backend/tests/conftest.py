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
    repo.assets.clear()
    repo.inspections.clear()
    repo._seed_default_data()
    return repo
