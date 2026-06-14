import hashlib
import hmac
import json

import pytest

from travel_agent.security.audit import AuditEvent, RiskLevel, redact_metadata
from travel_agent.security.ssrf import UnsafeOutboundUrl, validate_outbound_url
from travel_agent.security.webhooks import InvalidWebhook, verify_hmac_webhook


def _resolver_with(address: str):
    def resolve(*_args, **_kwargs):
        return [(2, 1, 6, "", (address, 443))]

    return resolve


@pytest.mark.parametrize(
    "url",
    [
        "http://api.example.test/resource",
        "https://127.0.0.1/resource",
        "https://metadata.google.internal/resource",
        "file:///etc/passwd",
    ],
)
def test_ssrf_guard_rejects_unapproved_urls(url):
    with pytest.raises(UnsafeOutboundUrl):
        validate_outbound_url(
            url,
            allowed_hosts={"api.example.test"},
            resolver=_resolver_with("93.184.216.34"),
        )


def test_ssrf_guard_rejects_private_resolved_address():
    with pytest.raises(UnsafeOutboundUrl):
        validate_outbound_url(
            "https://api.example.test/resource",
            allowed_hosts={"api.example.test"},
            resolver=_resolver_with("10.0.0.2"),
        )


def test_webhook_requires_valid_signature_and_recent_timestamp():
    body = b'{"event":"payment.completed"}'
    secret = b"test-secret"
    timestamp = 1_700_000_000
    signature = hmac.new(
        secret,
        str(timestamp).encode() + b"." + body,
        hashlib.sha256,
    ).hexdigest()

    verify_hmac_webhook(
        body=body,
        signature=signature,
        timestamp=timestamp,
        secret=secret,
        now=timestamp + 30,
    )
    with pytest.raises(InvalidWebhook):
        verify_hmac_webhook(
            body=body,
            signature="invalid",
            timestamp=timestamp,
            secret=secret,
            now=timestamp,
        )


def test_audit_metadata_redacts_sensitive_fields():
    event = AuditEvent(
        event_type="payment_started",
        request_id="request-1",
        action="start",
        result="allowed",
        risk_level=RiskLevel.INFO,
        resource_type="payment",
        resource_id="payment-1",
    )
    assert json.loads(json.dumps(event.event_type)) == "payment_started"
    assert redact_metadata({"token": "secret", "providerReference": "safe"}) == {
        "token": "[REDACTED]",
        "providerReference": "safe",
    }
