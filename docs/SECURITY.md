# Security

## Controls
- Pydantic validates API payloads.
- Public HTTP(S) destinations are supported. Private, loopback and link-local network targets are blocked except for the local development sandbox.
- Playwright is instructed with fixed locator strategies rather than AI-generated JavaScript.
- Sensitive actions are rejected by name and include submit, payment, OTP and CAPTCHA.
- Form fills require an approved request.
- Audit events record workflow and browser decisions.
- Environment secrets are excluded from Git and never written to workflow responses.
- Sandboxed webpage text is evidence, never interpreted as instructions.

This MVP does not claim certification, perfect security, or official portal compatibility.
