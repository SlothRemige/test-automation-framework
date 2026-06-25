# Test Automation Framework

Multi-platform test automation framework supporting Web, App (Android/iOS), and API testing.

## Quick Start

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium

# Run tests
pytest tests/api/ -v              # API tests (16 pass)
pytest tests/web/ -v              # Web tests (5 pass, headless)
pytest tests/mobile/ -v           # Mobile tests (needs Appium server)
./run_tests.sh parallel           # All tests in parallel
```

## Project Structure

```
├── config/              # Multi-environment configs (dev/staging/prod)
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── core/                # Shared infrastructure
│   ├── config_loader.py   # YAML + pydantic config loading
│   ├── http_client.py     # requests.Session wrapper with retry
│   ├── logger.py          # structlog setup
│   └── data_provider.py   # YAML/JSON test data loader
├── apis/                # API client layer
│   ├── base_api.py        # Base API class
│   └── user_api.py        # User API client
├── pages/               # Web Page Object Model
│   ├── base_page.py       # Base page (Playwright)
│   └── login_page.py      # Login page
├── screens/             # Mobile Screen Object Model
│   ├── base_screen.py     # Base screen (Appium)
│   └── home_screen.py     # Home screen
├── fixtures/            # Shared pytest fixtures
│   └── auth_fixtures.py   # Auth token and credentials
├── data/                # Test data (YAML)
│   ├── api/users.yaml
│   ├── web/users.yaml
│   └── mobile/test_data.yaml
├── tests/
│   ├── conftest.py        # HTTP client fixture
│   ├── api/               # API tests (16 pass)
│   ├── web/               # Web tests (5 pass)
│   └── mobile/            # Mobile tests (needs Appium)
├── conftest.py           # Root: --env, app_config, logging
├── pyproject.toml        # Dependencies + pytest config
└── run_tests.sh          # Test runner with Allure support
```

## Configuration

Switch environments via `--env` flag:

```bash
pytest tests/api/ --env=staging
pytest tests/ --env=prod
```

Config files: `config/dev.yaml`, `config/staging.yaml`, `config/prod.yaml`.

## Test Markers

| Marker | Description |
|--------|-------------|
| `smoke` | Smoke tests |
| `p0` | Critical path |
| `p1` | Important features |
| `p2` | Edge cases |
| `web` | Web tests |
| `api` | API tests |
| `mobile` | Mobile tests |

```bash
pytest tests/ -m "api and p0"       # API critical path only
pytest tests/ -m "web or api"       # Web + API, skip mobile
pytest tests/ -m "smoke"            # Smoke tests only
```

## Allure Report

```bash
./run_tests.sh api                  # Run API tests with Allure
./run_tests.sh report               # Generate HTML report
open allure-report/index.html       # View in browser
```

## Parallel Execution

```bash
./run_tests.sh parallel             # All tests in parallel (auto workers)
pytest tests/api/ -n auto           # API tests only
```

## Mock Strategy

- **API**: `responses.RequestsMock` in `tests/api/conftest.py::mock_api`
- **Web**: `page.route()` in `tests/web/conftest.py::mock_web_login`
- **Mobile**: Needs Appium server (not yet mocked)

## Requirements

- Python >=3.11
- Chromium (for Web tests): `playwright install chromium`
- Appium server (for Mobile tests, optional)
