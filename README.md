# ⚡ YGO Scraper v0.4.1

遊戲王卡片最低價格採購優化工具。從露天拍賣 (Ruten) 自動搜尋、比價，計算出最划算的購買方案。

---

## 📐 系統架構

| 層級 | 技術 | 說明 |
|------|------|------|
| **前端** | React + Vite + Tailwind CSS v4 | 使用者介面，提供搜尋卡片、管理購物車、全域設定管理等功能 |
| **後端** | FastAPI (Python) | API 伺服器，負責資料查詢、爬蟲、價格計算與設定管理 |
| **卡片資料庫** | SQLite (`cards.cdb`) | 啟動時自動從 GitHub 下載，載入記憶體供高速查詢 |
| **CID 對照表** | JSON (`cid_table.json`) | 卡片密碼 ↔ Konami CID 的對照表，啟動時自動下載 |
| **爬蟲** | Python (`ruten_scraper.py`, `konami_scraper.py`) | 分別負責露天拍賣比價與 Konami 官方卡號爬取 |

---

## 🔧 環境需求

- **Python** 3.9 以上
- **Node.js** 18 以上
- **pip** 和 **npm**（分別用於安裝 Python 與 Node.js 套件）

---

## 📦 第一次安裝

### 1. 安裝後端（Python）

```bash
# 進入專案根目錄
cd /Users/Mochi/Development/YGOscraper

# 建立 Python 虛擬環境（只需做一次）
python -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 安裝所有 Python 套件
pip install -r requirements.txt
```

### 2. 安裝前端（React）

```bash
# 進入前端目錄
cd frontend

# 安裝所有前端套件
npm install
```

> **💡 提示**：安裝步驟只需「第一次」執行。之後每次開專案只需要做下方的「啟動步驟」即可。

---

## 🚀 每次啟動專案（使用教學）

現在專案已經內建自動化腳本，可以一次在背景啟動後端跟前端！

### 步驟 1：啟動完整環境

打開終端機，依序輸入以下指令：

```bash
# 進入專案根目錄
cd /Users/Mochi/Development/YGOscraper

# 執行啟動腳本
./start_dev.sh
```

成功的話，你會看到類似這樣的終端機輸出，代表前後端都已成功啟動：
```text
🚀 正在啟動 YGO Scraper 測試環境...
==========================================
📦 [後端] 啟動 FastAPI 伺服器...
🎨 [前端] 啟動 Vite 開發伺服器...
==========================================
✅ 啟動完畢！
🌐 前端網址: http://localhost:5173
🔌 後端 API: http://127.0.0.1:8000
💡 按下 [Ctrl + C] 即可同時關閉前後端
==========================================
```

> 💡 **提示**：後端伺服器啟動時會自動從 GitHub 下載最新版的 `cards.cdb` 和 `cid_table.json`，不需要手動下載任何檔案。

### 步驟 2：打開瀏覽器

在瀏覽器中開啟以下網址：

```
http://localhost:5173
```

🎉 **看到深色介面就代表專案啟動成功了！**

### 關閉專案

在執行 `./start_dev.sh` 的終端機視窗中按下 `Ctrl + C`，腳本會自動幫你優雅地關閉前端和後端伺服器。

---

## 🎮 功能使用教學

### 1. 建立專案
- 在首頁點擊「**新建專案**」按鈕
- 每個專案代表一次獨立的採購計畫

### 2. 搜尋卡片
- 進入專案後，點擊「**搜尋卡片**」
- 在搜尋框輸入中文卡名（例如：`青眼白龍`、`增殖的G`）
- 按下 Enter 或點擊搜尋按鈕
- 搜尋結果會即時顯示卡片圖片、類型、攻守數值等資訊

### 3. 加入購物車
- 在搜尋結果中找到你要的卡片，點擊「**加入購物車**」
- 系統會**自動**用該卡的 CID 去 Konami 官方資料庫爬取所有印刷過的卡號（例如 `DABL-JP035`、`PAC1-JP001` 等）
- 這些卡號之後會用來在露天拍賣搜尋最低價格

### 4. 執行爬蟲比價
- 回到專案詳情頁面，點擊「**執行爬蟲**」
- 系統會自動到露天拍賣搜尋購物車中所有的卡號
- 爬蟲結束後，系統會自動清理資料並計算最優購買方案

