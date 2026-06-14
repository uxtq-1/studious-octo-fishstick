"""Provider webhook signature and replay validation."""

import hashlib
import hmac
import time
from collections.abc import MutableSet


class InvalidWebhook(ValueError):
    pass


def verify_hmac_webhook(
    *,
    body: bytes,
    signature: str,
    timestamp: int,
    secret: bytes,
    now: int | None = None,
    tolerance_seconds: int = 300,
) -> None:
    current_time = int(time.time()) if now is None else now
    if abs(current_time - timestamp) > tolerance_seconds:
        raise InvalidWebhook("Webhook timestamp is outside the allowed window")
    signed_payload = str(timestamp).encode() + b"." + body
    expected = hmac.new(secret, signed_payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise InvalidWebhook("Webhook signature is invalid")


def claim_webhook_event(event_id: str, processed_event_ids: MutableSet[str]) -> None:
    """Atomically claim an event in a persistence adapter.

    The set is suitable for tests and a single process. Production adapters
    must implement the same add-if-absent behavior with durable storage and a
    uniqueness constraint.
    """

    normalized_id = event_id.strip()
    if not normalized_id or len(normalized_id) > 256:
        raise InvalidWebhook("Webhook event ID is invalid")
    if normalized_id in processed_event_ids:
        raise InvalidWebhook("Webhook event was already processed")
    processed_event_ids.add(normalized_id)
