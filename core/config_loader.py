import os
from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebConfig(BaseSettings):
    base_url: str = "https://localhost"
    timeout: int = Field(default=30000, gt=0, description="Timeout in milliseconds")


class ApiConfig(BaseSettings):
    base_url: str = "https://localhost"
    timeout: int = Field(default=30, gt=0, description="Timeout in seconds")


class MobileConfig(BaseSettings):
    appium_server: str = "http://localhost:4723"
    platform_version: str = "14.0"


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TEST_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    environment: str = "dev"
    web: WebConfig = WebConfig()
    api: ApiConfig = ApiConfig()
    mobile: MobileConfig = MobileConfig()


def _yaml_to_env_defaults(raw: dict) -> None:
    prefix = "TEST_"
    for section in ("web", "api", "mobile"):
        if section in raw:
            for key, val in raw[section].items():
                env_key = f"{prefix}{section}__{key}".upper()
                os.environ.setdefault(env_key, str(val))
    os.environ.setdefault(f"{prefix}ENVIRONMENT", str(raw.get("environment", "dev")))


def load_config(env: str | None = None) -> AppConfig:
    if env is None:
        env = os.getenv("TEST_ENV", "dev")

    config_dir = Path(__file__).parent.parent / "config"
    config_path = config_dir / f"{env}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    _yaml_to_env_defaults(raw)
    return AppConfig()