### 5. 查看結果
- 計算完成後會顯示最佳採購方案（最低總價含運費）

### 6. 管理全域設定（v0.3.0 新功能）
- 點左側欄的「**全域設定**」展開設定面板
- 可調整：預設運費、每家最低消費、排除關鍵字、封鎖賣家 ID
- 這些設定會套用到**之後新建的所有專案**

---

## 📁 專案目錄結構

```
YGOscraper/
├── server.py             # 後端 API 入口點（FastAPI）~50 行
├── app/                  # 後端核心模組
│   ├── config.py         # 外部 URL 統一管理
│   ├── schemas.py        # Pydantic 資料模型
│   ├── routers/          # API 路由
│   │   ├── projects.py   # 專案 CRUD
│   │   ├── cart.py       # 購物車讀寫
│   │   ├── cards.py      # 卡片搜尋 + CID
│   │   ├── tasks.py      # 爬蟲/計算任務
│   │   ├── health.py     # 外部依賴健康檢查
│   │   └── settings.py   # 全域設定 CRUD
│   └── services/         # 服務層（爬蟲、清洗、計算、資料庫）
├── frontend/             # React 前端應用程式（Vite + Tailwind v4）
│   └── src/components/
│       ├── GlobalSettingsPanel.jsx  # 全域設定面板
│       ├── DependencyStatus.jsx    # 外部服務狀態指示器
│       └── ...
├── data/
│   └── global_settings.json  # 全域設定（跨專案共用）
├── docs/                 # 開發文件
├── requirements.txt      # Python 套件清單
├── _legacy/              # 舊版系統（已棄用）
└── .venv/                # Python 虛擬環境
```

---

## 🌐 API 端點一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/projects` | 列出所有專案 |
| POST | `/api/projects` | 新建專案 |
| GET | `/api/cart/{project}` | 讀取購物車 |
| PUT | `/api/cart/{project}` | 更新購物車 |
| GET | `/api/cards/search?q=...` | 搜尋卡片 |
| POST | `/api/tasks/{project}/scrape` | 執行爬蟲 |
| GET | `/api/tasks/{project}/results` | 讀取計算結果 |
| GET | `/api/settings` | 讀取全域設定 |
| PUT | `/api/settings` | 更新全域設定 |
| GET | `/api/health/dependencies` | 檢查外部服務狀態 |

---

## 📌 版本歷史

| 版本 | 說明 |
|------|------|
| **v0.4.1** | 版本號統一管理：`server.py` 為單一真相來源，前端動態讀取 `/api/version` |
| **v0.4.0** | 設定頁面重構：全域設定從側邊欄移至右上角 Modal |
| **v0.3.1** | CI/CD Pipeline：GitHub Actions TDD + Lint 自動化 |
| **v0.3.0** | 全域設定 UI 面板、獨立 `global_settings.json`、外部依賴健康檢查、版本號同步 |
| **v0.2.1** | ResultsPage 白畫面修復、API 錯誤處理（ApiErrorBanner）、前端架構梳理完成 |
| **v0.2.0** | 後端架構重構完成：Service 模組化、API 路由拆分、Pydantic Schema、外部 URL 集中管理 |
| **v0.1.0** | React 前端 + FastAPI 後端的初版整合，UI/UX 改版 |
| **v0.0.x** | 舊版 CLI / HTML 腳本版本（已棄用，保留於 `_legacy/`） |

---

## ⚠️ 常見問題

### `EPERM: operation not permitted` 錯誤
如果在執行 `npm install` 或 `npm run dev` 時遇到此錯誤，這是 macOS 的 `com.apple.provenance` 延伸屬性問題。請依序嘗試：

```bash
# 方法 1：清除延伸屬性
xattr -cr frontend/node_modules

# 方法 2：重建 node_modules
rm -rf frontend/node_modules
npm install --prefix frontend

# 方法 3：若 npm cache 被 root 佔用
sudo chown -R $(whoami):staff ~/.npm
```

### 後端啟動時卡住或下載失敗
後端需要在啟動時從 GitHub 下載 `cards.cdb`（約 6MB）和 `cid_table.json`。請確保網路暢通。

### Git 操作出現 `Operation not permitted`
macOS 的 `com.apple.provenance` 屬性可能導致 Git 無法存取某些檔案。執行 `xattr -cr .` 可批量清除。
