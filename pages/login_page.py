from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "button[type='submit']"
    ERROR_MESSAGE = ".error-message"
    SUCCESS_MESSAGE = ".success-message"

    def __init__(self, page: Page):
        super().__init__(page)

    def login(self, username: str, password: str) -> None:
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_login_success(self) -> bool:
        return self.is_visible(self.SUCCESS_MESSAGE)
