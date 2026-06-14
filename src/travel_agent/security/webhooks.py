"""Provider webhook signature and replay validation."""

import hashlib
import hmac
import time


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
