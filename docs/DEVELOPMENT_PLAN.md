# YGOscraper 2.0 開發計畫與進度追蹤

> **最後更新**：2026-03-23
> **用途**：這份文件是 AI 助手和開發者共用的「活文件」，紀錄整體開發目標、進度、和備忘事項。
> 每次對話都可以更新此文件。

---

## 📋 重構進度總覽（Task Checklist）

### 階段一：穩定現況 ✅
- [x] 將目前所有變更 Commit 存檔 (WIP 狀態)
- [x] 建立待辦清單追蹤後續進度

### 階段二：Pydantic Schema 修復 ✅
> 此階段優先於 API 拆分，因為它是目前 Bug 的主要來源。
- [x] 修正 `CartItem` Model：前端傳送的額外欄位 (`passcode`, `cid`, `type` 等) 需要被接受
- [x] 將所有 Models 搬入 `app/schemas.py`，定義完整的 `CartItemCreate`, `CartItemFull`, `CardNumber` 等結構

### 階段三：API 路由拆分（後端重構）✅
- [x] 建立 `app/routers/` 目錄，將 API 依功能分檔：
  - [x] `projects.py`：專案 CRUD
  - [x] `cart.py`：購物車讀寫
  - [x] `cards.py`：卡片搜尋 + CID 爬取
  - [x] `tasks.py`：執行爬蟲/計算流程 + 結果讀取
- [x] 重整 `server.py` 為純啟動入口 (只保留 `lifespan`, CORS, `include_router`)

### 階段四：資料存取層封裝 ✅
- [x] 建立 `app/services/storage.py` (`ProjectStorage` 類別)，統一管理 `cart.json` / `plan.json` 的讀寫
- [x] 收編 `file_genarator.py` → `app/services/project_service.py` (修正拼寫 genarator→generator)
- [x] 為未來自建 DB 預留介面：定義 `CardDatabaseService` 抽象層

### 階段五：腳本模組化（淘汰 subprocess）✅
- [x] `clean_csv.py` → `app/services/cleaner_service.py` (封裝為 `DataCleaner` 類別)
- [x] `caculator.py` → `app/services/calculator_service.py` (封裝為 `PurchaseOptimizer` 類別)
- [x] 移動 `scraper.py`, `konami_scraper.py` 到 `app/services/` 下
- [x] 修改 `tasks.py` router：用 `import` 取代 `subprocess.run()`
- [x] 修復 `cards.py` 的反向依賴（`import server` → `app.state` 注入）

### 階段六：前端架構梳理 ✅
- [x] 抽取 `CardSearchPage.jsx` 中的常數 (卡片類型/屬性/種族對應表) 到 `src/constants/cardTypes.js`
- [x] 確認 API 錯誤處理是否完善 (如網路斷線、後端 500)
- [x] 消除 `ProjectDetail.jsx` 中重複定義的 `attrNames` / `raceNames`

---

## 🐛 已知 Bug 清單

- [x] 🔴 **[Critical]** `CartItem` Pydantic model 與前端實際傳送的資料不匹配 → 已在 Phase 0 (schemas.py) 修復
- [x] 🟡 `target_card_numbers` 欄位定義：已改為 `List[Union[CardNumberInfo, str]]` 兼容兩種格式
- [ ] 🟡 `data/cart.json` 和 `frontend/package.json` 有 Git 權限問題 (`Operation not permitted`)
- [x] 🟢 `file_genarator.py` 拼寫錯誤：已建立 `app/services/project_service.py` 替代
- [x] 🟢 `storage.py` 淺拷貝 Bug：已改用 `copy.deepcopy()`
- [x] 🔴 **[Critical]** `ResultsPage.jsx` 結果頁白畫面：前後端資料結構不匹配 → 已在 `tasks.py` 的 `get_results` 中做格式轉換修復
  - **後端** `calculator_service.py` 輸出的 `plan.json` 格式：`{ sellers: { 賣家ID: {items, items_subtotal} }, summary: {total_items_cost, total_shipping_cost, grand_total} }`
  - **前端** `ResultsPage.jsx` 期望的格式：`{ total_cost, total_item_cost, total_shipping_cost, missing_cards, plan: [{seller, subtotal, shipping_cost, items: [{name, url, card_name_zh, price, buy_count, card_number}]}] }`
  - 存取 `results.plan.length` 時因 `results.plan` 為 `undefined` 而拋出 `TypeError`，導致整個頁面 Crash 變成白畫面
  - 修復方向：在 API 回傳層（`tasks.py` 的 `get_results`）或前端 `ResultsPage.jsx` 中做格式轉換，使兩端一致

