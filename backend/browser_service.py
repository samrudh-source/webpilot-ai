from dataclasses import dataclass

ALLOWED_FIELDS = {"full_name", "email", "gpa", "statement"}


@dataclass
class BrowserProposal:
    action: str
    field: str
    value: str


def propose_form_fill(applicant: dict) -> list[dict]:
    source = {
        "full_name": applicant.get("full_name", ""),
        "email": applicant.get("email", ""),
        "gpa": applicant.get("gpa", ""),
        "statement": applicant.get("statement", ""),
    }
    return [
        BrowserProposal("fill", field, value).__dict__
        for field, value in source.items()
        if field in ALLOWED_FIELDS and value
    ]

