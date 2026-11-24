# WebPilot AI

**Find the Rule. Prepare the Form. Keep the Human in Control.**

WebPilot AI is a local AI-powered browser automation MVP for discovering website requirements, extracting evidence, preparing application forms, and requiring human approval before permitted browser actions. Its primary demo is a fictional scholarship portal served locally.

## Implemented status
- React/Vite/TypeScript enterprise dashboard with 12 routed screens
- FastAPI API, SQLite/SQLAlchemy persistence, Pydantic validation
- Playwright/Chromium browser inspection and approved field filling
- Mock AI provider with Gemini API-key integration hook
- Eligibility, document, form preparation and validation services
- Human approval enforcement and audit events
- Local simulated scholarship portal
- Final submission, payment, OTP and CAPTCHA actions remain blocked

## Architecture
`USER GOAL → ORCHESTRATOR → PLANNER → POLICY GATE → BROWSER ENGINE → EVIDENCE/VALIDATION → PERSISTENCE`

## Installation
```bash
cd frontend
npm install
npm run build

cd ../backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m playwright install chromium
```

## Configuration
Copy `.env.example` to `.env`. Never commit `.env`. Gemini is optional; the mock provider is used when `GEMINI_API_KEY` is empty.

## Run
Terminal 1:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`. The sandbox is available at `http://127.0.0.1:8000/sandbox`.

## Tests
```bash
cd backend && pytest -q
cd frontend && npm test
```

## API
See [docs/API.md](docs/API.md). Interactive OpenAPI documentation is at `http://127.0.0.1:8000/docs`.

## Security
See [docs/SECURITY.md](docs/SECURITY.md). Webpage content is treated as untrusted. Public HTTP(S) websites and the local sandbox are supported; private-network targets are blocked, browser actions are allowlisted, and final submissions are not executable.

## Known limitations
- Gemini is represented by a modular mock-first provider; live Gemini calls require future provider implementation.
- Persistent browser contexts and accessibility-tree extraction are scaffolded by Playwright DOM inspection, not a full remote browser session.
- This is a local MVP for a fictional portal, not an official scholarship or government integration.
