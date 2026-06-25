# 自动化测试框架实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零搭建纯 Python 自动化测试框架，覆盖 Web、App、API 三类被测对象，支持多环境配置。

**Architecture:** 分层单体架构 — core/ 提供跨端共享基础设施，pages/screens/apis/ 封装各端操作，tests/ 按端分目录，pytest conftest 层级机制实现 fixture 隔离与复用。

**Tech Stack:** Python >=3.11, pytest >=8.3, Playwright >=1.48, Appium-Python-Client >=4.0, requests >=2.32, PyYAML + pydantic-settings, structlog

---

### Task 1: 项目骨架和依赖管理

**Files:**
- Create: `pyproject.toml`
- Create: `pytest.ini`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "test-automation-framework"
version = "0.1.0"
description = "Multi-platform test automation framework (Web, App, API)"
requires-python = ">=3.11"

dependencies = [
    "pytest>=8.3",
    "playwright>=1.48",
    "Appium-Python-Client>=4.0",
    "requests>=2.32",
    "pyyaml>=6.0",
    "pydantic-settings>=2.0",
    "structlog>=24.0",
    "pytest-xdist>=3.6",
    "pytest-check>=2.0",
    "responses>=0.25",
    "allure-pytest>=2.13",
]

[project.optional-dependencies]
dev = [
    "pytest-watch>=0.1",
    "ipython>=8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = ["-v", "--strict-markers", "--tb=short"]
markers = [
    "smoke: 冒烟测试",
    "p0: 核心功能",
    "p1: 重要功能",
    "p2: 边缘场景",
    "web: Web端测试",
    "api: API端测试",
    "mobile: 移动端测试",
]
```

- [ ] **Step 2: 创建 pytest.ini**

pytest 配置已在 pyproject.toml 的 `[tool.pytest.ini_options]` 中定义，无需单独 pytest.ini 文件。

- [ ] **Step 3: 安装依赖**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pip install -e ".[dev]"
```

Expected: 所有依赖安装成功，无报错。

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "feat: add project skeleton with dependencies"
```

---

### Task 2: 多环境配置系统

**Files:**
- Create: `config/dev.yaml`
- Create: `config/staging.yaml`
- Create: `config/prod.yaml`
- Create: `core/__init__.py`
- Create: `core/config_loader.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: 创建环境配置文件**

`config/dev.yaml`:
```yaml
environment: dev
web:
  base_url: "https://dev.example.com"
  timeout: 30000
api:
  base_url: "https://dev-api.example.com"
  timeout: 30
mobile:
  appium_server: "http://localhost:4723"
  platform_version: "14.0"
```

`config/staging.yaml`:
```yaml
environment: staging
web:
  base_url: "https://staging.example.com"
  timeout: 30000
api:
  base_url: "https://staging-api.example.com"
  timeout: 30
mobile:
  appium_server: "http://localhost:4723"
  platform_version: "14.0"
```

`config/prod.yaml`:
```yaml
environment: prod
web:
  base_url: "https://example.com"
  timeout: 15000
api:
  base_url: "https://api.example.com"
  timeout: 15
mobile:
  appium_server: "http://localhost:4723"
  platform_version: "14.0"
```

- [ ] **Step 2: 创建 core/__init__.py**

```python
```

- [ ] **Step 3: 创建 core/config_loader.py**

```python
import os
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings


class WebConfig(BaseSettings):
    base_url: str = "https://localhost"
    timeout: int = 30000


class ApiConfig(BaseSettings):
    base_url: str = "https://localhost"
    timeout: int = 30


class MobileConfig(BaseSettings):
    appium_server: str = "http://localhost:4723"
    platform_version: str = "14.0"


class AppConfig(BaseSettings):
    environment: str = "dev"
    web: WebConfig = WebConfig()
    api: ApiConfig = ApiConfig()
    mobile: MobileConfig = MobileConfig()


def load_config(env: str | None = None) -> AppConfig:
    if env is None:
        env = os.getenv("TEST_ENV", "dev")

    config_dir = Path(__file__).parent.parent / "config"
    config_path = config_dir / f"{env}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    return AppConfig(
        environment=raw["environment"],
        web=WebConfig(**raw.get("web", {})),
        api=ApiConfig(**raw.get("api", {})),
        mobile=MobileConfig(**raw.get("mobile", {})),
    )
```

- [ ] **Step 4: 创建 tests/__init__.py**

```python
```

- [ ] **Step 5: 验证配置加载**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && python -c "
from core.config_loader import load_config
c = load_config('dev')
print(f'env={c.environment}, web={c.web.base_url}, api={c.api.base_url}')
"
```

Expected: `env=dev, web=https://dev.example.com, api=https://dev-api.example.com`

- [ ] **Step 6: Commit**

```bash
git add config/ core/ tests/__init__.py
git commit -m "feat: add multi-environment config system"
```

---

### Task 3: 日志系统

**Files:**
- Create: `core/logger.py`

- [ ] **Step 1: 创建 core/logger.py**

```python
import logging
import sys

import structlog


def setup_logging(level: str = "INFO") -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer()
            if sys.stderr.isatty()
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(format="%(message)s", stream=sys.stderr, level=level)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
```

- [ ] **Step 2: 验证日志输出**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && python -c "
from core.logger import setup_logging, get_logger
setup_logging('DEBUG')
log = get_logger('test')
log.info('hello', key='value')
log.debug('debug message')
"
```

Expected: 终端看到彩色格式化日志输出。

- [ ] **Step 3: Commit**

```bash
git add core/logger.py
git commit -m "feat: add structured logging with structlog"
```

---

### Task 4: 全局 pytest 配置和 fixtures

**Files:**
- Create: `conftest.py`

- [ ] **Step 1: 创建根 conftest.py**

```python
import pytest

from core.config_loader import load_config, AppConfig
from core.logger import setup_logging


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Test environment: dev, staging, prod",
    )


