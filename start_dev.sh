#!/bin/bash

# 獲取腳本所在目錄的絕對路徑，確保在哪個資料夾執行都沒問題
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 正在啟動 YGO Scraper 測試環境..."
echo "=========================================="

# 1. 啟動後端 (跑在背景)
echo "📦 [後端] 啟動 FastAPI 伺服器..."
cd "$PROJECT_DIR"
source .venv/bin/activate
uvicorn server:app --reload &
BACKEND_PID=$!

# 2. 啟動前端 (跑在背景)
echo "🎨 [前端] 啟動 Vite 開發伺服器..."
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo "=========================================="
echo "✅ 啟動完畢！"
echo "🌐 前端網址: http://localhost:5173"
echo "🔌 後端 API: http://127.0.0.1:8000"
echo "💡 按下 [Ctrl + C] 即可同時關閉前後端"
echo "=========================================="

# 捕捉 Ctrl+C (SIGINT) 或結束訊號，優雅地關閉兩個伺服器
cleanup() {
    echo ""
    echo "🛑 正在關閉伺服器..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "👋 已全部關閉，掰掰！"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待背景程序，讓腳本持續執行不要馬上結束
wait $BACKEND_PID $FRONTEND_PID
