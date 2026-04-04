## ADDED Requirements

### Requirement: Scheduled Integration Workflow
系統 SHALL 有一個 GitHub Actions workflow (`integration.yml`)，定期驗證外部 API 的可用性與回傳格式。

#### Scenario: 定時觸發
- **WHEN** UTC 每日 00:00
- **THEN** integration workflow SHALL 自動執行

#### Scenario: 手動觸發
- **WHEN** 開發者在 GitHub Actions 頁面手動觸發 `workflow_dispatch`
- **THEN** integration workflow SHALL 執行

---

### Requirement: Konami API Smoke Test
Integration workflow SHALL 驗證 Konami 官方資料庫的回傳格式沒有改變。

#### Scenario: Konami 回傳正常
- **WHEN** 發送請求到 Konami DB 取得已知卡片的頁面
- **THEN** SHALL 能正確解析出卡號與稀有度資訊

#### Scenario: Konami 回傳格式異常
- **WHEN** Konami 網頁的 HTML 結構變更導致解析失敗
- **THEN** test SHALL 失敗

---

### Requirement: Ruten API Smoke Test
Integration workflow SHALL 驗證露天拍賣搜尋 API 的回傳格式沒有改變。

#### Scenario: Ruten 搜尋回傳正常
- **WHEN** 發送搜尋請求到露天拍賣 API
- **THEN** SHALL 能正確解析出商品列表（含 product_id, price, seller_id 等欄位）

#### Scenario: Ruten 回傳格式異常
- **WHEN** 露天拍賣 API 回傳結構變更
- **THEN** test SHALL 失敗

---

### Requirement: salix5 cards.cdb Smoke Test
Integration workflow SHALL 驗證 salix5/cdb GitHub Release 上的 `cards.cdb` 檔案可正常下載且為合法 SQLite 資料庫。

#### Scenario: cards.cdb 下載正常
- **WHEN** 發送 HTTP GET 到 `CARDS_CDB_URL`
- **THEN** response status SHALL 為 200，且下載內容的前 16 bytes SHALL 包含 SQLite magic header (`SQLite format 3`)

#### Scenario: cards.cdb 無法下載
- **WHEN** URL 回傳 404 或其他非 200 status
- **THEN** test SHALL 失敗

---

### Requirement: salix5 cid_table.json Smoke Test
Integration workflow SHALL 驗證 salix5/heliosphere 上的 `cid_table.json` 可正常下載且為合法 JSON。

#### Scenario: cid_table.json 格式正常
- **WHEN** 發送 HTTP GET 到 `CID_TABLE_URL`
- **THEN** response status SHALL 為 200，內容 SHALL 可被 JSON 解析，且為非空的 dict/list

#### Scenario: cid_table.json 格式異常
- **WHEN** response 內容無法被 JSON 解析
- **THEN** test SHALL 失敗

---

### Requirement: salix5 卡圖 Smoke Test
Integration workflow SHALL 驗證 salix5/query-data 上的卡圖 URL 可正常存取。

#### Scenario: 已知卡圖可下載
- **WHEN** 發送 HTTP GET 到 `CARD_IMAGE_BASE_URL` + 一個已知的 passcode（如 `89631139.jpg`）
- **THEN** response status SHALL 為 200，且 Content-Type SHALL 為 image 類型

#### Scenario: 卡圖 URL 失效
- **WHEN** URL 回傳 404
- **THEN** test SHALL 失敗

---

### Requirement: 失敗通知
當 integration tests 失敗時，系統 SHALL 自動建立 GitHub Issue 通知開發者。

#### Scenario: Integration test 失敗自動開 Issue
- **WHEN** scheduled integration workflow 有任一 test 失敗
- **THEN** SHALL 自動建立一個 GitHub Issue，標題包含 "External API format change detected"，body 包含失敗的 test 名稱和錯誤訊息
