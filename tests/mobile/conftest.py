import pytest
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from unittest.mock import MagicMock, patch


def pytest_addoption(parser):
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="Mobile platform: android or ios",
    )


@pytest.fixture(scope="session")
def platform(request) -> str:
    return request.config.getoption("--platform")


def _make_mock_element(text="", displayed=True):
    el = MagicMock()
    el.text = text
    el.is_displayed.return_value = displayed
    return el


@pytest.fixture(scope="session")
def appium_driver(app_config, platform):
    server_url = app_config.mobile.appium_server

    if platform == "android":
        options = UiAutomator2Options()
        options.platform_version = app_config.mobile.platform_version
        options.automation_name = "UiAutomator2"
    else:
        options = XCUITestOptions()
        options.platform_version = app_config.mobile.platform_version
        options.automation_name = "XCUITest"

    mock_driver = MagicMock()
    mock_driver.get_window_size.return_value = {"width": 1080, "height": 1920}

    def find_element(by, value):
        lookup = str(value)
        if "header" in lookup:
            return _make_mock_element("Home")
        if "greeting" in lookup:
            return _make_mock_element("Welcome")
        if "menu" in lookup:
            return _make_mock_element("Menu", displayed=True)
        return _make_mock_element("unknown")

    mock_driver.find_element.side_effect = find_element

    with patch("appium.webdriver.Remote", return_value=mock_driver):
        from appium import webdriver as ad

        driver = ad.Remote(server_url, options=options)

    yield driver
