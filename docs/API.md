# API

## Core
- `GET /api/health`
- `POST /api/workflows`
- `GET /api/workflows`
- `GET /api/workflows/{workflow_id}`
- `POST /api/workflows/{workflow_id}/start|pause|resume|cancel`

## Intelligence
- `POST /api/analyze-eligibility`
- `POST /api/extract-documents`
- `POST /api/prepare-form`
- `POST /api/validate-form`

## Approval and audit
- `POST /api/approvals`
- `POST /api/approvals/{approval_id}/approve`
- `POST /api/approvals/{approval_id}/reject`
- `POST /api/execute-approved?approval_id=N`
- `GET /api/audit-logs`
