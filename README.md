# ⚡ YGO Scraper v2.0.0

遊戲王卡片最低價格採購優化工具。從露天拍賣 (Ruten) 自動搜尋、比價，計算出最划算的購買方案。

---

## 📐 系統架構

| 層級 | 技術 | 說明 |
|------|------|------|
| **前端** | React + Vite + Tailwind CSS v4 | 使用者介面，提供搜尋卡片、管理購物車等功能 |
| **後端** | FastAPI (Python) | API 伺服器，負責資料查詢、爬蟲與價格計算 |
| **卡片資料庫** | SQLite (`cards.cdb`) | 啟動時自動從 GitHub 下載，載入記憶體供高速查詢 |
| **CID 對照表** | JSON (`cid_table.json`) | 卡片密碼 ↔ Konami CID 的對照表，啟動時自動下載 |
| **爬蟲** | Python (`scraper.py`, `konami_scraper.py`) | 分別負責露天拍賣比價與 Konami 官方卡號爬取 |

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
cd /Users/Mochi/Documents/Development/YGOscraper

# 建立 Python 虛擬環境（只需做一次）
python -m venv env

# 啟動虛擬環境
source env/bin/activate        # macOS / Linux
# env\Scripts\activate         # Windows

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

每次要開始使用此專案時，你需要開啟**兩個終端機視窗**，分別跑「後端」和「前端」。

### 步驟 1：啟動後端伺服器

打開**第一個終端機視窗**，依序輸入以下指令：

```bash
# 1. 進入專案根目錄
cd /Users/Mochi/Documents/Development/YGOscraper

# 2. 啟動 Python 虛擬環境
source env/bin/activate

# 3. 啟動後端 API 伺服器
uvicorn server:app --reload
```

成功的話，你會看到類似這樣的訊息：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     ✅ cards.cdb 已成功載入記憶體
INFO:     ✅ cid_table.json 已成功載入
```

> 後端伺服器**啟動時會自動從 GitHub 下載**最新版的 `cards.cdb` 和 `cid_table.json`，不需要手動下載任何檔案。

### 步驟 2：啟動前端介面

打開**第二個終端機視窗**（不要關掉第一個！），依序輸入以下指令：

```bash
# 1. 進入前端目錄
cd /Users/Mochi/Documents/Development/YGOscraper/frontend

# 2. 啟動前端開發伺服器
npm run dev
```

成功的話，你會看到類似這樣的訊息：
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### 步驟 3：打開瀏覽器

在瀏覽器中輸入以下網址：

```
http://localhost:5173
```

🎉 **看到深色介面就代表專案啟動成功了！**

### 關閉專案

在兩個終端機視窗中分別按 `Ctrl + C` 即可關閉後端與前端。

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

---

## 📁 專案目錄結構

```
YGOscraper/
├── server.py             # 後端 API 主程式（FastAPI）
├── scraper.py            # 露天拍賣爬蟲
├── konami_scraper.py     # Konami 官方資料庫爬蟲（卡號查詢）
├── caculator.py          # 最低價格計算引擎
├── clean_csv.py          # 爬蟲資料清理
├── file_genarator.py     # 檔案產生工具
├── requirements.txt      # Python 套件清單
├── data/                 # 專案資料（購物車 JSON 等）
├── frontend/             # React 前端應用程式
│   ├── src/
│   │   ├── main.jsx      # 前端進入點
│   │   ├── App.jsx       # 路由設定
│   │   ├── index.css     # 全域樣式（Tailwind v4）
│   │   ├── components/   # React 元件
│   │   └── lib/          # API 工具函式
│   ├── package.json
│   └── vite.config.js
├── _legacy/              # v1.0 舊版程式碼（已棄用）
└── env/                  # Python 虛擬環境
```

---

## 📌 版本歷史

| 版本 | 說明 |
|------|------|
| **v2.0.0** | 全面重寫：React 前端 + FastAPI 後端，卡片資料庫改為啟動時載入記憶體 |
| **v1.0.0** | 舊版 CLI / HTML 版本（已棄用，保留於 `_legacy/` 資料夾） |

---

## ⚠️ 常見問題

### `EPERM: operation not permitted` 錯誤
如果在執行 `npm run dev` 或其他指令時遇到此錯誤，這是 macOS 的權限問題。請在終端機執行：
```bash
chmod -R 755 /Users/Mochi/Documents/Development/YGOscraper/frontend/node_modules
```

### 後端啟動時卡住或下載失敗
後端需要在啟動時從 GitHub 下載 `cards.cdb`（約 6MB）和 `cid_table.json`。請確保網路暢通。
