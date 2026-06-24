import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class WebConfig(BaseModel):
    base_url: str = "https://localhost"
    timeout: int = Field(default=30000, gt=0, description="Timeout in milliseconds")


class ApiConfig(BaseModel):
    base_url: str = "https://localhost"
    timeout: int = Field(default=30, gt=0, description="Timeout in seconds")


class MobileConfig(BaseModel):
    appium_server: str = "http://localhost:4723"
    platform_version: str = "14.0"


class AppConfig(BaseModel):
    environment: str = "dev"
    web: WebConfig = WebConfig()
    api: ApiConfig = ApiConfig()
    mobile: MobileConfig = MobileConfig()


def load_config(env: str | None = None) -> AppConfig:
    if env is None:
        env = os.getenv("TEST_ENV", "dev")

    config_dir = Path(__file__).parent.parent / "config"
    config_path = config_dir / f"{env}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    env_name = raw.get("environment")
    if env_name is None:
        raise ValueError(f"Config file {config_path} missing required 'environment' key")

    return AppConfig(
        environment=env_name,
        web=WebConfig(**raw.get("web", {})),
        api=ApiConfig(**raw.get("api", {})),
        mobile=MobileConfig(**raw.get("mobile", {})),
    )
