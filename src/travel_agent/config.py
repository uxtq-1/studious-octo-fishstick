"""Application settings with safe demonstration defaults."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "AI Travel Agent"
    environment: str = "development"
    simulation_mode: bool = True
    policy_path: Path = Path("config/policy.yaml")
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://127.0.0.1:8000", "http://localhost:8000"]
    )
    allowed_hosts: list[str] = Field(
        default_factory=lambda: ["127.0.0.1", "localhost", "testserver"]
    )
    max_request_body_bytes: int = Field(default=1_048_576, ge=1_024, le=10_485_760)
    dev_auth_enabled: bool = True

    model_config = SettingsConfigDict(env_prefix="TRAVEL_AGENT_", env_file=".env")

    @model_validator(mode="after")
    def validate_secure_environment(self) -> "Settings":
        if "*" in self.allowed_origins:
            raise ValueError("CORS wildcard origins are not allowed")
        for origin in self.allowed_origins:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
                or parsed.username
                or parsed.password
            ):
                raise ValueError("CORS origins must be explicit HTTP(S) origins")
        if self.environment == "production" and self.dev_auth_enabled:
            raise ValueError("development authentication cannot be enabled in production")
        if self.environment == "production" and any(
            not origin.startswith("https://") for origin in self.allowed_origins
        ):
            raise ValueError("production CORS origins must use HTTPS")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
