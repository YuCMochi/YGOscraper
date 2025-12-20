## 系統架構與流程

```mermaid
sequenceDiagram
    participant 使用者
    participant GUI
    participant 主控制器 (main_controller.py)
    participant 檔案創建 (file_genarator.py)
    participant 爬蟲模組 (scraper.py)
    participant 資料清理 (clean_csv.py)
    participant 計算器 (caculator.py)

    使用者->>GUI: 打開程式創建新購買專案
    GUI->>主控制器 (main_controller.py):請求執行 

    主控制器 (main_controller.py)->>檔案創建 (file_genarator.py): 在 /data資料夾下創建新資料夾目錄&空白的 cart.json
    檔案創建 (file_genarator.py)-->>主控制器 (main_controller.py): 偵測檔案已創建完成
    主控制器 (main_controller.py)-->>GUI: 呼叫已就緒 回傳資料夾位置
    使用者->>GUI: 以UI輸入 cart.json所需資料
    GUI->>主控制器 (main_controller.py): 通知已更新 cart.json

    主控制器 (main_controller.py)->>爬蟲模組 (scraper.py): 請求執行＆輸入 cart.json
    爬蟲模組 (scraper.py)-->>主控制器 (main_controller.py): 返回原始商品資料 ruten_data.csv
    
    主控制器 (main_controller.py)->>資料清理 (clean_csv.py): 請求執行＆輸入 ruten_data.csv
    資料清理 (clean_csv.py)-->>主控制器 (main_controller.py): 返回清理後資料 cleaned_ruten_data.csv
    
    主控制器 (main_controller.py)->>計算器 (caculator.py): 請求執行＆輸入 ruten_data.csv
    計算器 (caculator.py)->>計算器 (caculator.py): 產生計算過程 caculate.log
    計算器 (caculator.py)-->>主控制器 (main_controller.py): 返回最佳購買方案 plan.json
    主控制器 (main_controller.py)-->>GUI: 依照 plan.json 顯示結果
```

## 檔案目錄
每當單次使用 main_controller.py 都會在/data下創建一個名字是 年月日_時分秒 的資料夾

```mermaid
flowchart TB
    Root["/data"] --> Src@{ label: "<span style=\"caret-color:\">%Y%m%d_%H%M%S（單次輸出資料夾）</span>" }
    Src --> Components["cart.json"] & Utils["ruten_data.csv"] & n1["cleaned_ruten_data.csv"] & n2["caculate.log"] & n3["plan.json<br>"]

    Src@{ shape: rect}
```

## GUI 開發接口說明

本系統已預留以下接口供未來圖形介面 (GUI) 開發整合使用：

1.  **一鍵執行 (`start_process`)**
    *   **位置**: `main_controller.py` -> `start_process()`
    *   **用途**: 自動執行完整流程（建檔 -> 爬蟲 -> 清理 -> 計算）。
    *   **回傳**: 該次任務的資料夾路徑。

2.  **分段控制 (`MainController` Class)**
    *   **位置**: `main_controller.py` -> `MainController` 類別
    *   **方法**:
        *   `initialize_project()`: 建立專案資料夾。
        *   `run_scraper()`: 執行爬蟲。
        *   `run_cleaner()`: 執行資料清理。
        *   `run_calculator()`: 執行最佳化計算。
    *   **用途**: 允許 GUI 逐步執行並更新進度條或狀態顯示。

3.  **人機互動暫停點 (`wait_for_user_input`)**
    *   **位置**: `main_controller.py` -> `wait_for_user_input()`
    *   **用途**: 流程暫停點。GUI 可在此時彈出視窗讓使用者編輯 `cart.json`，確認後再繼續。

4.  **專案路徑獲取 (`create_project_environment`)**
    *   **位置**: `file_genarator.py` -> `FileGenerator.create_project_environment()`
    *   **用途**: 取得當前任務的絕對路徑，方便 GUI 讀取產出的 `plan.json` 或開啟資料夾。
