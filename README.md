# 網路爬蟲專案

這是一個使用 Python 開發的網路爬蟲專案。

## 環境需求

- Python 3.8 或更高版本
- pip（Python 套件管理器）

## 安裝步驟

1. 克隆此專案到本地
2. 安裝所需套件：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 修改 `scraper.py` 中的爬蟲邏輯
2. 執行程式：
   ```bash
   python scraper.py
   ```

## 功能特點

- 自動處理網路請求
- 錯誤處理和日誌記錄
- 資料儲存為 CSV 格式
- 可自定義的資料解析邏輯

## 注意事項

- 請確保遵守目標網站的爬蟲政策
- 建議加入適當的延遲，避免對目標網站造成負擔
- 定期檢查並更新 User-Agent 