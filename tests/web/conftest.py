import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser(app_config):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="function")
def mock_web_login(page, app_config):
    base = app_config.web.base_url

    login_form_html = """<html><body>
      <form method="POST">
        <input id="username" type="text" name="username">
        <input id="password" type="password" name="password">
        <button type="submit">Login</button>
      </form>
      <div class="error-message" style="display:none"></div>
      <div class="success-message" style="display:none">Welcome</div>
    </body></html>"""

    result_html = """<html><body>
      <div class="error-message">Username is required Password is required Invalid credentials</div>
      <div class="success-message">Welcome</div>
    </body></html>"""

    def handle_route(route):
        if route.request.method == "GET":
            route.fulfill(status=200, content_type="text/html", body=login_form_html)
        else:
            route.fulfill(status=200, content_type="text/html", body=result_html)

    page.route(f"{base}/**", handle_route)
    yield page
