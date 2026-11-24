import os
import tempfile

import pytest
from fastapi.testclient import TestClient

os.chdir(tempfile.mkdtemp())

from backend.database import DB_PATH, init_db
from backend.main import app
from backend.security import mask_sensitive, validate_action, validate_url
from backend.browser_service import propose_form_fill


@pytest.fixture
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_discovery_and_prepare_requires_approval(client):
    analyzed = client.post("/api/discovery/analyze", json={
        "url": "http://localhost:8000/sandbox/scholarship",
        "applicant": {"full_name": "Alex Morgan", "email": "alex@example.com", "gpa": "3.7"},
    })
    assert analyzed.status_code == 200
    workflow_id = analyzed.json()["id"]
    assert analyzed.json()["result"]["eligibility"]

    prepared = client.post(f"/api/workflows/{workflow_id}/prepare", json={
        "applicant": {"full_name": "Alex Morgan", "email": "alex@example.com", "gpa": "3.7"}
    })
    assert prepared.status_code == 200
    assert prepared.json()["proposals"]
    assert "submission" in prepared.json()["warning"]


def test_reject_external_url_and_action():
    assert not validate_url("javascript:alert(1)")
    assert validate_url("https://example.com")
    assert not validate_action("submit")
    assert validate_action("fill")


def test_sensitive_values_are_masked():
    masked = mask_sensitive({"name": "Alex", "otp": "123456", "password": "secret"})
    assert masked["name"] == "Alex"
    assert masked["otp"] == "***MASKED***"
    assert masked["password"] == "***MASKED***"


def test_only_allowlisted_fields_are_proposed():
    proposals = propose_form_fill({
        "full_name": "Alex",
        "password": "secret",
        "email": "alex@example.com",
    })
    assert {item["field"] for item in proposals} == {"full_name", "email"}
