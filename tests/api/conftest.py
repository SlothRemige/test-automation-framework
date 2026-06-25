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
        # === Login endpoints (specific matchers first, catch-all last) ===
        # Valid credentials → success
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
        # SQL injection attempt → 400
        rsps.add(
            responses.POST,
            f"{base}/auth/login",
            json={"status": "error", "message": "Invalid input"},
            status=400,
            match=[
                responses.matchers.json_params_matcher(
                    {"username": "admin'--", "password": "x"}
                )
            ],
        )
        # Login catch-all → 401
        rsps.add(
            responses.POST,
            f"{base}/auth/login",
            json={"status": "error", "message": "Invalid credentials"},
            status=401,
        )

        # === User CRUD endpoints (specific matchers first, catch-all last) ===
        # Valid create → 201
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={
                "id": "123",
                "username": "newuser",
                "email": "new@example.com",
                "status": "created",
            },
            status=201,
            match=[
                responses.matchers.json_params_matcher(
                    {
                        "username": "newuser",
                        "email": "new@example.com",
                        "password": "Pass@123",
                    }
                )
            ],
        )
        # Duplicate username → 409
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"status": "error", "message": "Username already exists"},
            status=409,
            match=[
                responses.matchers.json_params_matcher(
                    {"username": "testuser", "email": "new@example.com", "password": "Pass@123"}
                )
            ],
        )
        # Server error trigger → 500
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"status": "error", "message": "Internal server error"},
            status=500,
            match=[responses.matchers.json_params_matcher({"username": "trigger_500"})],
        )
        # XSS payload → 400
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"status": "error", "message": "XSS rejected"},
            status=400,
            match=[
                responses.matchers.json_params_matcher(
                    {"username": "<script>alert(1)</script>"}
                )
            ],
        )
        # Payload too large → 413
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"status": "error", "message": "Payload too large"},
            status=413,
            match=[
                responses.matchers.json_params_matcher(
                    {"username": "a" * 1000}
                )
            ],
        )
        # Create user catch-all → 400
        rsps.add(
            responses.POST,
            f"{base}/users",
            json={"status": "error", "message": "Validation failed"},
            status=400,
        )

        # === GET /users endpoints ===
        # Unauthorized profile access
        rsps.add(
            responses.GET,
            f"{base}/users/1",
            json={"status": "error", "message": "Unauthorized"},
            status=401,
        )
        # Get user by ID → success
        rsps.add(
            responses.GET,
            f"{base}/users/123",
            json={"id": "123", "username": "newuser", "email": "new@example.com"},
            status=200,
        )
        # Get non-existent user → 404
        rsps.add(
            responses.GET,
            f"{base}/users/999",
            json={"status": "error", "message": "Not found"},
            status=404,
        )
        # List users — page 1
        rsps.add(
            responses.GET,
            f"{base}/users?page=1&limit=10",
            json={"data": [], "page": 1, "limit": 10, "total": 0},
            status=200,
        )
        # List users — invalid page
        rsps.add(
            responses.GET,
            f"{base}/users?page=0&limit=10",
            json={"status": "error", "message": "Invalid page"},
            status=400,
        )
        # List users — limit too high
        rsps.add(
            responses.GET,
            f"{base}/users?page=1&limit=1000",
            json={"status": "error", "message": "Limit too large"},
            status=400,
        )
        # Rate limit → 429
        rsps.add(
            responses.GET,
            f"{base}/users?page=1&limit=1",
            json={"status": "error", "message": "Too many requests"},
            status=429,
        )
        # Service unavailable → 503 (retries exhausted)
        rsps.add(
            responses.GET,
            f"{base}/users/503",
            json={"status": "error", "message": "Service unavailable"},
            status=503,
        )

        # === PUT /users endpoints ===
        # Update user → success
        rsps.add(
            responses.PUT,
            f"{base}/users/123",
            json={
                "id": "123",
                "username": "updateduser",
                "email": "updated@example.com",
                "status": "updated",
            },
            status=200,
        )
        # Update non-existent user
        rsps.add(
            responses.PUT,
            f"{base}/users/999",
            json={"status": "error", "message": "Not found"},
            status=404,
        )

        # === DELETE /users endpoints ===
        # Delete user → success
        rsps.add(
            responses.DELETE,
            f"{base}/users/123",
            json={"status": "deleted"},
            status=200,
        )
        # Delete non-existent user
        rsps.add(
            responses.DELETE,
            f"{base}/users/999",
            json={"status": "error", "message": "Not found"},
            status=404,
        )

        yield rsps
