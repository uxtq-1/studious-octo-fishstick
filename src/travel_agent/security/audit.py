"""Structured security audit events with bounded, redacted metadata."""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

LOGGER = logging.getLogger("travel_agent.security")
SENSITIVE_KEYS = frozenset(
    {"authorization", "cookie", "cvv", "pan", "password", "passport", "secret", "token"}
)


class RiskLevel(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_type: str
    request_id: str
    action: str
    result: str
    risk_level: RiskLevel
    resource_type: str
    resource_id: str
    user_id: str | None = None
    tenant_id: str | None = None
    role: str | None = None
    reason: str | None = None
    timestamp: str = ""


def hash_ip(ip_address: str, *, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{ip_address}".encode()).hexdigest()


def redact_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        key: "[REDACTED]" if any(term in key.lower() for term in SENSITIVE_KEYS) else value
        for key, value in metadata.items()
    }


def write_audit_event(event: AuditEvent, metadata: dict[str, Any] | None = None) -> None:
    payload = asdict(event)
    payload["timestamp"] = event.timestamp or datetime.now(UTC).isoformat()
    payload["metadata"] = redact_metadata(metadata or {})
    LOGGER.info(json.dumps(payload, separators=(",", ":"), sort_keys=True))
