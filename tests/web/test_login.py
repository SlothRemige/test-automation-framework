import pytest

from core.data_provider import load_yaml
from pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.p0
class TestLogin:
    def test_login_success(self, mock_web_login, page, app_config):
        data = load_yaml("web/users.yaml")["valid_user"]
        login_page = LoginPage(page)
        login_page.navigate(app_config.web.base_url)
        login_page.login(data["username"], data["password"])
        assert login_page.is_login_success()

    def test_login_failure(self, mock_web_login, page, app_config):
        data = load_yaml("web/users.yaml")["invalid_user"]
        login_page = LoginPage(page)
        login_page.navigate(app_config.web.base_url)
        login_page.login(data["username"], data["password"])
        assert login_page.is_visible(LoginPage.ERROR_MESSAGE)


@pytest.mark.web
@pytest.mark.p1
class TestLoginValidation:
    _scenarios = load_yaml("web/users.yaml")["login_scenarios"]

    @pytest.mark.parametrize(
        "username,password,expected_error",
        [(s["username"], s["password"], s["expected_error"]) for s in _scenarios],
    )
    def test_login_validation(
        self, mock_web_login, page, app_config, username, password, expected_error
    ):
        login_page = LoginPage(page)
        login_page.navigate(app_config.web.base_url)
        login_page.login(username, password)
        assert expected_error in login_page.get_error_message()
