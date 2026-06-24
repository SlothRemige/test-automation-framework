import pytest


def test_config_loads(config):
    assert config.environment == "dev"
    assert config.web.base_url == "https://dev.example.com"


def test_env_option(env):
    assert env == "dev"


@pytest.mark.smoke
def test_smoke_marker():
    assert True
