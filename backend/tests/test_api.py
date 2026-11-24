from fastapi.testclient import TestClient
from app.main import app
from app.services.browser_engine import browser_engine

client = TestClient(app)

def test_health():
    assert client.get("/api/health").json()["status"] == "healthy"

def test_workflow_creation():
    r = client.post("/api/workflows", json={"name":"Test scholarship","target_url":"http://127.0.0.1:8000/sandbox","task":"Prepare the fictional scholarship application"})
    assert r.status_code == 200
    assert r.json()["status"] == "pending"

def test_eligibility():
    r = client.post("/api/analyze-eligibility", json={"workflow_id":1,"source_url":"http://127.0.0.1:8000/sandbox"})
    assert r.status_code == 200
    assert r.json()["source_url"].endswith("/sandbox")

def test_form_validation():
    r = client.post("/api/validate-form", json={"fields":{"full_name":"Aarav Kumar","email":"aarav@example.in","mobile":"+91 98765 43210","percentage":"82.5"}})
    assert r.json()["valid"] is True

def test_approval_required():
    r = client.post("/api/execute-approved", params={"approval_id":999})
    assert r.status_code == 404

def test_url_allowlist():
    assert browser_engine.validate_url("http://127.0.0.1:8000/sandbox")
    assert browser_engine.validate_url("https://example.com")
    assert not browser_engine.validate_url("http://192.168.1.10")
