import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .ai_service import get_ai_provider
from .browser_service import propose_form_fill
from .browser_engine import PlaywrightBrowserEngine
from .database import db_session, init_db
from .security import mask_sensitive, validate_action, validate_url

app = FastAPI(title="WebPilot AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    url: str
    applicant: dict[str, Any] = Field(default_factory=dict)


class PrepareRequest(BaseModel):
    applicant: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    approved: bool


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def audit(db, workflow_id: str | None, action: str, details: dict, source_url: str | None = None, status: str = "completed"):
    db.execute(
        "INSERT INTO audit_logs(workflow_id, action, details, source_url, status, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (workflow_id, action, json.dumps(mask_sensitive(details)), source_url, status, utcnow()),
    )


@app.on_event("startup")
def startup():
    init_db()
    seed()


def seed():
    with db_session() as db:
        exists = db.execute("SELECT 1 FROM workflows LIMIT 1").fetchone()
        if exists:
            return
        now = utcnow()
        db.execute(
            "INSERT INTO workflows(id,title,url,status,applicant,result,created_at,updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("wf-demo-001", "Future Scholars Scholarship", "http://localhost:8000/sandbox/scholarship",
             "ready", json.dumps({"full_name": "Alex Morgan", "email": "alex@example.com", "gpa": "3.7"}),
             json.dumps({"summary": "Sandbox workflow ready for review.", "eligibility": [], "documents": []}),
             now, now),
        )


@app.get("/api/health")
def health():
    return {"status": "healthy", "mode": os.getenv("AI_PROVIDER", "mock")}


@app.get("/api/workflows")
def workflows():
    with db_session() as db:
        rows = db.execute("SELECT * FROM workflows ORDER BY created_at DESC").fetchall()
    return [workflow_json(row) for row in rows]


def workflow_json(row):
    return {
        "id": row["id"], "title": row["title"], "url": row["url"], "status": row["status"],
        "applicant": json.loads(row["applicant"]), "result": json.loads(row["result"]) if row["result"] else None,
        "created_at": row["created_at"], "updated_at": row["updated_at"],
    }


@app.post("/api/discovery/analyze")
def analyze(request: AnalyzeRequest):
    if not validate_url(request.url):
        raise HTTPException(400, "Only HTTP(S) URLs are permitted")
    result = get_ai_provider().analyze(request.url, mask_sensitive(request.applicant))
    workflow_id = f"wf-{uuid.uuid4().hex[:8]}"
    now = utcnow()
    with db_session() as db:
        db.execute(
            "INSERT INTO workflows(id,title,url,status,applicant,result,created_at,updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (workflow_id, "Website Eligibility Review", request.url, "review",
             json.dumps(mask_sensitive(request.applicant)), json.dumps(result), now, now),
        )
        audit(db, workflow_id, "analyze", {"provider": os.getenv("AI_PROVIDER", "mock")}, request.url)
    return {"id": workflow_id, **workflow_json(db_row(workflow_id))}


def db_row(workflow_id: str):
    with db_session() as db:
        row = db.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Workflow not found")
    return row


@app.post("/api/workflows/{workflow_id}/prepare")
def prepare(workflow_id: str, request: PrepareRequest):
    row = db_row(workflow_id)
    proposals = propose_form_fill(request.applicant)
    now = utcnow()
    with db_session() as db:
        db.execute("UPDATE workflows SET status='approval', applicant=?, updated_at=? WHERE id=?",
                   (json.dumps(mask_sensitive(request.applicant)), now, workflow_id))
        audit(db, workflow_id, "prepare", {"proposal_count": len(proposals)}, row["url"], "pending")
    return {"workflow_id": workflow_id, "status": "approval", "proposals": proposals,
            "warning": "No application submission occurs. Human approval is required."}


@app.post("/api/workflows/{workflow_id}/approve")
def approve(workflow_id: str, request: ApprovalRequest):
    if not request.approved:
        raise HTTPException(400, "Approval must be explicitly granted")
    row = db_row(workflow_id)
    with db_session() as db:
        db.execute("UPDATE workflows SET status='paused', updated_at=? WHERE id=?", (utcnow(), workflow_id))
        audit(db, workflow_id, "approve", {"approved": True, "submission": False}, row["url"])
        audit(db, workflow_id, "pause", {"reason": "Human review boundary"}, row["url"])
    return {"workflow_id": workflow_id, "status": "paused",
            "message": "Preparation approved. The application has not been submitted."}


@app.post("/api/workflows/{workflow_id}/{operation}")
def operation(workflow_id: str, operation: str):
    if operation not in {"pause", "resume", "cancel"} or not validate_action(operation):
        raise HTTPException(400, "Unsupported workflow operation")
    status = {"pause": "paused", "resume": "in_progress", "cancel": "cancelled"}[operation]
    row = db_row(workflow_id)
    with db_session() as db:
        db.execute("UPDATE workflows SET status=?, updated_at=? WHERE id=?", (status, utcnow(), workflow_id))
        audit(db, workflow_id, operation, {}, row["url"])
    return {"workflow_id": workflow_id, "status": status}


@app.get("/api/audit")
def audit_logs():
    with db_session() as db:
        rows = db.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 100").fetchall()
    return [dict(row) for row in rows]


@app.get("/api/browser/inspect")
def inspect_browser(url: str = "http://localhost:8000/sandbox/scholarship"):
    if not validate_url(url) or not url.startswith("http://localhost:8000/sandbox/"):
        raise HTTPException(400, "Browser inspection is restricted to the local sandbox")
    try:
        fields = PlaywrightBrowserEngine().inspect_sandbox(url)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    return {"url": url, "fields": fields, "submission_allowed": False}


@app.get("/sandbox/scholarship", response_class=HTMLResponse)
def sandbox():
    return """
    <!doctype html><html lang="en"><head><title>Future Scholars — Sandbox</title>
    <style>body{font-family:system-ui;background:#0b1220;color:#e6edf7;max-width:760px;margin:auto;padding:40px}input,textarea{width:100%;padding:10px;margin:8px 0 18px;background:#111827;color:white;border:1px solid #334155}button{background:#0891b2;color:white;border:0;padding:12px 18px}section{padding:16px 0}</style>
    </head><body><h1>Future Scholars Scholarship</h1><p><strong>SIMULATED PORTAL — NOT AN OFFICIAL APPLICATION</strong></p>
    <section id="eligibility"><h2>Eligibility</h2><ul><li>Applicant must be at least 18 years old</li><li>Minimum cumulative GPA of 3.0</li><li>Residency in an eligible country</li></ul></section>
    <form><label for="full_name">Full name</label><input id="full_name" name="full_name">
    <label for="email">Email</label><input id="email" name="email" type="email">
    <label for="gpa">GPA</label><input id="gpa" name="gpa">
    <label for="statement">Personal statement</label><textarea id="statement" name="statement"></textarea>
    <button type="button" onclick="alert('Submission disabled in sandbox')">Submit (disabled)</button></form></body></html>
    """
