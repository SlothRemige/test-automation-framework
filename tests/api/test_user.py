import pytest


@pytest.mark.api
@pytest.mark.p0
class TestUserLogin:
    def test_login_success(self, mock_api, user_api, valid_credentials):
        resp = user_api.login(
            username=valid_credentials["username"],
            password=valid_credentials["password"],
        )
        assert resp.status_code == 200
        assert resp["token"] == "mock-jwt-token"
        assert resp["status"] == "ok"

    def test_login_failure(self, mock_api, user_api):
        resp = user_api.login(
            username="invalid_user",
            password="wrong_password",
        )
        assert resp.status_code == 401
        assert resp["status"] == "error"
        assert "token" not in resp

    @pytest.mark.parametrize(
        "username,password",
        [
            ("", "somepass"),
            ("testuser", ""),
            ("", ""),
        ],
    )
    def test_login_empty_fields(self, mock_api, user_api, username, password):
        resp = user_api.login(username=username, password=password)
        assert resp.status_code == 401
        assert resp["status"] == "error"


@pytest.mark.api
@pytest.mark.p1
class TestUserProfile:
    def test_get_profile_unauthorized(self, mock_api, user_api):
        resp = user_api.get_profile("1")
        assert resp.status_code == 401
        assert resp["status"] == "error"
        assert resp["message"] == "Unauthorized"


@pytest.mark.api
@pytest.mark.p0
class TestUserCrud:
    def test_create_user_success(self, mock_api, user_api):
        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Pass@123",
        }
        resp = user_api.create_user(payload)
        assert resp.status_code == 201
        assert resp["status"] == "created"
        assert resp["id"] == "123"

    def test_get_user_by_id(self, mock_api, user_api):
        resp = user_api.get_profile("123")
        assert resp.status_code == 200
        assert resp["id"] == "123"
        assert resp["username"] == "newuser"

    def test_get_user_not_found(self, mock_api, user_api):
        resp = user_api.get_profile("999")
        assert resp.status_code == 404
        assert resp["status"] == "error"
        assert resp["message"] == "Not found"

    def test_update_user(self, mock_api, user_api):
        payload = {"username": "updateduser", "email": "updated@example.com"}
        resp = user_api.update_user("123", payload)
        assert resp.status_code == 200
        assert resp["status"] == "updated"
        assert resp["username"] == "updateduser"

    def test_delete_user(self, mock_api, user_api):
        resp = user_api.delete_user("123")
        assert resp.status_code == 200
        assert resp["status"] == "deleted"

    def test_crud_lifecycle(self, mock_api, user_api):
        create_resp = user_api.create_user(
            {"username": "newuser", "email": "new@example.com", "password": "Pass@123"}
        )
        assert create_resp.status_code == 201
        assert create_resp["id"] == "123"

        read_resp = user_api.get_profile("123")
        assert read_resp.status_code == 200
        assert read_resp["username"] == "newuser"

        update_resp = user_api.update_user(
            "123", {"username": "updateduser", "email": "updated@example.com"}
        )
        assert update_resp.status_code == 200
        assert update_resp["status"] == "updated"

        delete_resp = user_api.delete_user("123")
        assert delete_resp.status_code == 200
        assert delete_resp["status"] == "deleted"


@pytest.mark.api
@pytest.mark.p2
class TestUserEdgeCases:
    def test_create_user_server_error(self, mock_api, user_api):
        resp = user_api.create_user({"username": "trigger_500"})
        assert resp.status_code == 500
        assert resp["status"] == "error"
        assert resp["message"] == "Internal server error"

    @pytest.mark.parametrize(
        "payload",
        [
            {"username": ""},
            {"email": "no-username"},
            {"username": "a", "email": "bad-email"},
        ],
    )
    def test_create_user_validation(self, mock_api, user_api, payload):
        resp = user_api.create_user(payload)
        assert resp.status_code == 400
        assert resp["status"] == "error"
        assert resp["message"] == "Validation failed"
