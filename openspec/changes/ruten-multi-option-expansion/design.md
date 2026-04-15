## Context

目前 `RutenScraper._process_products_async()` 是單階段流程：搜尋 API → `_get_product_details_async()` → `_extract_product_data()`。複數選項商品（`PriceRange` 有多個不同值）被標記為 `alt_price=1`，在 cleaner 階段整筆排除，完全無法參與比價。

露天 `items/v2/list?gno={id}&level=detail` 可取得商品的 `sub_items[]` 陣列，每個子項目含獨立的名稱、價格、庫存。由於此 API 一次只支援單一商品查詢，僅對已標記 `alt_price=True` 的商品才觸發，避免全量呼叫。

## Goals / Non-Goals

**Goals:**
- 對 `alt_price=True` 的商品展開子選項為獨立資料列
- 展開後每筆子商品的 `alt_price=False`，可通過 cleaner 過濾
- `alt_price` 欄位值從整數 `0/1` 改為布林 `False/True`

**Non-Goals:**
- 不使用 items/v2 取得運費（單次查詢成本過高，不批量）
- 不修改 cleaner、calculator、API 端點的核心邏輯
- 不處理 #6 運費精算、#7 賣家 storeinfo

## Decisions

### 決策 1：第二階段僅對 alt_price 商品觸發

**選擇**：在 `_process_products_async()` 中，完成第一階段資料提取後，過濾出 `alt_price=True` 的商品再逐一呼叫 items/v2。

**替代方案**：全量打 items/v2（level=simple 或 detail）
**否決理由**：一次只能查一個商品，若對全部 550 筆打 API 成本過高，且多數商品無需此資訊。

### 決策 2：展開後子商品取代原商品（而非並列）

**選擇**：若商品有 sub_items，移除原始資料列，插入展開的子商品列。

**替代方案**：保留原始列 + 追加子商品列
**否決理由**：若兩者並存，原始列的 `alt_price=True` 仍會被 cleaner 排除，且會造成重複計算。取代更乾淨。

### 決策 3：alt_price 改為布林值

**選擇**：`_extract_product_data()` 回傳 `alt_price: bool`，CSV 儲存為 `True/False`。

**替代方案**：維持 `0/1` 整數
**否決理由**：整數語意不直觀（在我們的討論中已確認），改布林更清楚。cleaner 的判斷條件 `== "1"` 需同步改為 `== "True"`（CSV 讀回來是字串）。

### 決策 4：items/v2 呼叫採循序非同步，不並行

**選擇**：`for` loop 逐一 `await`，每次呼叫間加短暫 sleep。

**替代方案**：`asyncio.gather()` 並行所有 alt_price 商品
**否決理由**：alt_price 商品數量通常不多，且並行大量單次查詢可能觸發 rate limiting。循序呼叫更安全。

## Risks / Trade-offs

- **sub_items 結構未知**：items/v2 level=detail 的 `sub_items` 欄位格式需實測確認（鍵名、是否有空值）→ 加防禦性 `.get()` 存取，遇到解析失敗時保留原始資料列（fallback to alt_price=True）
- **展開後子商品的 product_id 重複**：子商品可能沿用父商品 ID，需確認 cleaner 的去重邏輯是否受影響 → 實作時確認 sub_items 是否有獨立 ID，若無則以 `{parent_id}_{index}` 組合
- **cleaner `alt_price == "1"` 判斷**：改為布林後 CSV 儲存為字串 `"True"`，需同步修改 cleaner 判斷條件

## Open Questions

~~- items/v2 level=detail 的 `sub_items` 實際 JSON 結構？（鍵名待實測確認）~~
~~- sub_items 中的子商品是否有獨立的商品 URL / product_id？~~

**已確認（2026-04-06 實測）：**
- 選項資料在 `data[0].spec_info.specs`（dict），非 `sub_items` 陣列
- 每個 spec 有 `spec_id`（字串）、`spec_name`、`spec_price`、`spec_num`（庫存）、`spec_status`（`"Y"`=可售）
- 子選項**無獨立 product_id**，使用 `{parent_id}_{spec_id}` 組合作為唯一識別
