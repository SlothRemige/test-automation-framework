import pytest

from core.data_provider import load_yaml


@pytest.fixture(scope="session")
def valid_credentials():
    return load_yaml("api/users.yaml")["valid_user"]


@pytest.fixture(scope="session")
def admin_credentials():
    return load_yaml("api/users.yaml")["admin_user"]


@pytest.fixture(scope="session")
def auth_token(app_config, valid_credentials):
    import requests

    resp = requests.post(
        f"{app_config.api.base_url}/auth/login",
        json={
            "username": valid_credentials["username"],
            "password": valid_credentials["password"],
        },
        timeout=app_config.api.timeout,
    )
    if resp.status_code == 200:
        return resp.json().get("token", "")
    return ""
