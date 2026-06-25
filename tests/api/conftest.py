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
        # Create user with valid payload → success
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"id": "123", "username": "newuser", "email": "new@example.com", "status": "created"},
            status=201,
            match=[
                responses.matchers.json_params_matcher(
                    {"username": "newuser", "email": "new@example.com", "password": "Pass@123"}
                )
            ],
        )
        # Create user triggering server error → 500
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"status": "error", "message": "Internal server error"},
            status=500,
            match=[
                responses.matchers.json_params_matcher(
                    {"username": "trigger_500"}
                )
            ],
        )
        # Create user with invalid payload → validation error (catch-all)
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"status": "error", "message": "Validation failed"},
            status=400,
        )
        # Get user by ID → success
        rsps.add(
            responses.GET,
            f"{base}/users/123",
            json={"id": "123", "username": "newuser", "email": "new@example.com"},
            status=200,
        )
        # Update user → success
        rsps.add(
            responses.PUT,
            f"{base}/users/123",
            json={"id": "123", "username": "updateduser", "email": "updated@example.com", "status": "updated"},
            status=200,
        )
        # Delete user → success
        rsps.add(
            responses.DELETE,
            f"{base}/users/123",
            json={"status": "deleted"},
            status=200,
        )
        # Get non-existent user → 404
        rsps.add(
            responses.GET,
            f"{base}/users/999",
            json={"status": "error", "message": "Not found"},
            status=404,
        )
        yield rsps
