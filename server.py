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
import json
import sqlite3
import urllib.request
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# 全域共用資源（由 lifespan 在啟動時初始化）
# ============================================================
# passcode → cid 的對應字典，從 salix5 的 cid_table.json 載入
_PASSCODE_TO_CID_MAP: dict = {}
# 卡片資料庫的記憶體中 SQLite 連線
_LOCAL_CARD_DB = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    伺服器的生命週期管理：
    - 啟動時（yield 前）：從網路載入 CID 對應表和卡片資料庫到記憶體中
    - 關閉時（yield 後）：關閉資料庫連線
    """
    global _LOCAL_CARD_DB, _PASSCODE_TO_CID_MAP

    # --- 載入 CID 對應表 ---
    print("載入 CID 對應表 (cid_table.json) 到記憶體...")
    try:
        req = urllib.request.Request(
            "https://raw.githubusercontent.com/salix5/heliosphere/master/data/cid_table.json",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req) as response:
            cid_data = json.loads(response.read().decode("utf-8"))
            for cid_str, passcode_val in cid_data.items():
                _PASSCODE_TO_CID_MAP[str(passcode_val)] = cid_str
        print(f"成功載入 {len(_PASSCODE_TO_CID_MAP)} 筆 CID 對應資料。")
    except Exception as e:
        print(f"[警告] 載入 CID 對應資料失敗，卡片搜尋將缺少 CID 資訊: {e}")

    # --- 載入 cards.cdb 卡片資料庫 ---
    print("載入卡片資料庫 (cards.cdb) 到記憶體...")
    try:
        req = urllib.request.Request(
            "https://raw.githubusercontent.com/salix5/cdb/gh-pages/cards.cdb",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req) as response:
            db_data = response.read()

        with open("/tmp/temp_cards.cdb", "wb") as f:
            f.write(db_data)

        source_db = sqlite3.connect("/tmp/temp_cards.cdb")
        # check_same_thread=False 讓 FastAPI 的非同步環境可以安全地使用此連線
        _LOCAL_CARD_DB = sqlite3.connect(":memory:", check_same_thread=False)
        source_db.backup(_LOCAL_CARD_DB)
        source_db.close()
        os.remove("/tmp/temp_cards.cdb")
        print("成功載入 cards.cdb 到記憶體。")
    except Exception as e:
        print(f"[警告] 載入 cards.cdb 失敗，卡片搜尋功能將無法使用: {e}")

    yield  # 伺服器在此運行，等待請求

    # 關閉時清理資源
    if _LOCAL_CARD_DB:
        _LOCAL_CARD_DB.close()


# ============================================================
# 建立 FastAPI App 實例
# ============================================================
app = FastAPI(
    title="YGOscraper API",
    version="2.1.0",
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
from app.routers import projects, cart, cards, tasks  # noqa: E402

app.include_router(projects.router)
app.include_router(cart.router)
app.include_router(cards.router)
app.include_router(tasks.router)

# ============================================================
# 本地開發啟動入口
# ============================================================
if __name__ == "__main__":
    import uvicorn

    os.makedirs("data", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)
