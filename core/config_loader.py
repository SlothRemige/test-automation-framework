import os
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class WebConfig(BaseSettings):
    base_url: str = "https://localhost"
    timeout: int = 30000


class ApiConfig(BaseSettings):
    base_url: str = "https://localhost"
    timeout: int = 30


class MobileConfig(BaseSettings):
    appium_server: str = "http://localhost:4723"
    platform_version: str = "14.0"


class AppConfig(BaseSettings):
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

    return AppConfig(
        environment=raw["environment"],
        web=WebConfig(**raw.get("web", {})),
        api=ApiConfig(**raw.get("api", {})),
        mobile=MobileConfig(**raw.get("mobile", {})),
    )
