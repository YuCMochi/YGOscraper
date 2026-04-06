## 1. 實測 items/v2 level=detail API

- [x] 1.1 手動對一個已知有複數選項的商品呼叫 `items/v2/list?gno={id}&level=detail`，確認 sub_items 的實際 JSON 結構（鍵名、子商品是否有獨立 ID）
- [x] 1.2 確認子商品的 product_id 格式，決定是否需要用 `{parent_id}_{index}` 組合

## 2. ruten_scraper.py：核心修改

- [x] 2.1 `_extract_product_data()` 的 `alt_price` 回傳值從 `0/1` 整數改為 `False/True` 布林值
- [x] 2.2 新增 `_fetch_item_detail_async(product_id: str) -> dict | None`：呼叫 items/v2 level=detail，失敗時回傳 None
- [x] 2.3 新增 `_expand_variants(parent_product: dict, sub_items: list) -> list[dict]`：將 sub_items 展開為多筆商品 dict，`alt_price=False`，其餘欄位（seller_id、image_url 等）繼承父商品
- [x] 2.4 修改 `_process_products_async()`：第一階段結束後，對 `alt_price=True` 的商品逐一 await `_fetch_item_detail_async()`，展開後取代原始列；API 失敗時保留原始列並記錄警告

## 3. cleaner_service.py：同步修改

- [x] 3.1 將 `alt_price == "1"` 的判斷改為 `alt_price == "True"`

## 4. 驗證

- [x] 4.1 用含複數選項商品的購物車跑一次完整爬蟲，確認展開後子商品出現在 ruten_data.csv 且 alt_price 為 "False"
- [x] 4.2 確認單一選項商品不受影響（不呼叫 items/v2）
- [x] 4.3 跑完整 run 流程（scrape → clean → calculate），確認展開後的子商品能進入計算結果
