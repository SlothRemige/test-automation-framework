import pytest
import responses

from apis.user_api import UserApi


@pytest.fixture(scope="module")
def user_api(http_client):
    return UserApi(http_client)


@pytest.fixture(scope="function")
def mock_api(app_config):
    base = app_config.api.base_url
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Login with valid credentials → success
        rsps.add(
            responses.POST,
            f"{base}/auth/login",
            json={"token": "mock-jwt-token", "status": "ok"},
            status=200,
            match=[
                responses.matchers.json_params_matcher(
                    {"username": "testuser", "password": "Test@123456"}
                )
            ],
        )
        # Login with any other credentials → failure
        rsps.add(
            responses.POST,
            f"{base}/auth/login",
            json={"status": "error", "message": "Invalid credentials"},
            status=401,
        )
        # Profile without valid auth → unauthorized
        rsps.add(
            responses.GET,
            f"{base}/users/1",
            json={"status": "error", "message": "Unauthorized"},
            status=401,
        )
        yield rsps
