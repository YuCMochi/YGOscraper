## Why

露天拍賣中部分商品含有複數選項（如不同稀有度），目前爬蟲只記錄 `alt_price=1` 並在 cleaner 階段整筆排除，導致這些商品完全無法參與比價。透過 items/v2 `level=detail` API 將複數選項展開為獨立資料列，可讓這些商品重新進入計算流程。

## What Changes

- 新增 `_fetch_item_detail_async()` 方法：對單一商品呼叫 `items/v2/list?gno={id}&level=detail`
- 新增 `_expand_variants()` 方法：將 sub_items 展開為多筆獨立商品資料列，`alt_price` 設為 `False`
- `_process_products_async()` 中，第一階段完成後針對 `alt_price=True` 的商品執行第二階段展開
- `alt_price` 欄位語意從 `0/1` 整數改為 `False/True` 布林值（`has_variants` 命名保留為內部處理語意）
- cleaner_service.py 的 `alt_price == "1"` 過濾邏輯：展開後的子商品 `alt_price=False`，自然通過此過濾，無需額外修改
- 移除運費相關的 items/v2 查詢計畫（一次只能查一個商品，批量成本過高）

## Capabilities

### New Capabilities

- `multi-option-expansion`: 對 alt_price 商品呼叫 items/v2 level=detail，將各選項展開為獨立資料列加入 CSV

### Modified Capabilities

（無，現有 spec 不涉及爬蟲內部欄位語意）

## Impact

- `app/services/ruten_scraper.py`：新增兩個方法，修改 `_process_products_async()` 主流程
- `ruten_data.csv` 結構：`alt_price` 欄位值由 `0/1` 改為 `False/True`；原本被排除的複數選項商品現在會展開後出現在 CSV 中
- `app/services/cleaner_service.py`：`alt_price == "1"` 判斷需同步改為判斷 `True`（小幅修改）
- 不影響 calculator_service.py、storage.py、API 端點
