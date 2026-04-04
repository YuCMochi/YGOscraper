# Architecture Decisions

> 紀錄 YGOscraper 重要的設計決策，供 agent 開發時參考。

---

## 1. 運費計算：`default_shipping_cost`

**決策日期**：v0.3.0 前

**背景**：
露天 API 回傳的 `ShippingCost` 是所有運送方式中「最便宜的」（例如郵寄 40 元），
但多數使用者偏好超商取貨（約 60-65 元），不希望跑不同地方取不同包裹。

**決議**：MVP 階段使用統一的 `global_settings.default_shipping_cost`（預設 60 元）
作為所有賣家的運費，讓 calculator 線性規劃模型可以正常運作。

**後續計畫（v0.5.0 #6）**：
利用 items/v2 API 的 `deliver_way` 欄位取得每商品的完整運送方式與對應運費，
讓使用者選擇偏好的取貨方式，calculator 改為按實際運費計算。

---

## 2. 複數選項商品：`alt_price` 排除機制

**決策日期**：v0.2.0 前

**背景**：
露天拍賣允許賣家在單一商品中設定複數選項（如不同稀有度），各選項可有不同價格、
獨立庫存。但露天 API 回傳的 `StockQty` 和 `SoldQty` 是**所有選項的合併值**，
無法區分個別選項的庫存。

**決議（MVP 處理方式）**：
- `ruten_scraper.py`：用 `PriceRange` 首尾是否相同判斷是否有複數選項 → 標記 `alt_price=1`
- `cleaner_service.py`：過濾直接排除 `alt_price=1` 的商品

**已知盲點**：
若複數選項的價格剛好相同（例如兩種稀有度都賣 30 元），`PriceRange=[30,30]`，
`alt_price` 會是 `0`，不會被過濾掉，但庫存仍是合併的，可能導致 calculator 誤判庫存充足。

**後續計畫（v0.5.0 #5）**：
利用 items/v2 API 的 `level=detail` 取得每個選項的獨立資訊（名稱、價格、庫存），
將各選項拆成獨立資料列，取代 `alt_price` 排除機制。

---

## 3. 兩層設定架構：`global_settings` + `cart_settings`

**決策日期**：2026-03-25（決議採用方案 A）

**背景**：
`cart.json` 原本只有 `global_settings` 一層設定。
為支援「結果頁手動排除商品/商家 → 重新計算」功能，需要能在不汙染全域設定的情況下，
記錄「這次計算」的額外過濾條件。

**決議（方案 A：兩層設定架構）**：

```json
{
  "global_settings": {
    "default_shipping_cost": 60,
    "min_purchase_limit": 0,
    "global_exclude_keywords": [],
    "global_exclude_seller": []
  },
  "cart_settings": {
    "shipping_cost": null,
    "min_purchase": null,
    "exclude_keywords": ["額外的"],
    "exclude_seller": ["某賣家ID"]
  }
}
```

合併規則：
- 數值型（`shipping_cost`, `min_purchase`）：`cart_settings` 為 `null` = 繼承全域，有值 = 覆蓋
- 列表型（`exclude_keywords`, `exclude_seller`）：`effective = global + cart`（聯集合併）

**實作位置**：
- Schema：`app/schemas.py` 的 `CartSettings`
- 合併邏輯：`app/services/cleaner_service.py` 和 `app/services/calculator_service.py`
- API：`app/routers/tasks.py` 讀取合併後的 effective settings

**前端入口**：
- 全域設定：右上角齒輪 ⚙️ Modal（`GlobalSettingsModal.jsx`）
- 專案設定（`cart_settings`）：`ProjectDetail` 右欄設定面板
- 結果頁手動排除（v0.5.0 #8）：排除操作寫入 `cart_settings`
