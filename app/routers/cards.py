"""
app/routers/cards.py - 卡片搜尋與卡號爬取的 API 路由
=====================================================
負責所有與卡片查詢有關的操作：
- GET /api/cards/search               : 在本地 SQLite (cards.cdb) 中搜尋卡片
- GET /api/cards/cid/{cid}/card-numbers : 向 Konami 官網爬取指定卡片的所有版本卡號

現在透過 server 模組的 card_db（CardDatabaseService 實例）存取卡片資料，
不再直接接觸底層的 SQLite 連線或全域變數。
"""
import server as _server  # 取得共用的 card_db 實例

from fastapi import APIRouter, HTTPException
from app.services.konami_scraper_service import KonamiScraperService

router = APIRouter(prefix="/api", tags=["cards"])

# 初始化 Konami 爬蟲服務
_konami = KonamiScraperService()


@router.get("/cards/search")
async def search_cards(q: str):
    """
    使用本地記憶體中的 SQLite (cards.cdb) 搜尋卡片。
    
    支援模糊搜尋（LIKE %關鍵字%），回傳最多 50 筆結果。
    """
    if not q or not _server.card_db.is_ready():
        return []

    try:
        return _server.card_db.search(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards/cid/{cid}/card-numbers")
async def get_card_numbers_by_cid(cid: int):
    """
    根據 Konami 的 CID，爬取該卡片的所有版本卡號。
    
    例如：CID=4007 → [{"card_number": "DABL-JP035", "rarity_name": "R", ...}, ...]
    """
    try:
        print(f"正在爬取 CID {cid} 的卡號...")
        card_numbers = _konami.get_card_numbers(cid)
        print(f"CID {cid} 共取得 {len(card_numbers)} 個版本")
        return {"cid": cid, "card_numbers": card_numbers}
    except Exception as e:
        print(f"爬取 CID {cid} 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"爬取卡號失敗: {str(e)}")
