## 1. 測試基礎設施

- [x] 1.1 建立 `tests/` 目錄結構（`conftest.py`, `fixtures/`, `unit/`, `api/`, `integration/`）
- [x] 1.2 建立 `pyproject.toml`，設定 pytest（testpaths, markers, asyncio_mode）和 ruff
- [x] 1.3 安裝 dev dependencies（pytest, pytest-asyncio, httpx, ruff）到 requirements-dev.txt
- [x] 1.4 建立 `tests/fixtures/` 中的靜態測試資料（sample_cart.json, sample_ruten_data.csv）
- [x] 1.5 建立 `tests/conftest.py`，設定共用 fixtures（tmp_dir, sample cart data, mock file I/O）

## 2. Unit Tests — Schemas

- [x] 2.1 建立 `tests/unit/test_schemas.py`：CartItemFull 合法資料驗證
- [x] 2.2 CartItemFull 拒絕 required_amount ≤ 0
- [x] 2.3 CartData 預設值驗證（default_shipping_cost = 60 等）

## 3. Unit Tests — Cleaner Service

- [x] 3.1 建立 `tests/unit/test_cleaner.py`：黑名單賣家過濾
- [x] 3.2 價格異常過濾（> 5000）
- [x] 3.3 eBay 商品過濾（product_name 及 image_url）
- [x] 3.4 排除關鍵字過濾
- [x] 3.5 卡號精確匹配（SD5 不匹配 YSD5）
- [x] 3.6 重複商品去重（相同 product_id）

## 4. Unit Tests — Calculator Service

- [x] 4.1 建立 `tests/unit/test_calculator.py`：單賣家最佳解
- [x] 4.2 多賣家最佳解（含運費比較）
- [x] 4.3 庫存不足拋出 RuntimeError
- [x] 4.4 最低消費門檻限制

## 5. API Tests

- [x] 5.1 建立 `tests/api/test_health.py`：GET /health 回傳 200

## 6. Integration Tests（外部 API Smoke Tests）

- [x] 6.1 建立 `tests/integration/test_scrapers.py`：Konami DB 頁面解析 smoke test（標記 @pytest.mark.integration）
- [x] 6.2 Ruten 搜尋 API 解析 smoke test（標記 @pytest.mark.integration）
- [x] 6.3 建立 `tests/integration/test_external_resources.py`：cards.cdb 下載 + SQLite header 驗證
- [x] 6.4 cid_table.json 下載 + JSON 解析驗證
- [x] 6.5 卡圖 URL 可存取驗證（用已知 passcode）

## 7. GitHub Actions — PR CI Workflow

- [x] 7.1 建立 `.github/workflows/ci.yml`
- [x] 7.2 設定 backend-lint job（ruff check）
- [x] 7.3 設定 backend-test job（pytest -m "not integration"）
- [x] 7.4 設定 frontend-lint job（npm run lint）
- [x] 7.5 設定 frontend-build job（npm run build）

## 8. GitHub Actions — Integration Workflow

- [x] 8.1 建立 `.github/workflows/integration.yml`
- [x] 8.2 設定 schedule (cron: 每日 UTC 00:00) + workflow_dispatch 觸發
- [x] 8.3 設定 scraper-smoke-test job（pytest -m integration）
- [x] 8.4 設定失敗時自動建立 GitHub Issue

## 9. 驗證

- [x] 9.1 本地執行 `pytest -m "not integration"` 全部通過
- [x] 9.2 本地執行 `ruff check .` 全部通過
- [x] 9.3 確認 `.gitignore` 包含 pytest 相關快取（`.pytest_cache/`, `__pycache__/`）
