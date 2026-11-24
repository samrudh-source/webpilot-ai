import re

SENSITIVE_FIELDS = {"ssn", "password", "otp", "credit_card", "bank_account"}
ALLOWED_ACTIONS = {"open", "fill", "read", "pause", "approve", "cancel", "resume"}


def mask_sensitive(value):
    if not isinstance(value, dict):
        return value
    masked = {}
    for key, item in value.items():
        if key.lower() in SENSITIVE_FIELDS:
            masked[key] = "***MASKED***"
        elif isinstance(item, dict):
            masked[key] = mask_sensitive(item)
        else:
            masked[key] = item
    return masked


def validate_action(action: str) -> bool:
    return action in ALLOWED_ACTIONS


def validate_url(url: str) -> bool:
    return bool(re.match(r"^https?://", url.strip(), re.I))
