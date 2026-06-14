"""Application settings with safe demonstration defaults."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = "AI Travel Agent"
    environment: str = "development"
    simulation_mode: bool = True
    policy_path: Path = Path("config/policy.yaml")

    model_config = SettingsConfigDict(env_prefix="TRAVEL_AGENT_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
