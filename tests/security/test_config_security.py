import pytest
from pydantic import ValidationError

from travel_agent.config import Settings


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "https://travel.example.test/path",
        "https://user:password@travel.example.test",
        "file:///tmp/app",
    ],
)
def test_cors_origin_must_be_an_explicit_http_origin(origin):
    with pytest.raises(ValidationError):
        Settings(allowed_origins=[origin])


def test_production_cors_requires_https():
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            dev_auth_enabled=False,
            allowed_origins=["http://travel.example.test"],
        )
