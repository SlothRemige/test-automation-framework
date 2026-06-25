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

    success_html = """<html><body>
      <div class="success-message">Welcome</div>
    </body></html>"""

    error_html_required = """<html><body>
      <div class="error-message">Username is required</div>
    </body></html>"""

    error_html_password = """<html><body>
      <div class="error-message">Password is required</div>
    </body></html>"""

    error_html_invalid = """<html><body>
      <div class="error-message">Invalid credentials</div>
    </body></html>"""

    def handle_route(route):
        if route.request.method == "GET":
            route.fulfill(status=200, content_type="text/html", body=login_form_html)
            return

        from urllib.parse import parse_qs

        post_data = route.request.post_data or ""
        params = parse_qs(post_data)
        username = params.get("username", [""])[0]
        password = params.get("password", [""])[0]

        if username == "testuser" and password == "Test@123456":
            route.fulfill(status=200, content_type="text/html", body=success_html)
        elif not username:
            route.fulfill(status=400, content_type="text/html", body=error_html_required)
        elif not password:
            route.fulfill(status=400, content_type="text/html", body=error_html_password)
        else:
            route.fulfill(status=401, content_type="text/html", body=error_html_invalid)

    page.route(f"{base}/**", handle_route)
    yield page
