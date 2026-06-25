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


@pytest.mark.api
@pytest.mark.p1
class TestUserSecurity:
    def test_sql_injection_rejected(self, mock_api, user_api):
        resp = user_api.login(username="admin'--", password="x")
        assert resp.status_code == 400
        assert resp["status"] == "error"
        assert "Invalid input" in resp["message"]

    def test_xss_payload_rejected(self, mock_api, user_api):
        resp = user_api.create_user({"username": "<script>alert(1)</script>"})
        assert resp.status_code == 400
        assert resp["message"] == "XSS rejected"

    def test_payload_too_large(self, mock_api, user_api):
        resp = user_api.create_user({"username": "a" * 1000})
        assert resp.status_code == 413
        assert resp["message"] == "Payload too large"

    @pytest.mark.parametrize(
        "username,password",
        [
            ("testuser", "wrong_password"),
            ("nonexistent", "any_password"),
            ("testuser@example.com", "Test@123456"),
        ],
    )
    def test_login_variations(self, mock_api, user_api, username, password):
        resp = user_api.login(username=username, password=password)
        assert resp.status_code == 401
        assert resp["status"] == "error"


@pytest.mark.api
@pytest.mark.p1
class TestUserNegativeCrud:
    def test_update_nonexistent_user(self, mock_api, user_api):
        resp = user_api.update_user("999", {"username": "nope"})
        assert resp.status_code == 404
        assert resp["message"] == "Not found"

    def test_delete_nonexistent_user(self, mock_api, user_api):
        resp = user_api.delete_user("999")
        assert resp.status_code == 404
        assert resp["message"] == "Not found"

    def test_create_duplicate_username(self, mock_api, user_api):
        payload = {"username": "testuser", "email": "new@example.com", "password": "Pass@123"}
        resp = user_api.create_user(payload)
        assert resp.status_code == 409
        assert resp["message"] == "Username already exists"


@pytest.mark.api
@pytest.mark.p2
class TestUserPagination:
    def test_list_users_page1(self, mock_api, user_api):
        resp = user_api.list_users(page=1, limit=10)
        assert resp.status_code == 200
        assert resp["total"] == 0
        assert resp["page"] == 1

    def test_list_users_invalid_page(self, mock_api, user_api):
        resp = user_api.list_users(page=0, limit=10)
        assert resp.status_code == 400
        assert resp["message"] == "Invalid page"

    def test_list_users_limit_too_high(self, mock_api, user_api):
        resp = user_api.list_users(page=1, limit=1000)
        assert resp.status_code == 400
        assert resp["message"] == "Limit too large"


@pytest.mark.api
@pytest.mark.p2
class TestUserResilience:
    def test_rate_limit_429(self, mock_api, user_api):
        resp = user_api.list_users(page=1, limit=1)
        assert resp.status_code == 429
        assert resp["message"] == "Too many requests"

    def test_service_unavailable_triggers_retry(self, mock_api, user_api):
        import requests as req

        with pytest.raises(req.exceptions.RetryError):
            user_api.get_profile("503")
