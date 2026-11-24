from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pathlib import Path

from .database import Base, engine, get_db
from .models import Workflow, WorkflowStep, ApplicantProfile, ExtractedEvidence, FormField, ApprovalRequest, AuditEvent
from .schemas import *
from .services.ai_provider import ai_provider
from .services.browser_engine import browser_engine
from .config import settings

Base.metadata.create_all(bind=engine)
app = FastAPI(title="WebPilot AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def audit(db: Session, workflow_id: int | None, action: str, detail: str):
    db.add(AuditEvent(workflow_id=workflow_id, action=action, detail=detail))
    db.commit()

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "WebPilot AI",
        "database": "connected",
        "ai_provider": "gemini" if settings.gemini_api_key else "mock",
    }

@app.post("/api/workflows", response_model=WorkflowOut)
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)):
    if not browser_engine.validate_url(str(payload.target_url)):
        raise HTTPException(400, "Target URL must use HTTP(S) and resolve to a public host")
    wf = Workflow(name=payload.name, target_url=str(payload.target_url), task=payload.task)
    db.add(wf); db.commit(); db.refresh(wf)
    audit(db, wf.id, "workflow_created", f"Created workflow for {wf.target_url}")
    return wf

@app.get("/api/workflows")
def list_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).order_by(Workflow.created_at.desc(), Workflow.id.desc()).all()

@app.get("/api/workflows/{workflow_id}")
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, "Workflow not found")
    steps = db.query(WorkflowStep).filter(WorkflowStep.workflow_id == workflow_id).all()
    return {"workflow": wf, "steps": steps}

def set_status(workflow_id: int, status: str, db: Session):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf: raise HTTPException(404, "Workflow not found")
    wf.status = status
    db.add(wf); db.commit(); db.refresh(wf)
    audit(db, wf.id, f"workflow_{status}", f"Workflow status changed to {status}")
    return wf

@app.post("/api/workflows/{workflow_id}/start")
def start(workflow_id: int, db: Session = Depends(get_db)):
    wf = set_status(workflow_id, "running", db)
    plan = ai_provider.analyze(wf.task)
    for stage in plan["steps"]:
        db.add(WorkflowStep(workflow_id=wf.id, stage="planner", message=stage, status="completed"))
    db.commit()
    try:
        evidence = browser_engine.inspect(wf.target_url)
    except Exception as exc:
        wf.status = "paused"; db.commit()
        audit(db, wf.id, "browser_error", str(exc))
        raise HTTPException(502, f"Browser inspection failed: {exc}")
    db.add(ExtractedEvidence(workflow_id=wf.id, source_url=evidence["url"], evidence_type="page_snapshot", content=evidence["text"]))
    db.commit()
    audit(db, wf.id, "browser_inspected", f"Inspected {evidence['url']}")
    return {"workflow": wf, "plan": plan, "evidence": evidence}

@app.post("/api/workflows/{workflow_id}/pause")
def pause(workflow_id: int, db: Session = Depends(get_db)): return set_status(workflow_id, "paused", db)
@app.post("/api/workflows/{workflow_id}/resume")
def resume(workflow_id: int, db: Session = Depends(get_db)): return set_status(workflow_id, "running", db)
@app.post("/api/workflows/{workflow_id}/cancel")
def cancel(workflow_id: int, db: Session = Depends(get_db)): return set_status(workflow_id, "cancelled", db)

@app.post("/api/analyze-eligibility")
def analyze_eligibility(payload: EligibilityRequest, db: Session = Depends(get_db)):
    if not browser_engine.validate_url(payload.source_url): raise HTTPException(400, "Source URL is not allowlisted")
    if "127.0.0.1:8000/sandbox" in payload.source_url:
        result = {
            "eligible": True,
            "requirements": ["Resident of Karnataka", "Aged 18–25", "Enrolled in a recognised Indian institution", "Family income within the declared scheme limit", "Minimum 60% aggregate or equivalent", "Active application period"],
            "source_url": payload.source_url,
        }
    else:
        result = {
            "eligible": None,
            "requirements": ["Target content inspected", "Explicit eligibility rules require human review", "Source URL recorded for evidence"],
            "source_url": payload.source_url,
        }
    db.add(ExtractedEvidence(workflow_id=payload.workflow_id, source_url=payload.source_url, evidence_type="eligibility", content=str(result)))
    db.commit(); audit(db, payload.workflow_id, "eligibility_analyzed", "Eligibility requirements extracted")
    return result

