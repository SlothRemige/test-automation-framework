import os

import pytest

from core.data_provider import load_yaml


@pytest.fixture(scope="session")
def valid_credentials():
    data = load_yaml("api/users.yaml")["valid_user"]
    return {
        "username": data["username"],
        "password": os.getenv("TEST_PASSWORD", data["password"]),
        "email": data["email"],
    }


@pytest.fixture(scope="session")
def admin_credentials():
    data = load_yaml("api/users.yaml")["admin_user"]
    return {
        "username": data["username"],
        "password": os.getenv("ADMIN_PASSWORD", data["password"]),
        "email": data["email"],
    }


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
        token = resp.json().get("token", "")
        if token:
            return token
    pytest.skip(
        f"Auth token not available (status={resp.status_code})"
    )
