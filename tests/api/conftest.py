import pytest

from apis.user_api import UserApi


@pytest.fixture(scope="module")
def user_api(http_client):
    return UserApi(http_client)
