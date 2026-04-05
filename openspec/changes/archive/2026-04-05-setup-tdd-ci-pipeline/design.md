## Context

YGOscraper 是一個遊戲王卡片採購最佳化工具。Backend 用 Python + FastAPI，Frontend 用 React + Vite + Tailwind。目前沒有任何自動化測試和 CI 流程。

專案架構：
- `server.py` → FastAPI 入口，lifespan 管理 `CardDatabaseService`
- `app/routers/` → API endpoints（projects, cart, cards, tasks, health, settings）
- `app/services/` → Business logic（calculator, cleaner, scraper, storage, card_db, project）
- `app/schemas.py` → Pydantic 資料模型
- `frontend/` → React + Vite（scripts: dev, build, lint, preview）

外部依賴：Konami 官方資料庫（爬卡號/稀有度）、露天拍賣（爬商品價格）。

## Goals / Non-Goals

**Goals:**
- 建立 pytest 測試基礎設施，讓新 code 可以 TDD 開發
- 為核心 service（calculator, cleaner）和 schemas 寫出基礎 unit tests
- 為 FastAPI routers 建立 API contract tests（用 httpx + TestClient）
- 建立 GitHub Actions CI workflow：PR 時自動跑 lint + test + frontend build
- 建立 GitHub Actions scheduled workflow：定期驗證外部 API 回傳格式
- 所有測試都用 mock 隔離外部依賴

**Non-Goals:**
- 不回頭補所有舊 code 的 test（只測核心 service）
- 不建立 Frontend 的 unit test framework（Vitest）
- 不做 E2E browser testing（Playwright / Cypress）
- 不修改現有 application code

## Decisions

### Decision 1: 測試框架選 pytest + pytest-asyncio

**選擇**: pytest  
**理由**: Python 生態系標準，fixture 系統強大，FastAPI 官方推薦搭配使用  
**替代方案**: unittest（太囉嗦），nose2（生態系小）

### Decision 2: FastAPI 測試用 httpx.AsyncClient

**選擇**: httpx.AsyncClient + ASGITransport  
**理由**: FastAPI 官方推薦做法，支援 async endpoints 和 lifespan events，不需要實際啟動 server  
**替代方案**: requests + TestClient（同步版，不支援 async lifespan）

### Decision 3: Mock 策略 — unittest.mock + fixtures

**選擇**: 用 `unittest.mock.patch` mock 外部依賴（檔案 I/O、外部 HTTP）  
**理由**: 不需要額外裝 library，pytest 原生支援。fixtures 放在 `conftest.py` 統一管理測試資料  
**替代方案**: responses library（只管 HTTP mock），pytest-mock（多一層包裝，不必要）

### Decision 4: CI 拆成兩個 workflow

**PR CI (`ci.yml`)**:
```yaml
trigger: pull_request → main
jobs:
  - backend-lint (ruff)
  - backend-test (pytest)
  - frontend-lint (eslint)
  - frontend-build (vite build)
```

**Integration CI (`integration.yml`)**:
```yaml
trigger: schedule (cron: 每日 UTC 00:00) + workflow_dispatch
jobs:
  - scraper-smoke-test (打真實外部 API、驗證回傳 HTML 結構)
```

**理由**: 外部 API 不穩定，不能綁在 PR 上。定期跑 + 手動觸發，壞了發 GitHub Issue

### Decision 5: 目錄結構

```
tests/
  ├── conftest.py               ← 共用 fixtures, pytest config
  ├── fixtures/                 ← 測試用的靜態資料檔案
  │     ├── sample_cart.json
  │     ├── sample_ruten_data.csv
  │     └── sample_cleaned_data.csv
  ├── unit/
  │     ├── test_calculator.py  ← PurchaseOptimizer
  │     ├── test_cleaner.py     ← DataCleaner
  │     └── test_schemas.py     ← Pydantic models
  ├── api/
  │     ├── test_health.py      ← /health endpoints
  │     └── test_projects.py    ← /projects endpoints
  └── integration/
        └── test_scrapers.py    ← 打真實外部 API（只在 scheduled CI 跑）
```

### Decision 6: pytest 設定放在 pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: marks tests that hit real external APIs (deselect with '-m \"not integration\"')"
]
asyncio_mode = "auto"
```

用 `pytest -m "not integration"` 來跳過外部 API tests。CI PR workflow 也用這個 marker 排除。

### Decision 7: Linter 選 Ruff

**選擇**: ruff  
**理由**: 超快（Rust 寫的）、整合 flake8 + isort + pyflakes 到一個工具。GitHub Actions 有官方 action  
**替代方案**: flake8 + isort（要管兩個工具），pylint（太慢太囉嗦）

## Risks / Trade-offs

- **[卡片資料庫依賴]** → `CardDatabaseService` 需要 `cards.cdb` 和 `cid_table.json`，API tests 需要 mock 或用最小化的 test db。先用 mock 處理。
- **[外部 API 格式變更]** → Konami / Ruten 隨時可能改 HTML 結構，integration tests 只能驗證「現在的格式」。→ scheduled CI 壞了就自動開 issue 追蹤。
- **[初始覆蓋率低]** → 只測核心邏輯，不量化覆蓋率目標。TDD 是漸進的，先建基礎設施最重要。
