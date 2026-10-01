"""Shared pytest fixtures for all tests.

Uses an in-memory SQLite database so tests run without a real PostgreSQL instance.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

# ---------------------------------------------------------------------------
# In-memory SQLite for tests (no Postgres needed for CI)
# ---------------------------------------------------------------------------
SQLITE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create fresh tables for each test, drop after."""
    import app.models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db):
    """Test client with DB override."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def registered_user(client):
    """Create and return a user dict with token."""
    resp = client.post("/auth/signup", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepass123",
    })
    assert resp.status_code == 201

    login = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "securepass123",
    })
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"user": resp.json(), "token": token, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture()
def centre_and_test(client):
    """Create a diagnostic centre and test, return their IDs."""
    centre_resp = client.post("/centres", json={
        "name": "City Diagnostics",
        "location": "Mumbai, MH",
    })
    assert centre_resp.status_code == 201
    centre = centre_resp.json()

    test_resp = client.post("/tests", json={
        "centre_id": centre["id"],
        "name": "Complete Blood Count",
        "description": "Full CBC panel",
        "price": "750.00",
    })
    assert test_resp.status_code == 201
    test = test_resp.json()

    return {"centre": centre, "test": test}
