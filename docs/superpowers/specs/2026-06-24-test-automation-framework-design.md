# 自动化测试框架设计方案

## 概述

构建一个纯 Python 生态的自动化测试框架，覆盖 Web、App（Android/iOS）、API 三类被测对象。采用分层单体架构，融合插件式模块化的边界意识和扁平结构的克制原则。

## 技术选型

| 类别 | 选型 | 版本 |
|------|------|------|
| 语言 | Python | >=3.11 |
| 测试框架 | pytest | >=8.3 |
| Web 驱动 | Playwright | >=1.48 |
| App 驱动 | Appium-Python-Client | >=4.0 |
| HTTP 客户端 | requests | >=2.32 |
| 配置管理 | PyYAML + pydantic-settings | YAML>=6.0, pydantic-settings>=2.0 |
| 日志 | structlog | >=24.0 |
| 并发 | pytest-xdist | >=3.6 |
| Mock | responses | >=0.25 |
| 断言增强 | pytest-check | >=2.0 |
| 报告 | allure-pytest | >=2.13 |
| 依赖管理 | uv 或 pdm | — |

## 目录结构

```
project/
├── pyproject.toml                    # 依赖管理
├── pytest.ini                        # pytest 全局配置
├── conftest.py                       # 根级：环境切换、全局 fixture
│
├── config/
│   ├── dev.yaml                      # 开发环境配置
│   ├── staging.yaml                  # 预发布环境配置
│   └── prod.yaml                     # 生产环境配置
│
├── data/                             # 测试数据，与代码物理隔离
│   ├── web/
│   ├── api/
│   └── mobile/
│
├── core/                             # 跨端共享基础设施
│   ├── config_loader.py              # YAML 加载 + 环境变量覆盖
│   ├── http_client.py                # 封装 requests.Session
│   ├── logger.py                     # structlog 封装
│   └── data_provider.py              # 数据加载 + 参数化
│
├── pages/                            # Web POM
│   ├── base_page.py
│   └── login_page.py
├── screens/                          # App Screen Object
│   ├── base_screen.py
│   └── home_screen.py
├── apis/                             # API 封装
│   ├── base_api.py
│   └── user_api.py
│
├── tests/
│   ├── conftest.py                   # 各端共享 fixture
│   ├── web/
│   │   ├── conftest.py               # Web 专属 fixture
│   │   └── test_login.py
│   ├── api/
│   │   ├── conftest.py               # API 专属 fixture
│   │   └── test_user.py
│   └── mobile/
│       ├── conftest.py               # Mobile 专属 fixture
│       └── test_home.py
│
└── fixtures/                         # 跨端共享 fixture
    ├── auth_fixtures.py
    └── db_fixtures.py
```

## 架构设计

### 分层职责

- **core/** — 跨端共享基础设施：配置加载、HTTP 客户端、日志、数据提供。薄层封装，不做独立 pip 包
- **pages/** — Web Page Object Model，封装页面元素定位和操作
- **screens/** — App Screen Object Model，封装移动端屏幕元素和操作
- **apis/** — API 客户端封装，封装请求构建和响应解析
- **tests/** — 测试用例，按端分目录，每端有独立 conftest.py
- **fixtures/** — 跨端共享的 pytest fixtures（认证、数据库等）
- **data/** — 测试数据 YAML/JSON 文件，与代码物理隔离
- **config/** — 多环境配置文件

### conftest 层级机制

```
根 conftest.py           → 全局 fixtures（--env 参数、环境切换）
tests/conftest.py        → 各端共享 fixtures
tests/web/conftest.py    → Web 专用（browser、page）
tests/api/conftest.py    → API 专用（client、base_url）
tests/mobile/conftest.py → Mobile 专用（driver）
```

子目录 conftest 自动继承父级 fixtures，无需显式导入。运行 `pytest tests/web/` 时，API 的 fixtures 不会被加载，天然隔离。

### 数据流

```
config/*.yaml → core/config_loader.py → conftest.py (fixtures) → tests
data/*.yaml   → core/data_provider.py → pytest parametrize  → tests
```

## 运行方式

```bash
pytest tests/web/ -m smoke          # Web 冒烟测试
pytest tests/api/ -k "login"        # API 登录相关用例
pytest tests/mobile/ --platform=ios # iOS App 测试
pytest tests/ -n 4                  # 全量回归，4 线程并行
pytest tests/ --env=staging         # 切换到 staging 环境
```

## 分阶段实施

| 阶段 | 周期 | 重点 | 产出 |
|------|------|------|------|
| Phase 1：骨架 | 1-2天 | core/config_loader、根 conftest、环境切换 | `pytest --env=dev` 跑通 dummy case |
| Phase 2：API MVP | 3-5天 | 完整 API 链路：data → fixture → test → assert | 一套 API 用例跑通 |
| Phase 3：Web + App | 5-7天 | Playwright + Appium，base_page/base_screen | 三端各有核心用例 |
| Phase 4：加固 | 持续 | allure 报告、并发、失败重试、CI | 团队规范文档 |

## pytest 配置

```ini
[pytest]
testpaths = tests
pythonpath = .
addopts = -v --strict-markers --tb=short
markers =
    smoke: 冒烟测试
    p0: 核心功能
    p1: 重要功能
    p2: 边缘场景
    web: Web端
    api: API端
    mobile: 移动端
```
