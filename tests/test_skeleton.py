import pytest


def test_config_loads(app_config):
    assert app_config.environment == "dev"
    assert app_config.web.base_url == "https://dev.example.com"


def test_env_option(env):
    assert env == "dev"


@pytest.mark.smoke
def test_smoke_marker():
    assert True
