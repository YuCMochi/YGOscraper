## Why

專案目前完全沒有自動化測試和 CI 流程。每次改 code 都靠人肉驗證，尤其 `calculator_service` 和 `cleaner_service` 的邏輯變複雜後，很容易改壞而不自知。同時也沒有 PR gate，任何 code 都能直接 merge。

## What Changes

- 建立 Python 測試基礎設施（pytest + fixtures + mock 策略）
- 為 backend 核心邏輯新增 unit tests（calculator、cleaner、schemas、router API contract）
- 建立 GitHub Actions CI workflow：PR 時跑 lint + test + frontend build
- 建立 GitHub Actions scheduled workflow：定期驗證外部依賴（Konami / Ruten / salix5 GitHub 資源）的可用性與格式
- Frontend 在 CI 中跑 ESLint + Vite build 驗證
- 新增 `conftest.py`、pytest config、測試目錄結構

## Capabilities

### New Capabilities
- `backend-unit-testing`: Python backend 的 unit test 基礎設施與測試案例（pytest、fixtures、mock 策略）
- `ci-pr-workflow`: GitHub Actions PR CI workflow — 跑 lint、unit test、frontend build
- `ci-integration-workflow`: GitHub Actions scheduled workflow — 定期打真實外部 API 驗證回傳格式

### Modified Capabilities
（無既有 spec 需要修改）

## Impact

- **新增檔案**：`tests/` 目錄、`.github/workflows/ci.yml`、`.github/workflows/integration.yml`、`pyproject.toml`（pytest 設定）
- **Dependencies**：新增 dev dependencies — `pytest`、`pytest-asyncio`、`httpx`（FastAPI TestClient）
- **Frontend**：不新增 test framework，只在 CI 中跑既有的 `lint` 和 `build` script
- **既有程式碼**：不修改，只新增測試檔案和 CI 設定
