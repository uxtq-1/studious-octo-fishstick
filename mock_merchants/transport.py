"""Placeholder transport mock merchant retained for the next reconstruction phase."""

from mock_merchants.base import MerchantProfile

PROFILE = MerchantProfile(
    merchant_id="mock-transport",
    name="Mock Transport Merchant",
    category="transport",
    base_url="http://127.0.0.1:8000",
)
