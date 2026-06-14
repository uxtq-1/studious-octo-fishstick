"""Deterministic policy evaluation retained from the prototype concepts."""

from decimal import Decimal

from travel_agent.policy.models import PolicyResult, PolicyViolation, TravelPolicy


def evaluate_trip(
    policy: TravelPolicy,
    *,
    flight_cost: Decimal,
    hotel_nightly_cost: Decimal = Decimal("0"),
    ground_cost: Decimal = Decimal("0"),
    cabin: str = "economy",
) -> PolicyResult:
    values = (flight_cost, hotel_nightly_cost, ground_cost)
    if any(value < 0 for value in values):
        raise ValueError("Travel costs cannot be negative")

    violations: list[PolicyViolation] = []
    checks = (
        ("FLIGHT_PRICE_OVER_LIMIT", flight_cost, policy.flight_max),
        ("HOTEL_NIGHTLY_OVER_LIMIT", hotel_nightly_cost, policy.hotel_nightly_max),
        ("GROUND_PRICE_OVER_LIMIT", ground_cost, policy.ground_transport_max),
    )
    for code, actual, limit in checks:
        if actual > limit:
            violations.append(
                PolicyViolation(
                    code=code,
                    severity="approval_required",
                    actual=actual,
                    limit=limit,
                    currency=policy.currency,
                )
            )

    normalized_cabin = cabin.lower()
    if normalized_cabin not in policy.allowed_cabins:
        violations.append(
            PolicyViolation(
                code="CABIN_NOT_ALLOWED",
                severity="blocking",
                actual=normalized_cabin,
                limit=", ".join(sorted(policy.allowed_cabins)),
            )
        )
    elif normalized_cabin == "business" and policy.business_class_requires_approval:
        violations.append(
            PolicyViolation(
                code="BUSINESS_CLASS_APPROVAL_REQUIRED",
                severity="approval_required",
                actual=normalized_cabin,
            )
        )

    total = sum(values, Decimal("0"))
    if total > policy.trip_max:
        violations.append(
            PolicyViolation(
                code="TRIP_TOTAL_OVER_LIMIT",
                severity="blocking",
                actual=total,
                limit=policy.trip_max,
                currency=policy.currency,
            )
        )
    elif total > policy.approval_threshold:
        violations.append(
            PolicyViolation(
                code="TRIP_APPROVAL_THRESHOLD",
                severity="approval_required",
                actual=total,
                limit=policy.approval_threshold,
                currency=policy.currency,
            )
        )

    blocking = any(item.severity == "blocking" for item in violations)
    approval = any(item.severity == "approval_required" for item in violations)
    return PolicyResult(
        policy_version=policy.version,
        passed=not violations,
        requires_approval=approval and not blocking,
        violations=tuple(violations),
    )
