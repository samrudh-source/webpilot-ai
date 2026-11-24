from pydantic import BaseModel, Field, HttpUrl
from typing import Any, Literal

class WorkflowCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    target_url: HttpUrl
    task: str = Field(min_length=3, max_length=2000)

class WorkflowOut(BaseModel):
    id: int
    name: str
    target_url: str
    task: str
    status: str
    created_at: Any
    model_config = {"from_attributes": True}

class EligibilityRequest(BaseModel):
    workflow_id: int
    source_url: str

class DocumentRequest(BaseModel):
    workflow_id: int

class PrepareFormRequest(BaseModel):
    workflow_id: int
    target_url: str

class ValidateFormRequest(BaseModel):
    fields: dict[str, str]

class ApprovalCreate(BaseModel):
    workflow_id: int
    proposed_action: str
    reason: str
    target_url: str
    affected_fields: dict[str, str]

class ApprovalOut(BaseModel):
    id: int
    workflow_id: int
    proposed_action: str
    reason: str
    target_url: str
    affected_fields: dict[str, str]
    status: str
