## ADDED Requirements

### Requirement: 複數選項商品展開為獨立資料列
爬蟲 SHALL 對 `alt_price=True` 的商品呼叫 `items/v2/list?gno={id}&level=detail`，將 `sub_items` 陣列中的每個選項展開為獨立資料列，並以展開後的子商品取代原始商品列。展開後每筆子商品的 `alt_price` SHALL 設為 `False`。

#### Scenario: 正常展開複數選項
- **WHEN** 商品 PriceRange 有多個不同值（alt_price=True）
- **THEN** 爬蟲呼叫 items/v2 level=detail 取得 sub_items
- **THEN** 每個 sub_item 展開為獨立資料列（含各自的名稱、價格、庫存）
- **THEN** 展開後的子商品 alt_price=False，可通過 cleaner 的過濾

#### Scenario: items/v2 呼叫失敗或 sub_items 為空
- **WHEN** items/v2 API 呼叫失敗，或回傳的 sub_items 為空陣列
- **THEN** 保留原始商品列（alt_price=True），不丟棄任何資料
- **THEN** 記錄警告日誌

#### Scenario: 商品只有單一選項（alt_price=False）
- **WHEN** 商品 PriceRange 只有一個值，或最低價等於最高價
- **THEN** 不呼叫 items/v2，直接使用原始資料列

### Requirement: alt_price 欄位使用布林值
爬蟲輸出的 CSV SHALL 以 `True`/`False` 字串表示 `alt_price` 欄位，取代原本的 `1`/`0` 整數。cleaner_service.py 的過濾條件 SHALL 同步更新為判斷字串 `"True"`。

#### Scenario: 有價差商品的欄位值
- **WHEN** 商品展開前 alt_price 為 True（或展開失敗保留原始列）
- **THEN** CSV 中 alt_price 欄位值為字串 `"True"`

#### Scenario: 無價差或已展開商品的欄位值
- **WHEN** 商品為單一選項，或已成功展開為子商品列
- **THEN** CSV 中 alt_price 欄位值為字串 `"False"`

#### Scenario: cleaner 正確過濾未展開的複數選項商品
- **WHEN** cleaner 讀取 CSV，遇到 alt_price="True" 的資料列
- **THEN** 該列被排除，不進入 calculator