@pytest.fixture(scope="session")
def env(request) -> str:
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def config(env: str) -> AppConfig:
    return load_config(env)


@pytest.fixture(scope="session", autouse=True)
def _setup_logging(config: AppConfig):
    setup_logging("DEBUG")


def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: 冒烟测试")
    config.addinivalue_line("markers", "p0: 核心功能")
    config.addinivalue_line("markers", "p1: 重要功能")
    config.addinivalue_line("markers", "p2: 边缘场景")
    config.addinivalue_line("markers", "web: Web端测试")
    config.addinivalue_line("markers", "api: API端测试")
    config.addinivalue_line("markers", "mobile: 移动端测试")
```

- [ ] **Step 2: 创建 dummy test 验证框架骨架**

```bash
mkdir -p /Users/remiges/project/python/test/tests
```

创建 `tests/test_skeleton.py`:
```python
def test_config_loads(config):
    assert config.environment == "dev"
    assert config.web.base_url == "https://dev.example.com"


def test_env_option(env):
    assert env == "dev"


@pytest.mark.smoke
def test_smoke_marker():
    assert True
```

- [ ] **Step 3: 运行测试验证**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest tests/test_skeleton.py -v
```

Expected: 3 tests PASS

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest tests/test_skeleton.py -m smoke -v
```

Expected: 1 test PASS (只有 test_smoke_marker)

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest tests/test_skeleton.py --env=staging -v
```

Expected: test_config_loads FAIL (因为 staging 的 base_url 不同，这验证了环境切换生效)

- [ ] **Step 4: Commit**

```bash
git add conftest.py tests/test_skeleton.py
git commit -m "feat: add global pytest fixtures and env switching"
```

---

### Task 5: HTTP 客户端和 API 基础层

**Files:**
- Create: `core/http_client.py`
- Create: `apis/__init__.py`
- Create: `apis/base_api.py`

- [ ] **Step 1: 创建 core/http_client.py**

```python
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class HttpClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        retry = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(
            self._url(path), timeout=self.timeout, **kwargs
        )

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(
            self._url(path), timeout=self.timeout, **kwargs
        )

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.session.put(
            self._url(path), timeout=self.timeout, **kwargs
        )

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.session.delete(
            self._url(path), timeout=self.timeout, **kwargs
        )

    def set_header(self, key: str, value: str) -> None:
        self.session.headers[key] = value

    def close(self) -> None:
        self.session.close()
```

- [ ] **Step 2: 创建 apis/__init__.py**

```python
```

- [ ] **Step 3: 创建 apis/base_api.py**

```python
from core.http_client import HttpClient


class BaseApi:
    def __init__(self, client: HttpClient):
        self.client = client
```

- [ ] **Step 4: Commit**

```bash
git add core/http_client.py apis/
git commit -m "feat: add HTTP client and base API layer"
```

---

### Task 6: 测试数据提供器

**Files:**
- Create: `core/data_provider.py`
- Create: `data/api/users.yaml`
- Create: `data/api/__init__.py` (empty, for package)

- [ ] **Step 1: 创建 core/data_provider.py**

