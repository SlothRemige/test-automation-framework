import pytest

from core.config_loader import load_config, AppConfig
from core.logger import setup_logging

pytest_plugins = ["fixtures.auth_fixtures"]


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Test environment: dev, staging, prod",
    )


@pytest.fixture(scope="session")
def env(request) -> str:
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def app_config(env: str) -> AppConfig:
    return load_config(env)


@pytest.fixture(scope="session", autouse=True)
def _setup_logging(app_config: AppConfig):
    setup_logging("DEBUG")


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "p0: 核心功能")
    config.addinivalue_line("markers", "p1: 重要功能")
    config.addinivalue_line("markers", "p2: 边缘场景")
    config.addinivalue_line("markers", "web: Web端测试")
    config.addinivalue_line("markers", "api: API端测试")
    config.addinivalue_line("markers", "mobile: 移动端测试")


def pytest_sessionfinish(session):
    """Write Allure environment info after test session completes."""
    import json
    import os
    from pathlib import Path

    allure_dir = session.config.getoption("--alluredir", default=None)
    if allure_dir:
        env_file = Path(allure_dir) / "environment.properties"
        env_file.write_text(
            f"Environment={os.getenv('TEST_ENV', 'dev')}\nPython={os.sys.version}\n"
        )
        categories = Path(allure_dir) / "categories.json"
        categories.write_text(
            json.dumps(
                [
                    {
                        "name": "Ignored tests",
                        "matchedStatuses": ["skipped"],
                    },
                    {
                        "name": "Infrastructure problems",
                        "matchedStatuses": ["broken", "error"],
                        "messageRegex": ".*(ConnectionError|Timeout|ConnectionRefusedError).*",
                    },
                    {
                        "name": "Product defects",
                        "matchedStatuses": ["failed"],
                    },
                ],
                indent=2,
            )
        )
