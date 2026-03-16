"""
app/routers/cards.py - 卡片搜尋與卡號爬取的 API 路由
=====================================================
負責所有與卡片查詢有關的操作：
- GET /api/cards/search               : 在本地 SQLite (cards.cdb) 中搜尋卡片
- GET /api/cards/cid/{cid}/card-numbers : 向 Konami 官網爬取指定卡片的所有版本卡號

注意：本路由需要存取在 server.py 的 lifespan 中初始化的全域資源
（_LOCAL_CARD_DB 和 _PASSCODE_TO_CID_MAP），目前透過 server 模組的全域變數取得。
未來 Phase 2（CardDatabaseService 封裝）將改為依賴注入的方式。
"""
import server as _server  # 暫時從 server 模組取得共用的全域資源

from fastapi import APIRouter, HTTPException
from konami_scraper import KonamiScraper

router = APIRouter(prefix="/api", tags=["cards"])

# 初始化 Konami 爬蟲（此類別無狀態，可以安全地在模組層建立）
_konami_scraper = KonamiScraper()


@router.get("/cards/search")
async def search_cards(q: str):
    """
    使用本地記憶體中的 SQLite (cards.cdb) 搜尋卡片。
    
    支援模糊搜尋（LIKE %關鍵字%），回傳最多 50 筆結果。
    回傳欄位包含：passcode, name, cid, type, atk, def, level, race, attribute, desc, image_url
    """
    if not q or not _server._LOCAL_CARD_DB:
        return []

    try:
        cursor = _server._LOCAL_CARD_DB.cursor()
        cursor.execute(
            """
            SELECT t.id, t.name, d.type, d.atk, d.def, d.level, d.race, d.attribute, t.desc
            FROM texts t
            JOIN datas d ON t.id = d.id
            WHERE t.name LIKE ? LIMIT 50
            """,
            (f"%{q}%",),
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            pwd, name, c_type, atk, c_def, level, race, attr, desc = row
            passcode_str = str(pwd)
            # 從 passcode → cid 對應表中查找 CID
            cid = _server._PASSCODE_TO_CID_MAP.get(passcode_str)
            results.append(
                {
                    "passcode": passcode_str,
                    "name": name,
                    "cid": cid,
                    "type": c_type,
                    "atk": atk,
                    "def": c_def,
                    "level": level,
                    "race": race,
                    "attribute": attr,
                    "desc": desc,
                    # 卡圖從 GitHub 公開資源取得，不需要自行儲存
                    "image_url": f"https://raw.githubusercontent.com/salix5/query-data/gh-pages/pics/{passcode_str}.jpg",
                }
            )

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cards/cid/{cid}/card-numbers")
async def get_card_numbers_by_cid(cid: int):
    """
    根據 Konami 的 CID，向 Konami 官方資料庫爬取該卡片的所有版本卡號。
    
    例如：CID=4007 → [{"card_number": "DABL-JP035", "rarity_name": "R", ...}, ...]
    這個資料用於後續爬取露天拍賣時的搜尋關鍵字。
    """
    try:
        print(f"正在爬取 CID {cid} 的卡號...")
        data = _konami_scraper.scrape_cids([str(cid)])
        
        card_numbers = []
        if data and str(cid) in data:
            for v in data[str(cid)]:
                if v.get("card_number"):
                    card_numbers.append(
                        {
                            "card_number": v["card_number"],
                            "rarity_name": v.get("rarity_name", ""),
                            "pack_name": v.get("pack_name", ""),
                        }
                    )
        
        print(f"CID {cid} 共取得 {len(card_numbers)} 個版本")
        return {"cid": cid, "card_numbers": card_numbers}
    except Exception as e:
        print(f"爬取 CID {cid} 時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"爬取卡號失敗: {str(e)}")
