"""PCI-scoped payment metadata models.

Only provider-tokenized references are accepted. Cardholder data belongs in
the payment provider's hosted interface and never in this application.
"""

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import Field, ValidationInfo, field_validator

from travel_agent.security.validation import StrictRequestModel


class PaymentStatus(StrEnum):
    PENDING = "pending"
    REQUIRES_ACTION = "requires_action"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefundStatus(StrEnum):
    NOT_REQUESTED = "not_requested"
    REQUESTED = "requested"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ChargebackStatus(StrEnum):
    NONE = "none"
    OPEN = "open"
    WON = "won"
    LOST = "lost"


class PaymentRecord(StrictRequestModel):
    payment_id: str = Field(min_length=1, max_length=128)
    provider: str = Field(min_length=1, max_length=64)
    provider_reference: str = Field(min_length=1, max_length=256)
    payment_status: PaymentStatus
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    tenant_id: str = Field(min_length=1, max_length=128)
    booking_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    created_at: datetime
    updated_at: datetime
    refund_status: RefundStatus = RefundStatus.NOT_REQUESTED
    chargeback_status: ChargebackStatus = ChargebackStatus.NONE

    @field_validator("updated_at")
    @classmethod
    def updated_at_cannot_precede_creation(cls, value: datetime, info: ValidationInfo) -> datetime:
        created_at = info.data.get("created_at")
        if created_at and value < created_at:
            raise ValueError("updated_at cannot precede created_at")
        return value
