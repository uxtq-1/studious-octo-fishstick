"""Shared mock-merchant discovery representation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MerchantProfile:
    merchant_id: str
    name: str
    category: str
    base_url: str
