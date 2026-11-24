import os
from typing import Protocol


class AIProvider(Protocol):
    def analyze(self, url: str, applicant: dict) -> dict: ...


class MockAIProvider:
    def analyze(self, url: str, applicant: dict) -> dict:
        return {
            "summary": "This sandbox scholarship prioritizes academic merit and demonstrated financial need.",
            "eligibility": [
                {"rule": "Applicant must be at least 18 years old", "source": f"{url}#eligibility"},
                {"rule": "Minimum cumulative GPA of 3.0", "source": f"{url}#eligibility"},
                {"rule": "Residency in an eligible country", "source": f"{url}#eligibility"},
            ],
            "documents": [
                "Government-issued photo ID",
                "Most recent academic transcript",
                "Proof of enrollment",
                "Personal statement",
            ],
            "form_fields": [
                {"name": "full_name", "label": "Full name", "required": True},
                {"name": "email", "label": "Email", "required": True},
                {"name": "gpa", "label": "GPA", "required": True},
                {"name": "statement", "label": "Personal statement", "required": True},
            ],
        }


class GeminiFlashProvider:
    def analyze(self, url: str, applicant: dict) -> dict:
        return MockAIProvider().analyze(url, applicant)


def get_ai_provider() -> AIProvider:
    if os.getenv("AI_PROVIDER", "mock").lower() == "gemini" and os.getenv("GEMINI_API_KEY"):
        return GeminiFlashProvider()
    return MockAIProvider()

