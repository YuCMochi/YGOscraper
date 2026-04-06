# YGOscraper 開發計畫與進度追蹤（封存）

> **封存日期**：2026-04-04
> **狀態**：此文件已封存，不再更新。
>
> **遷移說明**：
> - 版本路線圖與功能追蹤 → [GitHub Issues & Milestones](https://github.com/YuCMochi/YGOscraper/issues)
> - 設計備註 → [`openspec/specs/architecture-decisions.md`](../openspec/specs/architecture-decisions.md)
> - 外部 API 參考 → [`openspec/specs/external-apis.md`](../openspec/specs/external-apis.md)
>
> 本文件保留歷史開發備忘錄（按日期）和目標檔案結構供參考。

## 🏗️ 目標檔案結構

完成所有階段後，專案應呈現以下結構：

```
YGOscraper/
├── server.py                    # 入口 (~50行)
├── app/
│   ├── __init__.py
│   ├── config.py                # 外部 URL 統一管理
│   ├── schemas.py               # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── cart.py
│   │   ├── cards.py
│   │   ├── tasks.py
│   │   ├── health.py            # v0.3.0 外部依賴健康檢查
│   │   └── settings.py          # v0.3.0 全域設定 CRUD
│   └── services/
│       ├── __init__.py
│       ├── card_db.py           # 卡片資料庫服務 (預留自建DB替換)
│       ├── storage.py           # 專案檔案讀寫 + 全域設定管理
│       ├── ruten_scraper.py     # 露天爬蟲
│       ├── konami_scraper.py    # Konami 爬蟲
│       ├── cleaner_service.py   # 資料清洗
│       ├── calculator_service.py # 最佳組合計算
│       └── project_service.py   # 專案建立管理
├── frontend/                    # React 前端
├── docs/                        # 開發文件（本文件所在處）
├── data/
│   └── global_settings.json     # v0.3.0 全域設定（獨立於專案）
└── _legacy/                     # 舊版系統
```

---

## 📝 開發備忘錄

### 2026-03-31
- v0.4.1 完成：把稀有度 badge 的原生 title tooltip 換成自訂 CSS tooltip，顯示三行格式
- v0.4.0 完成：稀有度重構 + 並行 Bug 修復 + 兩層專案設定
- `rarity_name` → `rarity_id`（Konami DB 的 rid），前端標籤分色 + hover tooltip
- 並行加入購物車 race condition 修復（writeQueue + mutex）
- `CartSettings` 兩層架構實作：數值型覆蓋、列表型聯集
- 清除舊版 cart.json 資料（breaking change，不遷移）
- 稀有度對照表新增 rid 14, 22, 30, 31, 32

### 2026-03-28
- v0.3.1 前端 Bug 修復 6 項 + 刪除專案功能
- 全域設定從側邊欄移至右上角齒輪 Modal（`GlobalSettingsPanel.jsx` → `GlobalSettingsModal.jsx`）
- 數字輸入框改用 `type="text" inputMode="numeric"` + 自訂 ±10 Stepper，修復刪不掉開頭 0 的 bug
- Tag 輸入重複時也清空輸入框
- ProjectDetail 右欄「全域設定」改名為「專案設定」+ v0.4.0 註記
- 新增「查看結果」按鈕（`BarChart3` icon），可回頭查看已計算的結果
- 新增專案刪除功能：hover 顯示 🗑️、`DELETE /api/projects/{id}`、軟刪至 `_legacy/trash/`
- `storage.py` 新增 `delete_project()` 函數
- Bug 5（稀有度分色）擱置，使用者有其他想法會更動後端

### 2026-03-27
- v0.3.0 核心功能開發完成：全域設定 UI 面板 + 外部依賴健康檢查
- 後端：`storage.py` 新增 `get_global_settings` / `save_global_settings`，全域設定獨立為 `data/global_settings.json`
- 後端：新增 `app/routers/health.py`（GET /api/health/dependencies，httpx 並行 HEAD 請求）
- 後端：新增 `app/routers/settings.py`（GET/PUT /api/settings）
- 後端：`project_service.py` 新專案自動繼承 `global_settings.json` 的設定
- 前端：新增 `GlobalSettingsPanel.jsx`（運費/低消/排除關鍵字/封鎖賣家 Tag 輸入）
- 前端：新增 `DependencyStatus.jsx`（側邊欄底部小圓點 + 可展開詳細列表）
- 前端：`Layout.jsx` 整合以上元件，版本號更新至 v0.3.0
- 瀏覽器驗證通過，所有 API 端點正常回應
- 已知：salix5 卡圖（400）和露天 API（403）的健康檢查 URL 需要調整（不影響實際功能）

### 2026-03-25
- 比對 Notion 筆記與專案進度，整理出 13 項未實現點子並進行優先度分析
- 確認 `global_settings` 四個欄位（`default_shipping_cost`, `min_purchase_limit`, `global_exclude_keywords`, `global_exclude_seller`）後端邏輯已完整，缺前端管理 UI
- 決定 v0.3.0 新增「全域設定 UI」和「依賴 URL 驗證」功能
- 確認 `cid_table.json` 整合已實作完成

### 2026-03-24
- 修復 `ResultsPage.jsx` 白畫面 Critical Bug：`tasks.py` 的 `get_results` 新增資料格式轉換
- 完成階段六（前端錯誤處理）：新建 `ApiErrorBanner.jsx` 共用元件、更新 `api.js` interceptor
- 所有頁面的 API 錯誤現在會顯示友善的使用者提示（取代 `alert()` 和靜默的 `console.error`）
- 集中管理外部 URL 至 `app/config.py`，消除散落各處的 hardcoded 網址
- 統一版本號為 `v0.2.0`（SemVer 開發期慣例），更新 README 目錄結構和版本歷史
- 合併 `refactor/backend-architecture` 回 `main`

### 2026-03-23
- 將開發計劃從 `.gemini/antigravity/brain/` 複製到專案 `docs/` 目錄，方便隨時查看
- 完成階段五（腳本模組化）：建立 4 個新 Service、淘汰 subprocess、修復 cards.py 反向依賴
- 目前進度：階段一～六完成，下一步是 v0.3.0 計畫中的功能

### 2026-03-18 (Refactoring Frontend Code 對話)
- 完成前端常數抽取（`cardTypes.js`），消除重複的 `attrNames`/`raceNames`

### 2026-03-16 (Continue YGOscraper Development 對話)
- 完成 6 個 Conventional Commits 的 Git 拆分提交

### 2026-03-13 (UI/UX Overhaul 對話)
- UI/UX 五大改版實作全部完成（購物車卡片式、稀有度標籤、結果頁、側邊欄清理、專案預覽）
- 瀏覽器驗證階段尚未完成

### 2026-03-11 (UI/UX Overhaul 對話)
- 建立 UI/UX 全面改版 implementation plan

---

## 🗺️ 版本路線圖

> 遵循 [SemVer](https://semver.org/) 開發階段慣例（`0.x.x` = 尚未正式發佈）
> 來源：Notion 筆記比對 + 2026-03-25 討論決議

| 版本 | 狀態 | 主題 | 內容 |
|------|------|------|------|
| **v0.2.0** | ✅ 完成 | 後端架構重構 | Service 模組化、API 路由拆分、Pydantic Schema、外部 URL 集中管理 |
| **v0.2.1** | ✅ 完成 | Bug 修復 + 前端小改善 | ResultsPage 白畫面修復、API 錯誤處理（ApiErrorBanner）、階段六完成 |
| **v0.3.0** | ✅ 完成 | 前端強化 + 全域設定 | 全域設定 UI + 健康檢查 + 獨立儲存 |
| **v0.3.1** | ✅ 完成 | Bug 修復 + 專案管理 | 全域設定 Modal 化、數字輸入修正、刪除專案、查看結果按鈕 |
| **v0.4.0** | ✅ 完成 | 稀有度重構 + 專案設定 + Bug 修復 | rid 標籤分色、並行加入購物車修復、兩層設定架構 |
| **v0.4.1** | ✅ 完成 | 前端標籤與 Tooltip 調整 | 純 CSS tooltip 分三行顯示稀有度及卡包出處 |
| **v0.5.0** | 💡 構想中 | 爬蟲升級（items/v2 API） | 見下方詳細清單 |
| **v0.6.0** | 💡 構想中 | Neuron 牌組導入 | 見下方詳細清單 |
| **v0.7.0** | 💡 構想中 | 使用者體驗 + UI 改善 | 見下方詳細清單 |
| **v1.0.0** | 🎯 目標 | 正式版 | 功能穩定、文件齊全、可供他人使用與部署 |

### v0.3.0 — 前端強化 + 全域設定 ✅

> 主題：讓使用者透過前端 UI 管理後端已支援的 `global_settings` 參數，加上穩定性改善。

- [x] **全域設定 UI（側邊欄）**：在左側欄建立「全域設定」面板，讓使用者管理：
  - [x] 預設運費 (`default_shipping_cost`，目前預設 60 元)
  - [x] 每家最低消費門檻 (`min_purchase_limit`，目前預設 0 = 不限制)
  - [x] 排除關鍵字清單 (`global_exclude_keywords`，如「卡套」「牌套」)
  - [x] 封鎖賣家清單 (`global_exclude_seller`，輸入賣家 ID)
  > ⚠️ 不預設內建任何黑名單資料，僅提供使用者自行設定的介面（避免法律風險）
- [x] **全域設定獨立儲存**：從 `cart.json` 抽出為 `data/global_settings.json`，新專案自動繼承
- [x] **依賴 URL 驗證機制**：頁面載入時自動檢查 `config.py` 中的外部 URL 是否可達，側邊欄底部顯示綠/黃指示燈
  > ⚠️ 已知問題：卡圖（400）和露天 API（403）的 HEAD 請求回傳非 2xx，需調整檢查 URL 或判定邏輯
- [ ] Loading 狀態改善
- [ ] 斷線重連提示
- [ ] 爬蟲進度即時顯示

### v0.3.1 — Bug 修復 + 專案管理 ✅

> 主題：修復 v0.3.0 的 6 項前端 Bug，新增刪除專案功能。

- [x] **全域設定 Modal 化**：從側邊欄移至右上角齒輪 ⚙️ → Modal Window，側邊欄更簡潔
- [x] **數字輸入框修正**：改用 `text + inputMode="numeric"` 修復刪不掉開頭 0 的 bug，自訂 ±10 Stepper 取代瀏覽器預設按鈕
- [x] **Tag 輸入清空修正**：排除關鍵字/封鎖賣家輸入後即使重複也會清空輸入框
- [x] **「全域設定」改名為「專案設定」**：ProjectDetail 右欄標題修正
- [x] **查看結果按鈕**：已計算過的專案可從 ProjectDetail 回頭查看結果
- [x] **刪除專案**：專案卡片 hover 顯示 🗑️ 刪除按鈕，軟刪至 `_legacy/trash/`（可手動恢復）
  - [x] 後端：`DELETE /api/projects/{id}` + `storage.delete_project()`

### v0.4.0 — 稀有度重構 + 專案設定 + Bug 修復 ✅

> 主題：cart.json 資料格式重構（breaking change），完整實作兩層設定架構，修復並行 Bug。

- [x] **稀有度 ID 重構 + 標籤分色**：
  - [x] `rarity_name` → `rarity_id`（Konami DB 的 rid）
  - [x] 新增 `rarityTypes.js`（24 條 rid 對照表）
  - [x] 前端標籤依 rid 查表顯示稀有度縮寫 + 分色
  - [x] Hover tooltip 顯示日文全名（中文通稱）
- [x] **修復並行加入購物車 race condition**：
  - [x] 兩階段設計：並行爬取 CID + 序列寫入購物車
  - [x] writeQueue + isWriting 互斥鎖避免 read-modify-write 衝突
- [x] **專案設定完整實作（兩層架構）**：
  - [x] 新增 `CartSettings` schema（shipping_cost, min_purchase, exclude_keywords, exclude_seller）
  - [x] 數值型：None = 繼承全域，有值 = 覆蓋
  - [x] 列表型：與全域設定聯集合併
  - [x] cleaner + calculator + tasks router 均已更新合併邏輯
  - [x] ProjectDetail 專案設定面板擴充為完整 4 項設定
- [x] **清除舊 cart.json 資料**（不遷移，直接清除）

### v0.4.1 — 前端標籤與 Tooltip 調整 ✅

> 主題：優化稀有度標籤的 Hover 體驗

- [x] 把稀有度 badge 的原生 title tooltip 換成自訂 CSS tooltip
- [x] Tooltip 內容分三行顯示：中文稀有度、日文全名、卡包出處

### v0.5.0 — 爬蟲升級（露天 items/v2 API 整合）💡

> 主題：利用 Notion 中發現的新 API 一次解決運費精算、複數選項商品、賣家品質三大問題。

- [ ] **整合 `items/v2/list` API**（`https://rapi.ruten.com.tw/api/items/v2/list?gno={item_id}&level=simple`）
  - [ ] 二階段爬蟲流程：第一階段用搜尋 API 取得商品 ID 清單 → 第二階段用 items/v2 批量查詢詳細資訊
  - [ ] 提取 `deliver_way`（各運送方式 + 運費）→ 取代 `default_shipping_cost` 估算
  - [ ] 提取 `seller_score`（賣家信用/出貨率）→ 可用於品質排序
  - [ ] 提取 `store_name`（店名）→ 前端顯示用
- [ ] **複數選項商品拆解**（`level=detail`）
  - [ ] 呼叫 detail 級別 API 取得每個選項的獨立資訊（名稱、價格、庫存）
  - [ ] 將各選項拆成獨立資料列，讓 calculator 能精確計算
  - [ ] 取代現有的 `alt_price` 排除機制
- [ ] **運費精算**
  - [ ] 讓使用者選擇偏好的取貨方式（郵寄/超商/宅配）
  - [ ] calculator 改為按每位賣家的實際運費計算
- [ ] **賣家 API 整合**（`https://rapi.ruten.com.tw/api/users/v1/index.php/{seller_id}/storeinfo`）
  - [ ] 可選功能：讀取賣家佈告欄資訊
- [ ] **結果頁手動微調**（待設計，見下方設計備註 `per_cart_settings`）
  - [ ] 計算完成後，使用者可手動排除特定商品/商家並重新計算
- [ ] **自動辨識引流商品過濾器**
  - [ ] 偵測商品名稱包含與搜尋關鍵字無關的高熱度卡名（如賣小廢卡掛「搜天救龍」引流）
  - [ ] 建立啟發式規則：商品名 token 中出現無關卡名 → 標記為疑似引流
  - [ ] `cleaner_service.py` 新增引流過濾邏輯（可選擇性開啟，預設關閉）

### v0.6.0 — Neuron 牌組代碼導入 💡

> 主題：殺手級功能，讓使用者用牌組代碼一鍵生成購物車。

- [ ] **後端新增 Neuron 爬蟲服務**（`app/services/neuron_service.py`）
  - [ ] 輸入 Neuron 牌組代碼 → 解析出卡組清單（卡片 CID + 數量）
  - [ ] CID → `konami_scraper.py` 取得各版本卡號
  - [ ] 整合資料自動生成 `cart.json` 格式
- [ ] **新增 API 端點**（`app/routers/` 中新增路由）
  - [ ] `POST /api/neuron/import` 接收牌組代碼，回傳解析結果
- [ ] **前端**
  - [ ] 在購物車頁新增「從 Neuron 導入卡組」按鈕
  - [ ] 導入後使用者可預覽、編輯、再加入購物車
- [ ] 非同步效能優化
- [ ] WebSocket 進度回報

### v0.7.0 — 前端重構 + 使用者體驗全面打磨 💡

> 主題：用 shadcn/ui 重構前端元件庫，並全面打磨 UX 細節。

- [ ] **前端重構（shadcn/ui）**：用 shadcn/ui 元件庫重構現有 React 前端
  - [ ] 引入 shadcn/ui + Tailwind CSS 設計系統
  - [ ] 逐頁替換現有自定義元件（購物車、搜尋、結果頁）
  - [ ] 統一設計語言和色彩系統
- [ ] **深色/淺色主題切換**（shadcn/ui 內建支援）
- [ ] 卡片圖鑑瀏覽
- [ ] 搜尋歷史記錄
- [ ] 購物車匯出/匯入
- [ ] UI 細節改善（源自 Notion 筆記）：
  - [ ] 搜尋選項加顏色/底圖/icon 視覺指示
  - [ ] Or/And 開關邏輯更明確的 UI 提示
  - [ ] 卡圖放大檢視
  - [ ] 自由開關禁限卡、屬性、種族、等級篩選條件
- [ ] 資料持久化
  - [ ] 自建卡片 DB（取代每次啟動下載）
  - [ ] 歷史採購方案比較

### 更遠的未來（v1.x+）

- [ ] 🗄️ **自建 card.cdb**：整合 card id + CID + 稀有度版本 + 異圖編號 + 卡圖的自建 DB，學 salix5 掛在 GitHub Pages 上
  - [ ] 爬 Konami DB 取得完整卡片資料
  - [ ] 對應 salix5 CDB 格式，整合 CID ↔ card id 對照表
  - [ ] 支援稀有度版本、異圖編號查詢
- [ ] 🔧 **自動 DB 維護工具**：定期爬 Konami DB + 偵測 salix5 CDB 更新來自動同步
  - [ ] 設計 cron / GitHub Actions 排程觸發
  - [ ] 偵測 salix5 CDB 有更新時自動 pull + 合併差異
- [ ] 🖥️ **部署方案**（二擇一或並行）：
  - [ ] 本地桌面 App（Electron/Tauri，前後端都在本地，使用者不需裝 Python）
  - [ ] 標準前後端分離網頁 App（Docker 部署後端）

---

### 📌 設計備註

#### `default_shipping_cost`（預設運費）

> 目前 `calculator_service.py` 的線性規劃模型使用 `global_settings.default_shipping_cost`（預設 60 元）
> 作為所有賣家的統一運費來計算最佳方案。
>
> **為什麼不用爬下來的真實運費？**
> 露天 API 回傳的 `ShippingCost` 是所有運送方式中「最便宜的」（例如郵寄 40 元），
> 但多數使用者偏好超商取貨（約 60-65 元），不希望跑不同地方取不同包裹。
> 設定一個統一的「使用者認同的平均運費」是 MVP 階段的合理簡化。
>
> **未來完整實作（v0.4.0，原 v0.5.0）：**
> - 利用 items/v2 API 的 `deliver_way` 欄位取得每商品的完整運送方式與對應運費
> - 讓使用者選擇偏好的取貨方式（郵寄/超商/宅配）
> - calculator 改為按每位賣家的實際運費計算

#### 複數選項商品（`alt_price` 過濾機制）

> 露天拍賣允許賣家在單一商品中設定複數選項（如不同稀有度），各選項可有不同價格、獨立庫存。
> 但露天 API 回傳的 `StockQty` 和 `SoldQty` 是**所有選項的合併值**，無法區分個別選項的庫存。
>
> **目前 MVP 處理方式：**
> - `ruten_scraper.py`：用 `PriceRange` 首尾是否相同判斷是否有複數選項 → 標記 `alt_price=1`
> - `cleaner_service.py`：過濾直接排除 `alt_price=1` 的商品
>
> **已知盲點：**
> 若複數選項的價格剛好相同（例如兩種稀有度都賣 30 元），`PriceRange=[30,30]`，
> `alt_price` 會是 `0`，**不會被過濾掉**，但庫存仍是合併的，可能導致 calculator 誤判庫存充足。
>
> **未來完整實作（v0.4.0，原 v0.5.0）：**
> - 利用 items/v2 API 的 `level=detail` 取得每個選項的獨立資訊（名稱、價格、庫存）
> - 將各選項拆成獨立的資料列，讓 calculator 能精確計算
> - 前端顯示時標註屬於哪個選項

#### `per_cart_settings`（專案級設定 vs 全域設定）✅ 決議：方案 A

> **決議日期：** 2026-03-25
>
> **背景：** `cart.json` 原本只有 `global_settings` 一層設定。
> 為支援「結果頁手動排除商品/商家 → 重新計算」功能，採用兩層設定架構。
>
> **採用方案 A：兩層設定架構**
> ```json
> {
>   "global_settings": { ... },
>   "cart_settings": {
>     "exclude_keywords": ["額外的"],
>     "exclude_seller": ["某賣家ID"]
>   }
> }
> ```
> - `cart_settings` 疊加在 `global_settings` 之上（merge，非覆蓋）
> - 結果頁的「排除」操作寫入 `cart_settings`，不汙染全域
> - `cleaner_service.py` 讀取時：`effective_exclude = global_exclude + cart_exclude`
>
> **實作時程：** v0.4.0（搭配結果頁手動微調功能）
> **v0.3.0 先做：** `global_settings` 的前端管理 UI

#### 已挖掘的露天 API 參考表

> 來源：Notion 筆記（2025-12-16 ~ 2025-12-18）

| API | URL | 用途 |
|-----|-----|------|
| 搜尋商品 | `https://rtapi.ruten.com.tw/api/search/v3/index.php/core/seller/{keyword}/...` | 目前 `ruten_scraper.py` 使用中 |
| 商品詳細 (simple) | `https://rapi.ruten.com.tw/api/items/v2/list?gno={item_id}&level=simple` | `deliver_way`、`seller_score`、`store_name` |
| 商品詳細 (detail) | `https://rapi.ruten.com.tw/api/items/v2/list?gno={item_id}&level=detail` | 複數選項商品的個別價格/庫存 |
| 賣家資訊 | `https://rapi.ruten.com.tw/api/users/v1/index.php/{seller_id}/storeinfo` | 賣家店名、信用、佈告欄 |

> items/v2 支援一次查詢複數商品（用 `&gno=` 串接，確切上限待驗證）

#### 外部資料源參考表

> 來源：Notion 筆記

| 用途 | URL |
|------|-----|
| 卡片圖床 | `https://github.com/salix5/query-data/blob/gh-pages/pics/{卡片密碼}.jpg` |
| 核心卡片數據 | `https://github.com/salix5/cdb/blob/gh-pages/cards.cdb` |
| Konami 官方查卡 | `https://www.db.yugioh-card.com/yugiohdb/card_search.action?ope=2&cid={cid}` |
| 卡片密碼→CID | `https://github.com/salix5/heliosphere/blob/master/data/cid_table.json` |
