# 遊戲王卡片即時比價工具 (Ruten Edition)

> 專門搜尋「露天拍賣」資料、使用非公開 API，採用貪心演算法+局部搜索優化找出最低總價組合。  
> 開發環境：Python + JavaScript 前後端分離架構。

---

## 專案目標

1. **即時比價**：使用者輸入卡片名稱 → 立即向露天 API 取回最新商品。
2. **智慧過濾**：自動排除標題不符、價格異常、缺貨等「錯誤商品」。
3. **最佳組合**：使用兩階段演算法（貪心初始解+局部搜索優化）計算「指定張數」的最低總價（含運費）。
4. **互動體驗**：  
   - 前端使用 SQL.js 動態載入卡片資料庫，支援模糊搜尋。  
   - 使用者可將多種卡片加入購物車並指定數量。  
5. **一鍵比價**：點擊「優化」按鈕自動執行爬蟲、資料清理和最佳組合計算。

---

## 系統架構

```mermaid
sequenceDiagram
    participant 使用者
    participant 前端 (HTML/JS/CSS)
    participant 卡片資料庫 (cards.cdb)
    participant 主控制器 (main_controller.py)
    participant 爬蟲模組 (scraper.py)
    participant 資料清理 (clean_csv.py)
    participant 優化引擎 (card_optimizer.py)

    使用者->>前端 (HTML/JS/CSS): 搜尋卡片並加入購物車
    前端 (HTML/JS/CSS)->>卡片資料庫 (cards.cdb): 載入並查詢卡片資訊
    前端 (HTML/JS/CSS)-->>使用者: 顯示卡片資訊與圖片
    使用者->>前端 (HTML/JS/CSS): 設定購買數量並點擊「優化」
    前端 (HTML/JS/CSS)->>前端 (HTML/JS/CSS): 將購物車資訊儲存至 cart.json
    使用者->>主控制器 (main_controller.py): 執行主控制流程
    主控制器 (main_controller.py)->>主控制器 (main_controller.py): 讀取 cart.json
    主控制器 (main_controller.py)->>爬蟲模組 (scraper.py): 並行爬取多種卡片資訊
    爬蟲模組 (scraper.py)-->>主控制器 (main_controller.py): 返回原始商品資料 (CSV)
    主控制器 (main_controller.py)->>資料清理 (clean_csv.py): 清理每種卡片的資料
    資料清理 (clean_csv.py)-->>主控制器 (main_controller.py): 返回清理後資料
    主控制器 (main_controller.py)->>優化引擎 (card_optimizer.py): 計算最佳購買組合
    優化引擎 (card_optimizer.py)->>優化引擎 (card_optimizer.py): 執行貪心算法獲得初始解
    優化引擎 (card_optimizer.py)->>優化引擎 (card_optimizer.py): 執行局部搜索優化
    優化引擎 (card_optimizer.py)-->>主控制器 (main_controller.py): 返回最佳購買方案
    主控制器 (main_controller.py)-->>使用者: 顯示最佳購買組合與總價
