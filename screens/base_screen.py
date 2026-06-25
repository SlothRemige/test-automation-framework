from appium.webdriver.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BaseScreen:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find_element(self, by: str, value: str):
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def find_elements(self, by: str, value: str):
        return self.wait.until(EC.presence_of_all_elements_located((by, value)))

    def click(self, by: str, value: str) -> None:
        self.find_element(by, value).click()

    def get_text(self, by: str, value: str) -> str:
        return self.find_element(by, value).text

    def is_displayed(self, by: str, value: str) -> bool:
        try:
            return self.driver.find_element(by, value).is_displayed()
        except WebDriverException:
            return False

    def take_screenshot(self, name: str) -> str:
        path = f"screenshots/{name}.png"
        self.driver.save_screenshot(path)
        return path

    def swipe_up(self) -> None:
        size = self.driver.get_window_size()
        self.driver.swipe(
            size["width"] // 2,
            int(size["height"] * 0.8),
            size["width"] // 2,
            int(size["height"] * 0.2),
            duration=800,
        )
