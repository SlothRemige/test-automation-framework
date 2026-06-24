import pytest

from core.data_provider import load_yaml
from screens.home_screen import HomeScreen


@pytest.mark.mobile
@pytest.mark.p0
class TestHomeScreen:
    def test_header_displayed(self, appium_driver):
        data = load_yaml("mobile/test_data.yaml")["home_screen"]
        home = HomeScreen(appium_driver)
        assert home.get_header_text() == data["expected_header"]

    def test_greeting_displayed(self, appium_driver):
        data = load_yaml("mobile/test_data.yaml")["home_screen"]
        home = HomeScreen(appium_driver)
        assert home.get_greeting() == data["expected_greeting"]

    def test_menu_visible(self, appium_driver):
        home = HomeScreen(appium_driver)
        assert home.is_menu_visible()
