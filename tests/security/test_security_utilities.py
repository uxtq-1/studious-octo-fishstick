import hashlib
import hmac
import json
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from travel_agent.security.audit import AuditEvent, RiskLevel, redact_metadata
from travel_agent.security.payments import PaymentRecord, PaymentStatus
from travel_agent.security.ssrf import UnsafeOutboundUrl, validate_outbound_url
from travel_agent.security.validation import SafeTextRequest, reject_sensitive_payment_fields
from travel_agent.security.webhooks import (
    InvalidWebhook,
    claim_webhook_event,
    verify_hmac_webhook,
)


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


@pytest.mark.parametrize(
    "message",
    [
        "<script>alert(1)</script>",
        "1 UNION SELECT password FROM users",
        "$(curl https://example.test)",
        "{{ config.items() }}",
    ],
)
def test_suspicious_input_is_rejected(message):
    with pytest.raises(ValidationError):
        SafeTextRequest(message=message)


def test_strict_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        SafeTextRequest(message="A normal support request", unexpected="not allowed")


def test_raw_card_fields_are_rejected():
    with pytest.raises(ValueError, match="Sensitive payment data"):
        reject_sensitive_payment_fields({"cardNumber": "4111111111111111"})


def test_payment_record_accepts_only_tokenized_metadata():
    now = datetime.now(UTC)
    record = PaymentRecord(
        payment_id="pay-1",
        provider="hosted-provider",
        provider_reference="provider-token-reference",
        payment_status=PaymentStatus.PENDING,
        amount=Decimal("125.50"),
        currency="USD",
        tenant_id="tenant-1",
        booking_id="booking-1",
        user_id="user-1",
        created_at=now,
        updated_at=now,
    )
    assert record.amount == Decimal("125.50")
    with pytest.raises(ValidationError):
        PaymentRecord(**record.model_dump(), cvv="123")


def test_duplicate_webhook_event_is_rejected():
    processed_events: set[str] = set()
    claim_webhook_event("event-1", processed_events)
    with pytest.raises(InvalidWebhook, match="already processed"):
        claim_webhook_event("event-1", processed_events)
