"""Typed policy and evaluation models."""

from decimal import Decimal

from pydantic import BaseModel, Field


class TravelPolicy(BaseModel):
    version: str
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    flight_max: Decimal = Field(ge=0)
    hotel_nightly_max: Decimal = Field(ge=0)
    ground_transport_max: Decimal = Field(ge=0)
    trip_max: Decimal = Field(ge=0)
    approval_threshold: Decimal = Field(ge=0)
    allowed_cabins: frozenset[str]
    business_class_requires_approval: bool = True


class PolicyViolation(BaseModel):
    code: str
    severity: str
    actual: Decimal | str
    limit: Decimal | str | None = None
    currency: str | None = None


class PolicyResult(BaseModel):
    policy_version: str
    passed: bool
    requires_approval: bool
    violations: tuple[PolicyViolation, ...]