---

## 🏗️ 目標檔案結構

完成所有階段後，專案應呈現以下結構：

```
YGOscraper/
├── server.py                    # 入口 (~50行)
├── app/
│   ├── __init__.py
│   ├── schemas.py               # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── cart.py
│   │   ├── cards.py
│   │   └── tasks.py
│   └── services/
│       ├── __init__.py
│       ├── card_db.py           # 卡片資料庫服務 (預留自建DB替換)
│       ├── storage.py           # 專案檔案讀寫管理
│       ├── ruten_scraper.py     # 露天爬蟲
│       ├── konami_scraper.py    # Konami 爬蟲
│       ├── cleaner_service.py   # 資料清洗
│       ├── calculator_service.py # 最佳組合計算
│       └── project_service.py   # 專案建立管理
├── frontend/                    # React 前端
├── docs/                        # 開發文件（本文件所在處）
├── data/                        # 專案資料
└── _legacy/                     # 舊版系統
```

---

## 📝 開發備忘錄

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

| 版本 | 狀態 | 主題 | 內容 |
|------|------|------|------|
| **v0.2.0** | ✅ 完成 | 後端架構重構 | Service 模組化、API 路由拆分、Pydantic Schema、外部 URL 集中管理 |
| **v0.2.1** | ✅ 完成 | Bug 修復 + 前端小改善 | ResultsPage 白畫面修復、API 錯誤處理（ApiErrorBanner）、階段六完成 |
| **v0.3.0** | ⬜ 計畫中 | 前端強化 | Loading 狀態、斷線重連提示、爬蟲進度即時顯示 |
| **v0.4.0** | 💡 構想中 | 資料持久化 | 自建卡片 DB（取代每次啟動下載）、歷史採購方案比較 |
| **v0.5.0** | 💡 構想中 | 爬蟲升級 | 非同步效能優化、WebSocket 進度回報、**運費精算**、**複數選項商品支援**（見備註） |
| **v0.6.0** | 💡 構想中 | 使用者體驗 | 卡片圖鑑瀏覽、搜尋歷史記錄、購物車匯出/匯入、深色/淺色主題切換 |
| **v1.0.0** | 🎯 目標 | 正式版 | 功能穩定、文件齊全、可供他人使用與部署（Docker / Railway） |

### 更遠的未來（v1.x+）
- 🔐 使用者帳號系統（多人各自管理專案）
- 📊 價格趨勢圖表（記錄每次爬蟲的價格變化）
- 🤖 智慧推薦（根據歷史資料推薦最佳購買時機）
- 📱 PWA 支援（手機上也能用）

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
> **未來完整實作（v0.5.0）：**
> - 爬取每商品的完整運送方式與對應運費
> - 讓使用者選擇偏好的取貨方式（郵寄/超商/宅配）
> - calculator 改為按每位賣家的實際運費計算

#### 複數選項商品（`alt_price` 過濾機制）

> 露天拍賣允許賣家在單一商品中設定複數選項（如不同稀有度），各選項可有不同價格、獨立庫存。
> 但露天 API 回傳的 `StockQty` 和 `SoldQty` 是**所有選項的合併值**，無法區分個別選項的庫存。
>
> **目前 MVP 處理方式：**
> - `ruten_scraper.py`：用 `PriceRange` 首尾是否相同判斷是否有複數選項 → 標記 `alt_price=1`
> - `cleaner_service.py`：過濾 3 直接排除 `alt_price=1` 的商品
>
> **已知盲點：**
> 若複數選項的價格剛好相同（例如兩種稀有度都賣 30 元），`PriceRange=[30,30]`，
> `alt_price` 會是 `0`，**不會被過濾掉**，但庫存仍是合併的，可能導致 calculator 誤判庫存充足。
>
> **未來完整實作（v0.5.0）：**
> - 呼叫露天商品詳情 API 取得每個選項的獨立資訊（名稱、價格、庫存）
> - 將各選項拆成獨立的資料列，讓 calculator 能精確計算
> - 前端顯示時標註屬於哪個選項
