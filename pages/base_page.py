from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.timeout = 10000

    def navigate(self, url: str) -> None:
        self.page.goto(url, timeout=self.timeout)

    def wait_for_url(self, pattern: str) -> None:
        self.page.wait_for_url(pattern, timeout=self.timeout)

    def get_title(self) -> str:
        return self.page.title()

    def take_screenshot(self, name: str) -> str:
        path = f"screenshots/{name}.png"
        self.page.screenshot(path=path)
        return path

    def click(self, selector: str) -> None:
        self.page.click(selector, timeout=self.timeout)

    def fill(self, selector: str, text: str) -> None:
        self.page.fill(selector, text, timeout=self.timeout)

    def get_text(self, selector: str) -> str:
        return self.page.text_content(selector, timeout=self.timeout) or ""

    def is_visible(self, selector: str) -> bool:
        return self.page.is_visible(selector, timeout=self.timeout)
