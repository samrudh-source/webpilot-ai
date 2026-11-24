# Architecture

## Components
- **React console:** dashboard, agent workspace, evidence, approval and audit experiences.
- **FastAPI:** validation, workflow state, AI orchestration, browser control and audit APIs.
- **SQLite/SQLAlchemy:** workflows, steps, evidence, profiles, form fields, approvals and events.
- **Playwright:** Chromium navigation, DOM/locator inspection and approved fill operations.
- **Sandbox portal:** local fictional scholarship application.

## Pipeline
1. Goal and target URL are validated.
2. Planner creates bounded stages.
3. Policy gate verifies local URL and blocked action types.
4. Browser engine inspects the page with Chromium.
5. Evidence is persisted and source URLs are recorded.
6. Forms are validated and placed behind approval.
7. Only approved non-sensitive fills may execute.