```python
import json
from pathlib import Path
from typing import Any

import yaml


DATA_DIR = Path(__file__).parent.parent / "data"


def load_yaml(relative_path: str) -> dict[str, Any]:
    filepath = DATA_DIR / relative_path
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath) as f:
        return yaml.safe_load(f)


def load_json(relative_path: str) -> dict[str, Any]:
    filepath = DATA_DIR / relative_path
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath) as f:
        return json.load(f)
```

- [ ] **Step 2: 创建 data/api/users.yaml**

```yaml
valid_user:
  username: "testuser"
  password: "Test@123456"
  email: "testuser@example.com"

admin_user:
  username: "admin"
  password: "Admin@123456"
  email: "admin@example.com"

invalid_user:
  username: "invalid"
  password: "wrong"
  email: "invalid@example.com"
```

- [ ] **Step 3: 验证数据加载**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && python -c "
from core.data_provider import load_yaml
data = load_yaml('api/users.yaml')
print(data['valid_user']['username'])
"
```

Expected: `testuser`

- [ ] **Step 4: Commit**

```bash
git add core/data_provider.py data/
git commit -m "feat: add test data provider with YAML/JSON support"
```

---

### Task 7: 认证 fixtures

**Files:**
- Create: `fixtures/__init__.py`
- Create: `fixtures/auth_fixtures.py`

- [ ] **Step 1: 创建 fixtures/__init__.py**

```python
```

- [ ] **Step 2: 创建 fixtures/auth_fixtures.py**

```python
import pytest

from core.data_provider import load_yaml


@pytest.fixture(scope="session")
def valid_credentials():
    return load_yaml("api/users.yaml")["valid_user"]


@pytest.fixture(scope="session")
def admin_credentials():
    return load_yaml("api/users.yaml")["admin_user"]


@pytest.fixture(scope="session")
def auth_token(config, valid_credentials):
    import requests

    resp = requests.post(
        f"{config.api.base_url}/auth/login",
        json={
            "username": valid_credentials["username"],
            "password": valid_credentials["password"],
        },
        timeout=config.api.timeout,
    )
    if resp.status_code == 200:
        return resp.json().get("token", "")
    return ""
```

- [ ] **Step 3: Commit**

```bash
git add fixtures/
git commit -m "feat: add shared auth fixtures"
```

---

### Task 8: API 测试层 conftest 和示例用例

**Files:**
- Create: `apis/user_api.py`
- Create: `tests/conftest.py`
- Create: `tests/api/__init__.py`
- Create: `tests/api/conftest.py`
- Create: `tests/api/test_user.py`

- [ ] **Step 1: 创建 apis/user_api.py**

```python
from typing import Any

from apis.base_api import BaseApi


