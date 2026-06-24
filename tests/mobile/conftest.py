import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions


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

    driver = webdriver.Remote(server_url, options=options)
    yield driver
    driver.quit()
