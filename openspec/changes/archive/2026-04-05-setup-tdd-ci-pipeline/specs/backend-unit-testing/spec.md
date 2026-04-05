## ADDED Requirements

### Requirement: pytest 測試基礎設施
系統 SHALL 有完整的 pytest 測試基礎設施，包含 `conftest.py`（共用 fixtures）、`tests/fixtures/` 目錄（靜態測試資料）、以及 `pyproject.toml` 中的 pytest 設定。

#### Scenario: 執行所有 unit tests
- **WHEN** 開發者在專案根目錄執行 `pytest -m "not integration"`
- **THEN** 所有非 integration 的 unit tests 和 API tests SHALL 被執行且全部通過

#### Scenario: 測試資料隔離
- **WHEN** 任何 test case 執行時
- **THEN** SHALL 不依賴外部檔案系統、外部 API、或真實的 `data/` 目錄

---

### Requirement: Calculator Service 測試
系統 SHALL 為 `PurchaseOptimizer` 提供 unit tests，覆蓋核心最佳化邏輯。

#### Scenario: 單賣家最佳解
- **WHEN** 市場只有一個賣家，且庫存足以滿足所有需求
- **THEN** 計算結果 SHALL 只使用該賣家，總金額 = 商品價格 + 一次運費

#### Scenario: 多賣家最佳解
- **WHEN** 多賣家有不同價格，跨賣家組合更便宜
- **THEN** 計算結果 SHALL 選出總成本（含運費）最低的組合

#### Scenario: 庫存不足報錯
- **WHEN** 市場總庫存不足以滿足需求
- **THEN** SHALL 拋出 `RuntimeError`

#### Scenario: 最低消費門檻
- **WHEN** 設定了 `min_purchase_limit`
- **THEN** 每個被選中的賣家 SHALL 達到最低消費門檻

---

### Requirement: Cleaner Service 測試
系統 SHALL 為 `DataCleaner` 提供 unit tests，覆蓋所有過濾規則。

#### Scenario: 黑名單賣家過濾
- **WHEN** CSV 中有黑名單賣家的商品
- **THEN** 清洗後結果 SHALL 不包含該賣家的任何商品

#### Scenario: 價格異常過濾
- **WHEN** 商品價格超過 5000 元
- **THEN** 該商品 SHALL 被過濾掉

#### Scenario: eBay 商品過濾
- **WHEN** 商品名稱或圖片 URL 包含 "ebay"
- **THEN** 該商品 SHALL 被過濾掉

#### Scenario: 排除關鍵字過濾
- **WHEN** 商品名稱包含排除關鍵字（如 "卡套"）
- **THEN** 該商品 SHALL 被過濾掉

#### Scenario: 卡號精確匹配
- **WHEN** 目標卡號為 "SD5" 且商品名稱包含 "YSD5"
- **THEN** 該商品 SHALL 被過濾掉（不匹配子字串）

#### Scenario: 重複商品去重
- **WHEN** 原始 CSV 中有相同 `product_id` 的重複列
- **THEN** 清洗結果 SHALL 只保留第一筆

---

### Requirement: Pydantic Schema 測試
系統 SHALL 為 `app/schemas.py` 提供 unit tests，驗證資料模型的 validation 行為。

#### Scenario: CartItemFull 接受合法資料
- **WHEN** 提供必填欄位（card_name_zh, required_amount）以及選填欄位
- **THEN** SHALL 成功建立 model 且值正確

#### Scenario: CartItemFull 拒絕不合法數量
- **WHEN** `required_amount` 為 0 或負數
- **THEN** SHALL 拋出 `ValidationError`

#### Scenario: CartData 預設值
- **WHEN** 只傳入空的 `shopping_cart`
- **THEN** `global_settings` 和 `cart_settings` SHALL 使用預設值（例如 `default_shipping_cost = 60`）

---

### Requirement: FastAPI Router API Contract 測試
系統 SHALL 為 `/health` endpoint 提供基本的 API contract test。

#### Scenario: Health check 回傳 200
- **WHEN** 發送 GET 到 `/health`
- **THEN** response status code SHALL 為 200