class UserApi(BaseApi):
    def login(self, username: str, password: str) -> dict[str, Any]:
        resp = self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        return resp.json()

    def get_profile(self, user_id: str) -> dict[str, Any]:
        resp = self.client.get(f"/users/{user_id}")
        return resp.json()

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.post("/users", json=payload)
        return resp.json()

    def update_user(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.put(f"/users/{user_id}", json=payload)
        return resp.json()

    def delete_user(self, user_id: str) -> dict[str, Any]:
        resp = self.client.delete(f"/users/{user_id}")
        return resp.json()
```

- [ ] **Step 2: 创建 tests/conftest.py**

```python
import pytest

from core.http_client import HttpClient


@pytest.fixture(scope="session")
def http_client(config):
    client = HttpClient(
        base_url=config.api.base_url,
        timeout=config.api.timeout,
    )
    yield client
    client.close()
```

- [ ] **Step 3: 创建 tests/api/conftest.py**

```python
import pytest

from apis.user_api import UserApi


@pytest.fixture(scope="module")
def user_api(http_client):
    return UserApi(http_client)
```

- [ ] **Step 4: 创建 tests/api/test_user.py**

```python
import pytest


@pytest.mark.api
@pytest.mark.p0
class TestUserLogin:
    def test_login_success(self, user_api, valid_credentials):
        resp = user_api.login(
            username=valid_credentials["username"],
            password=valid_credentials["password"],
        )
        assert "token" in resp or resp.get("status") == "ok"

    def test_login_failure(self, user_api):
        resp = user_api.login(
            username="invalid_user",
            password="wrong_password",
        )
        assert resp.get("status") == "error" or "token" not in resp


@pytest.mark.api
@pytest.mark.p1
class TestUserProfile:
    def test_get_profile_unauthorized(self, user_api):
        resp = user_api.get_profile("1")
        assert resp.get("status") == "error"
```

- [ ] **Step 5: 运行 API 测试（预期部分失败，因为 API 不存在）**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest tests/api/ -v --no-header
```

Expected: 测试会被收集并执行。由于没有真实后端，测试会因连接失败而 ERROR，这验证了框架结构正确。后续接入真实 API 后，测试可正常运行。

- [ ] **Step 6: 验证 marker 筛选**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest tests/api/ -m "api and p0" -v
```

Expected: 只收集到 TestUserLogin 中的 2 条用例。

- [ ] **Step 7: Commit**

```bash
git add apis/user_api.py tests/conftest.py tests/api/
git commit -m "feat: add API test layer with example user tests"
```

---

### Task 9: Web 测试层 — Page Object Model 基础

**Files:**
- Create: `pages/__init__.py`
- Create: `pages/base_page.py`
- Create: `pages/login_page.py`
- Create: `tests/web/__init__.py`
- Create: `tests/web/conftest.py`
- Create: `tests/web/test_login.py`
- Create: `data/web/__init__.py`
- Create: `data/web/users.yaml`

- [ ] **Step 1: 创建 pages/__init__.py**

```python
```

- [ ] **Step 2: 创建 pages/base_page.py**

```python
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
```

- [ ] **Step 3: 创建 pages/login_page.py**

```python
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
```

- [ ] **Step 4: 创建 data/web/users.yaml**

```yaml
valid_user:
  username: "testuser"
  password: "Test@123456"

invalid_user:
  username: "invalid"
  password: "wrong"

login_scenarios:
  - username: ""
    password: ""
    expected_error: "Username is required"
  - username: "testuser"
    password: ""
    expected_error: "Password is required"
  - username: "invalid"
    password: "wrong"
    expected_error: "Invalid credentials"
```

- [ ] **Step 5: 创建 tests/web/conftest.py**

```python
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser(config):
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
```

- [ ] **Step 6: 创建 tests/web/test_login.py**

```python
import pytest

from core.data_provider import load_yaml
from pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.p0
class TestLogin:
    def test_login_success(self, page, config):
        data = load_yaml("web/users.yaml")["valid_user"]
        login_page = LoginPage(page)
        login_page.navigate(config.web.base_url)
        login_page.login(data["username"], data["password"])
        assert login_page.is_login_success()

    def test_login_failure(self, page, config):
        data = load_yaml("web/users.yaml")["invalid_user"]
        login_page = LoginPage(page)
        login_page.navigate(config.web.base_url)
        login_page.login(data["username"], data["password"])
        assert login_page.is_visible(LoginPage.ERROR_MESSAGE)


@pytest.mark.web
@pytest.mark.p1
class TestLoginValidation:
    @pytest.mark.parametrize(
        "username,password,expected_error",
        load_yaml("web/users.yaml")["login_scenarios"],
    )
    def test_login_validation(self, page, config, username, password, expected_error):
        login_page = LoginPage(page)
        login_page.navigate(config.web.base_url)
        login_page.login(username, password)
        assert expected_error in login_page.get_error_message()
```

- [ ] **Step 7: 安装 Playwright 浏览器**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && playwright install chromium
```

- [ ] **Step 8: 验证 Web 测试可被收集**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest tests/web/ --collect-only -v
```

Expected: 列出所有 Web 测试用例（不执行）。

- [ ] **Step 9: Commit**

```bash
git add pages/ tests/web/ data/web/
git commit -m "feat: add Web test layer with Page Object Model"
```

---

### Task 10: App 测试层 — Screen Object Model 基础

**Files:**
- Create: `screens/__init__.py`
- Create: `screens/base_screen.py`
- Create: `screens/home_screen.py`
- Create: `tests/mobile/__init__.py`
- Create: `tests/mobile/conftest.py`
- Create: `tests/mobile/test_home.py`
- Create: `data/mobile/__init__.py`
- Create: `data/mobile/test_data.yaml`

- [ ] **Step 1: 创建 screens/__init__.py**

```python
```

- [ ] **Step 2: 创建 screens/base_screen.py**

```python
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BaseScreen:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find_element(self, by: str, value: str):
        return self.wait.until(
            EC.presence_of_element_located((by, value))
        )

    def find_elements(self, by: str, value: str):
        return self.wait.until(
            EC.presence_of_all_elements_located((by, value))
        )

    def click(self, by: str, value: str) -> None:
        self.find_element(by, value).click()

    def get_text(self, by: str, value: str) -> str:
        return self.find_element(by, value).text

    def is_displayed(self, by: str, value: str) -> bool:
        try:
            return self.driver.find_element(by, value).is_displayed()
        except Exception:
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
```

- [ ] **Step 3: 创建 screens/home_screen.py**

```python
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By

from screens.base_screen import BaseScreen


class HomeScreen(BaseScreen):
    HEADER = (By.ID, "com.example:id/header")
    MENU_BUTTON = (By.ACCESSIBILITY_ID, "menu")
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
```

- [ ] **Step 4: 创建 data/mobile/test_data.yaml**

```yaml
home_screen:
  expected_header: "Home"
  expected_greeting: "Welcome"

login_scenarios:
  - username: "testuser"
    password: "Test@123456"
    expected: "success"
  - username: "invalid"
    password: "wrong"
    expected: "error"
```

- [ ] **Step 5: 创建 tests/mobile/conftest.py**

```python
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
def appium_driver(config, platform):
    server_url = config.mobile.appium_server

    if platform == "android":
        options = UiAutomator2Options()
        options.platform_version = config.mobile.platform_version
        options.automation_name = "UiAutomator2"
    else:
        options = XCUITestOptions()
        options.platform_version = config.mobile.platform_version
        options.automation_name = "XCUITest"

    driver = webdriver.Remote(server_url, options=options)
    yield driver
    driver.quit()
```

- [ ] **Step 6: 创建 tests/mobile/test_home.py**

```python
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
```

- [ ] **Step 7: 验证 Mobile 测试可被收集**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest tests/mobile/ --collect-only -v
```

Expected: 列出所有 Mobile 测试用例（不执行，因为无 Appium server）。

- [ ] **Step 8: Commit**

```bash
git add screens/ tests/mobile/ data/mobile/
git commit -m "feat: add App test layer with Screen Object Model"
```

---

### Task 11: 清理 dummy test 并验证全量收集

**Files:**
- Remove: `tests/test_skeleton.py`

- [ ] **Step 1: 删除骨架测试**

```bash
rm /Users/remiges/project/python/test/tests/test_skeleton.py
```

- [ ] **Step 2: 验证全量测试收集**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest --collect-only -v
```

Expected: 列出所有 API + Web + Mobile 测试用例，markers 正确标注。

- [ ] **Step 3: 验证 marker 组合筛选**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest --collect-only -m "p0" -v
```

Expected: 只列出 p0 标记的用例。

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && pytest --collect-only -m "api or web" -v
```

Expected: 列出 API 和 Web 用例，不含 Mobile。

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "chore: remove skeleton test, verify full collection"
```

---

### Task 12: 最终项目结构验证

**Files:** (none, verification only)

- [ ] **Step 1: 确认最终目录结构**

```bash
cd /Users/remiges/project/python/test && find . -not -path './.venv/*' -not -path './.git/*' -not -name '*.pyc' -not -path './__pycache__/*' | sort
```

Expected 结构:
```
.
./config
./config/dev.yaml
./config/prod.yaml
./config/staging.yaml
./conftest.py
./core
./core/__init__.py
./core/config_loader.py
./core/data_provider.py
./core/http_client.py
./core/logger.py
./data
./data/api
./data/api/users.yaml
./data/mobile
./data/mobile/test_data.yaml
./data/web
./data/web/users.yaml
./apis
./apis/__init__.py
./apis/base_api.py
./apis/user_api.py
./docs
./docs/superpowers
./docs/superpowers/plans
./docs/superpowers/specs
./fixtures
./fixtures/__init__.py
./fixtures/auth_fixtures.py
./pages
./pages/__init__.py
./pages/base_page.py
./pages/login_page.py
./pyproject.toml
./screens
./screens/__init__.py
./screens/base_screen.py
./screens/home_screen.py
./tests
./tests/__init__.py
./tests/api
./tests/api/__init__.py
./tests/api/conftest.py
./tests/api/test_user.py
./tests/conftest.py
./tests/mobile
./tests/mobile/__init__.py
./tests/mobile/conftest.py
./tests/mobile/test_home.py
./tests/web
./tests/web/__init__.py
./tests/web/conftest.py
./tests/web/test_login.py
```

- [ ] **Step 2: 确认所有 import 无语法错误**

```bash
cd /Users/remiges/project/python/test && source .venv/bin/activate && python -c "
from core.config_loader import load_config
from core.http_client import HttpClient
from core.data_provider import load_yaml, load_json
from core.logger import setup_logging, get_logger
from apis.base_api import BaseApi
from apis.user_api import UserApi
from pages.base_page import BasePage
from pages.login_page import LoginPage
from screens.base_screen import BaseScreen
from screens.home_screen import HomeScreen
print('All imports OK')
"
```

Expected: `All imports OK`

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "chore: final project structure verification"
```
