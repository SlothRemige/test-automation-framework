import pytest

from core.http_client import HttpClient


@pytest.fixture(scope="session")
def http_client(app_config):
    client = HttpClient(
        base_url=app_config.api.base_url,
        timeout=app_config.api.timeout,
    )
    yield client
    client.close()
