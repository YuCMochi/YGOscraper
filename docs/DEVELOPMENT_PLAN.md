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

### 階段五：腳本模組化（淘汰 subprocess）⬜ 未開始
> 審計發現：`scraper.py` 的 `RutenScraper` 和 `konami_scraper.py` 的 `KonamiScraper` 已經是類別化的，可直接 import 使用。`clean_csv.py` 和 `caculator.py` 仍為獨立函式，需封裝。
- [ ] `clean_csv.py` → `app/services/cleaner_service.py` (封裝為 `DataCleaner` 類別)
- [ ] `caculator.py` → `app/services/calculator_service.py` (封裝為 `PurchaseOptimizer` 類別)
- [ ] 移動 `scraper.py`, `konami_scraper.py` 到 `app/services/` 下 (已有類別，僅需搬移)
- [ ] 修改 `tasks.py` router：用 `import` 取代 `subprocess.run()`

### 階段六：前端架構梳理 🔶 部分完成
- [x] 抽取 `CardSearchPage.jsx` 中的常數 (卡片類型/屬性/種族對應表) 到 `src/constants/cardTypes.js`
- [ ] 確認 API 錯誤處理是否完善 (如網路斷線、後端 500)
- [x] 消除 `ProjectDetail.jsx` 中重複定義的 `attrNames` / `raceNames`

---

## 🐛 已知 Bug 清單

- [x] 🔴 **[Critical]** `CartItem` Pydantic model 與前端實際傳送的資料不匹配 → 已在 Phase 0 (schemas.py) 修復
- [x] 🟡 `target_card_numbers` 欄位定義：已改為 `List[Union[CardNumberInfo, str]]` 兼容兩種格式
- [ ] 🟡 `data/cart.json` 和 `frontend/package.json` 有 Git 權限問題 (`Operation not permitted`)
- [x] 🟢 `file_genarator.py` 拼寫錯誤：已建立 `app/services/project_service.py` 替代
- [x] 🟢 `storage.py` 淺拷貝 Bug：已改用 `copy.deepcopy()`

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

### 2026-03-23
- 將開發計劃從 `.gemini/antigravity/brain/` 複製到專案 `docs/` 目錄，方便隨時查看
- 目前進度：階段一～四完成，下一步是階段五（腳本模組化）

### 2026-03-18 (Refactoring Frontend Code 對話)
- 完成前端常數抽取（`cardTypes.js`），消除重複的 `attrNames`/`raceNames`

### 2026-03-16 (Continue YGOscraper Development 對話)
- 完成 6 個 Conventional Commits 的 Git 拆分提交

### 2026-03-13 (UI/UX Overhaul 對話)
- UI/UX 五大改版實作全部完成（購物車卡片式、稀有度標籤、結果頁、側邊欄清理、專案預覽）
- 瀏覽器驗證階段尚未完成

### 2026-03-11 (UI/UX Overhaul 對話)
- 建立 UI/UX 全面改版 implementation plan
