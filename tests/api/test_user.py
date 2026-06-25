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
        assert resp["status"] == "error"


@pytest.mark.api
@pytest.mark.p1
class TestUserProfile:
    def test_get_profile_unauthorized(self, mock_api, user_api):
        resp = user_api.get_profile("1")
        assert resp["status"] == "error"
        assert resp["message"] == "Unauthorized"


@pytest.mark.api
@pytest.mark.p0
class TestUserCrud:
    def test_create_user_success(self, mock_api, user_api):
        payload = {"username": "newuser", "email": "new@example.com", "password": "Pass@123"}
        resp = user_api.create_user(payload)
        assert resp["status"] == "created"
        assert resp["id"] == "123"

    def test_get_user_by_id(self, mock_api, user_api):
        resp = user_api.get_profile("123")
        assert resp["id"] == "123"
        assert resp["username"] == "newuser"

    def test_get_user_not_found(self, mock_api, user_api):
        resp = user_api.get_profile("999")
        assert resp["status"] == "error"
        assert resp["message"] == "Not found"

    def test_update_user(self, mock_api, user_api):
        payload = {"username": "updateduser", "email": "updated@example.com"}
        resp = user_api.update_user("123", payload)
        assert resp["status"] == "updated"
        assert resp["username"] == "updateduser"

    def test_delete_user(self, mock_api, user_api):
        resp = user_api.delete_user("123")
        assert resp["status"] == "deleted"

    def test_crud_lifecycle(self, mock_api, user_api):
        # Create
        create_resp = user_api.create_user(
            {"username": "newuser", "email": "new@example.com", "password": "Pass@123"}
        )
        assert create_resp["id"] == "123"

        # Read
        read_resp = user_api.get_profile("123")
        assert read_resp["username"] == "newuser"

        # Update
        update_resp = user_api.update_user(
            "123", {"username": "updateduser", "email": "updated@example.com"}
        )
        assert update_resp["status"] == "updated"

        # Delete
        delete_resp = user_api.delete_user("123")
        assert delete_resp["status"] == "deleted"


@pytest.mark.api
@pytest.mark.p2
class TestUserEdgeCases:
    def test_create_user_server_error(self, mock_api, user_api):
        resp = user_api.create_user({"username": "trigger_500"})
        assert resp["status"] == "error"
        assert resp["message"] == "Internal server error"

    @pytest.mark.parametrize(
        "payload,expected_status",
        [
            ({"username": ""}, 400),
            ({"email": "no-username"}, 400),
            ({"username": "a", "email": "bad-email"}, 400),
        ],
    )
    def test_create_user_validation(self, mock_api, user_api, payload, expected_status):
        resp = user_api.create_user(payload)
        assert resp["status"] == "error"
        assert resp["message"] == "Validation failed"
