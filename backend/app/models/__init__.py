from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.sql import func
from ..database import Base

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    target_url = Column(String, nullable=False)
    task = Column(Text, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    stage = Column(String)
    message = Column(Text)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ApplicantProfile(Base):
    __tablename__ = "applicant_profiles"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    phone = Column(String)
    data = Column(JSON)

class ExtractedEvidence(Base):
    __tablename__ = "extracted_evidence"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    source_url = Column(String)
    evidence_type = Column(String)
    content = Column(Text)

class FormField(Base):
    __tablename__ = "form_fields"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    name = Column(String)
    label = Column(String)
    field_type = Column(String)
    proposed_value = Column(String)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    proposed_action = Column(String)
    reason = Column(Text)
    target_url = Column(String)
    affected_fields = Column(JSON)
    status = Column(String, default="pending")

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, nullable=True)
    action = Column(String)
    detail = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
