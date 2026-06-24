from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from screens.base_screen import BaseScreen


class HomeScreen(BaseScreen):
    HEADER = (By.ID, "com.example:id/header")
    MENU_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "menu")
    SEARCH_ICON = (By.ID, "com.example:id/search")
    USER_GREETING = (By.ID, "com.example:id/greeting")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def get_header_text(self) -> str:
        return self.get_text(*self.HEADER)

    def is_menu_visible(self) -> bool:
        return self.is_displayed(*self.MENU_BUTTON)

    def open_menu(self) -> None:
        self.click(*self.MENU_BUTTON)

    def get_greeting(self) -> str:
        return self.get_text(*self.USER_GREETING)
