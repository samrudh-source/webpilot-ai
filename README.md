# WebPilot AI

WebPilot AI is a simulated, human-controlled browser automation MVP. It discovers eligibility evidence, builds an application document checklist, proposes allowed form fills, records an SQLite audit trail, and blocks submission until the user explicitly approves preparation.

**Tagline:** Find the Rule. Prepare the Form. Keep the Human in Control.

> This repository demonstrates a local scholarship **sandbox**. It is not a live or official scholarship, government, or payment integration.

## Requirements

- Python 3.10+
- Node.js 20+
- Chromium via Playwright for optional real browser inspection

## Quick start

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The sandbox is at `http://localhost:8000/sandbox/scholarship`.

Optional Playwright browser:

```bash
playwright install chromium
```

For Gemini Flash integration, set `AI_PROVIDER=gemini` and `GEMINI_API_KEY` in `.env`. The mock provider is the default and requires no key. The Gemini adapter currently uses the mock-compatible response shape and is a prepared integration point, not a live API call.

## Tests

```bash
pip install -r requirements.txt
pytest -q
cd frontend && npm run build
```

## Architecture

- `frontend/`: React/Vite dashboard, browser viewport, evidence, checklist, approval, and audit panels.
- `backend/main.py`: FastAPI routes and workflow state.
- `backend/database.py`: SQLite workflow and audit storage.
- `backend/ai_service.py`: mock and Gemini Flash provider interface.
- `backend/browser_service.py`: allowlisted form preparation proposals.
- `backend/browser_engine.py`: Playwright persistent Chromium sandbox inspection.
- `backend/security.py`: URL/action validation and sensitive-data masking.

## Safety boundaries

Webpage and AI text is treated as untrusted data. Browser actions are allowlisted, only local sandbox URLs are accessible to browser inspection, passwords and OTP values are masked, and submission, payment, JavaScript execution, CAPTCHA solving, and OTP solving are never automated. Humans must approve preparation and complete challenges themselves.
