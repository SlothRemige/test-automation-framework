import pytest


@pytest.mark.api
@pytest.mark.p0
class TestUserLogin:
    def test_login_success(self, user_api, valid_credentials):
        resp = user_api.login(
            username=valid_credentials["username"],
            password=valid_credentials["password"],
        )
        assert "token" in resp or resp.get("status") == "ok"

    def test_login_failure(self, user_api):
        resp = user_api.login(
            username="invalid_user",
            password="wrong_password",
        )
        assert resp.get("status") == "error" or "token" not in resp


@pytest.mark.api
@pytest.mark.p1
class TestUserProfile:
    def test_get_profile_unauthorized(self, user_api):
        resp = user_api.get_profile("1")
        assert resp.get("status") == "error"
