from decimal import Decimal
from pathlib import Path

import pytest

from travel_agent.policy.engine import evaluate_trip
from travel_agent.policy.loader import load_policy


@pytest.fixture
def policy():
    return load_policy(Path("config/policy.example.yaml"))


def test_compliant_trip_passes(policy):
    result = evaluate_trip(policy, flight_cost=Decimal("900"), hotel_nightly_cost=Decimal("200"))
    assert result.passed is True
    assert result.requires_approval is False
    assert result.violations == ()


def test_business_class_requires_approval(policy):
    result = evaluate_trip(policy, flight_cost=Decimal("900"), cabin="business")
    assert result.requires_approval is True
    assert result.violations[0].code == "BUSINESS_CLASS_APPROVAL_REQUIRED"


def test_negative_cost_is_rejected(policy):
    with pytest.raises(ValueError, match="cannot be negative"):
        evaluate_trip(policy, flight_cost=Decimal("-1"))
