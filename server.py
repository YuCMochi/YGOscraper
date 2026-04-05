"""
server.py - YGOscraper API 應用程式入口點
==========================================
這個檔案是整個後端的啟動入口，職責非常單純：
1. 在伺服器啟動時，載入共用資源（cards.cdb 資料庫、CID 對應表）到記憶體
2. 設定 CORS 允許前端存取
3. 將各功能模組的 router 掛載到 FastAPI App 上

所有 API 端點的實作邏輯已移至 app/routers/ 下的對應模組：
  - app/routers/projects.py : 專案管理
  - app/routers/cart.py     : 購物車讀寫
  - app/routers/cards.py    : 卡片搜尋與卡號爬取
  - app/routers/tasks.py    : 爬蟲執行與結果讀取

所有 Pydantic 資料結構已移至 app/schemas.py 統一管理。
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 引入 CardDatabaseService，統一管理卡片資料庫的載入與查詢
from app.services.card_db import CardDatabaseService

# ============================================================
# 建立共用的 CardDatabaseService 實例
# 這個實例會在整個應用程式生命週期中共用（包含所有 routers）
# ============================================================
card_db = CardDatabaseService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    伺服器的生命週期管理：
    - 啟動時（yield 前）：初始化 CardDatabaseService（載入 cards.cdb + CID 對應表）
    - 關閉時（yield 後）：關閉資料庫連線

    透過 app.state 把 card_db 共享給所有 router，
    這樣 router 就不需要反向 import server 來取得它（消除循環引用）。
    """
    # 初始化卡片資料庫（內部會自動載入 cdb + cid_table.json）
    card_db.initialize()

    # 掛載到 app.state，讓 router 透過 request.app.state.card_db 取用
    app.state.card_db = card_db

    yield  # 伺服器在此運行，等待請求

    # 伺服器關閉時清理資源
    card_db.close()


# ============================================================
# 建立 FastAPI App 實例
# ============================================================
app = FastAPI(
    title="YGOscraper API",
    version="0.4.3",
    description="遊戲王卡片採購最佳化工具的後端 API",
    lifespan=lifespan,
)

# ============================================================
# CORS 設定（允許 React 開發伺服器存取）
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 掛載 API 路由模組
# ============================================================
from app.routers import cards, cart, health, projects, settings, tasks  # noqa: E402

app.include_router(projects.router)
app.include_router(cart.router)
app.include_router(cards.router)
app.include_router(tasks.router)
app.include_router(health.router)
app.include_router(settings.router)

# ============================================================
# 本地開發啟動入口
# ============================================================
if __name__ == "__main__":
    import uvicorn

    os.makedirs("data", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