@app.post("/api/extract-documents")
def extract_documents(payload: DocumentRequest, db: Session = Depends(get_db)):
    documents = ["Aadhaar Card", "Income certificate", "SSLC / PUC or degree marks card", "Caste / category certificate, if applicable", "Two recommendation letters", "Study or personal statement"]
    audit(db, payload.workflow_id, "documents_extracted", "Document checklist generated")
    return {"documents": documents, "count": len(documents)}

@app.post("/api/prepare-form")
def prepare_form(payload: PrepareFormRequest, db: Session = Depends(get_db)):
    values = {"full_name": "Aarav Kumar", "email": "aarav.kumar@example.in", "mobile": "+91 98765 43210", "district": "Bengaluru Urban", "institution": "Fictional Karnataka Institute of Technology", "percentage": "82.5", "study_area": "Computer Science"}
    for name, value in values.items():
        db.add(FormField(workflow_id=payload.workflow_id, name=name, label=name.replace("_", " ").title(), field_type="text", proposed_value=value))
    db.commit(); audit(db, payload.workflow_id, "form_prepared", "Fictional applicant values prepared")
    return {"fields": [{"name": k, "label": k.replace("_"," ").title(), "value": v} for k, v in values.items()], "source_url": payload.target_url}

@app.post("/api/validate-form")
def validate_form(payload: ValidateFormRequest):
    errors = {}
    if not payload.fields.get("full_name"): errors["full_name"] = "Full name is required"
    if "@" not in payload.fields.get("email", ""): errors["email"] = "Valid email is required"
    mobile = payload.fields.get("mobile", "")
    if mobile and not (mobile.startswith("+91") and len(mobile.replace(" ", "").replace("-", "")) >= 13):
        errors["mobile"] = "Mobile number must use the +91 country code"
    try:
        percentage = float(payload.fields.get("percentage", ""))
        if not 0 <= percentage <= 100: errors["percentage"] = "Percentage must be between 0 and 100"
    except ValueError: errors["percentage"] = "Percentage must be numeric"
    return {"valid": not errors, "errors": errors}

@app.post("/api/approvals", response_model=ApprovalOut)
def create_approval(payload: ApprovalCreate, db: Session = Depends(get_db)):
    if not browser_engine.validate_url(payload.target_url): raise HTTPException(400, "Target URL is not allowlisted")
    req = ApprovalRequest(workflow_id=payload.workflow_id, proposed_action=payload.proposed_action, reason=payload.reason, target_url=payload.target_url, affected_fields=payload.affected_fields)
    db.add(req); db.commit(); db.refresh(req)
    audit(db, payload.workflow_id, "approval_requested", payload.proposed_action)
    return req

@app.get("/api/approvals", response_model=list[ApprovalOut])
def list_approvals(db: Session = Depends(get_db)):
    return db.query(ApprovalRequest).order_by(ApprovalRequest.id.desc()).all()

@app.post("/api/approvals/{approval_id}/approve")
def approve(approval_id: int, db: Session = Depends(get_db)):
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not req: raise HTTPException(404, "Approval request not found")
    req.status = "approved"; db.commit()
    return {"approved": True, "approval_id": approval_id}

@app.post("/api/approvals/{approval_id}/reject")
def reject(approval_id: int, db: Session = Depends(get_db)):
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not req: raise HTTPException(404, "Approval request not found")
    req.status = "rejected"; db.commit()
    return {"approved": False, "approval_id": approval_id}

@app.post("/api/execute-approved")
def execute_approved(approval_id: int, db: Session = Depends(get_db)):
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not req: raise HTTPException(404, "Approval request not found")
    if req.status != "approved": raise HTTPException(409, "Approval required before browser execution")
    action = req.proposed_action.lower()
    if any(word in action for word in ("submit", "payment", "otp", "captcha")):
        raise HTTPException(403, "This sensitive action requires direct human control")
    try:
        result = browser_engine.fill_fields(req.target_url, req.affected_fields)
    except Exception as exc: raise HTTPException(502, str(exc))
    audit(db, req.workflow_id, "approved_fill_executed", str(result))
    return result

@app.get("/api/audit-logs")
def audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(200).all()

sandbox = Path(__file__).resolve().parents[2] / "sandbox-portal"
app.mount("/sandbox", StaticFiles(directory=str(sandbox), html=True), name="sandbox")
