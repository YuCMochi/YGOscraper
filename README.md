# 遊戲王卡片智慧比價工具 (Ruten Edition)

> 專門針對「露天拍賣」資料，採用**高效啟發式演算法（貪心 + 局部搜索）**，解決多卡片、多賣家、含運費的最佳採購組合問題。

---

## ✨ 專案亮點與目標 (MVP)

這個專案的核心目標是為組牌玩家提供一個比手動計算更省時、更便宜的採購方案。

1.  **即時資料擷取 (Scraping)**
    * **資料源**：鎖定露天拍賣 API (非公開)。
    * **效率**：支援多卡片並行爬取，大幅縮短等待時間。
2.  **精準過濾與標準化 (Cleaning)**
    * 使用卡片編號（`target_id`）作為關鍵字，排除高罕貴度卡或不相關商品，實現**「最低版本優先」**的比價策略。
    * 自動排除標題不符、價格異常、庫存為零的商品。
3.  **組合最佳化 (Optimization)**
    * **核心問題**：解決同時購買多種卡片時，單店運費 (固定成本) 遠高於商品差價的採購難題。
    * **演算法**：採用 **貪心演算法** 快速生成初始解，接著以 **局部搜索 (Local Search)** 進行迭代優化，在可接受的時間內找到接近全域最佳的最低總價（含固定運費）。
4.  **本地化與互動體驗 (Local MVP)**
    * 前端使用輕量級技術，動態載入卡片資料庫 (`cards.cdb`) 進行模糊搜尋。
    * 使用者可將多種卡片加入購物車並指定數量，透過 `cart.json` 文件將需求傳遞給主控程式。

---

## 💻 核心技術棧

| 模組 | 技術 | 職責說明 |
| :--- | :--- | :--- |
| **主控/運算** | Python (3.x) | 負責控制流程、讀取 JSON、協調爬蟲與優化引擎。 |
| **爬蟲** | Python (`requests`, `aiohttp`) | 採用非同步請求，並行爬取露天商品資料。 |
| **最佳化** | Python (核心邏輯) | 實現**貪心 + 局部搜索**演算法，計算最低成本。 |
| **資料庫** | SQL.js / SQLite | 輕量級卡片資料庫 (`cards.cdb`)，用於前端模糊搜尋。 |
| **前後端** | HTML/JS/CSS | 簡潔的前端界面，用於輸入需求和顯示結果。 |

---

## 系統架構與流程

為了驗證核心邏輯，專案採用**本地端主控制器**模式，而非傳統的客戶端-伺服器架構。


```mermaid
sequenceDiagram
    participant 使用者
    participant 前端 (HTML/JS/CSS)
    participant 卡片資料庫 (cards.cdb)
    participant 主控制器 (main_controller.py)
    participant 爬蟲模組 (scraper.py)
    participant 資料清理 (clean_csv.py)
    participant 優化引擎 (caculator.py)

    使用者->>前端 (HTML/JS/CSS): 搜尋卡片並加入購物車 (例如 3x灰流麗)
    前端 (HTML/JS/CSS)->>卡片資料庫 (cards.cdb): 載入並查詢卡片資訊
    前端 (HTML/JS/CSS)-->>使用者: 顯示卡片資訊與圖片
    使用者->>前端 (HTML/JS/CSS): 設定購買數量並點擊「優化」
    前端 (HTML/JS/CSS)->>前端 (HTML/JS/CSS): **輸出購物車需求 cart.json**
    
    rect rgb(200, 255, 200)
    note over 主控制器 (main_controller.py), 優化引擎 (caculator.py): 核心 Python 流程 (本地執行)
    主控制器 (main_controller.py)->>主控制器 (main_controller.py): 讀取 cart.json
    
    主控制器 (main_controller.py)->>爬蟲模組 (scraper.py): **1. 並行爬取多種卡片資訊 (使用 target_ids)**
    爬蟲模組 (scraper.py)-->>主控制器 (main_controller.py): 返回原始商品資料
    
    主控制器 (main_controller.py)->>資料清理 (clean_csv.py): **2. 清理與過濾** (排除關鍵字, 檢查庫存)
    資料清理 (clean_csv.py)-->>主控制器 (main_controller.py): 返回清理後資料
    
    主控制器 (main_controller.py)->>優化引擎 (caculator.py): **3. 演算法求解**
    優化引擎 (caculator.py)->>優化引擎 (caculator.py): **執行貪心算法** (生成初始解)
    優化引擎 (caculator.py)->>優化引擎 (caculator.py): **執行局部搜索** (迭代優化)
    優化引擎 (caculator.py)-->>主控制器 (main_controller.py): 返回最佳購買方案
    end
    
    主控制器 (main_controller.py)-->>使用者: 顯示最佳購買組合與總價