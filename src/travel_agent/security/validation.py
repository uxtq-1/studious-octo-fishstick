"""Strict API schemas and conservative input validation helpers."""

import re
import unicodedata
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

INJECTION_PATTERNS = (
    re.compile(r"<\s*(?:script|iframe|object|embed)\b", re.IGNORECASE),
    re.compile(r"\b(?:union\s+select|drop\s+table|insert\s+into)\b", re.IGNORECASE),
    re.compile(r"(?:\$\(|`[^`]*`|;\s*(?:cat|curl|wget|sh|bash)\b)", re.IGNORECASE),
    re.compile(r"(?:\{\{|\{%|<%)[\s\S]*(?:\}\}|%\}|%>)"),
)


class StrictRequestModel(BaseModel):
    """Base for API payloads that rejects undeclared fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def normalize_text(value: str, *, max_length: int = 2_000) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    if not normalized or len(normalized) > max_length:
        raise ValueError("Invalid request")
    if any(pattern.search(normalized) for pattern in INJECTION_PATTERNS):
        raise ValueError("Invalid request")
    return normalized


def reject_sensitive_payment_fields(payload: dict[str, Any]) -> None:
    """Reject cardholder data before it can enter application persistence."""

    prohibited_fragments = (
        "cardnumber",
        "card_number",
        "pan",
        "cvv",
        "cvc",
        "magneticstripe",
        "trackdata",
    )
    for key in payload:
        normalized_key = key.replace("-", "").lower()
        if any(fragment in normalized_key for fragment in prohibited_fragments):
            raise ValueError("Sensitive payment data is not accepted")


class SafeTextRequest(StrictRequestModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        return normalize_text(value)
