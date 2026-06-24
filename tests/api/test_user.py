import pytest


@pytest.mark.api
@pytest.mark.p0
class TestUserLogin:
    def test_login_success(self, mock_api, user_api, valid_credentials):
        resp = user_api.login(
            username=valid_credentials["username"],
            password=valid_credentials["password"],
        )
        assert resp["token"] == "mock-jwt-token"
        assert resp["status"] == "ok"

    def test_login_failure(self, mock_api, user_api):
        resp = user_api.login(
            username="invalid_user",
            password="wrong_password",
        )
        assert resp["status"] == "error"
        assert "token" not in resp


@pytest.mark.api
@pytest.mark.p1
class TestUserProfile:
    def test_get_profile_unauthorized(self, mock_api, user_api):
        resp = user_api.get_profile("1")
        assert resp["status"] == "error"
        assert resp["message"] == "Unauthorized"
