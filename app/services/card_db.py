"""
app/services/card_db.py - 卡片資料庫服務（含未來自建 DB 預留介面）
==================================================================
[目前實作] 從 salix5 的公開資源載入：
  - cards.cdb   (SQLite 格式，含卡名/攻守/種族/屬性)
  - cid_table.json (passcode → CID 的轉換表)

[未來計畫] 當你自行建立並維護完整 DB 後（包含卡名、CID、卡號版本），
只需替換這個類別的內部實作，所有呼叫它的 API 不需要修改任何一行。

設計原則（Dependency Inversion）：
  所有路由（routers）只透過 CardDatabaseService 介面存取卡片資料，
  不直接接觸底層的 SQLite 連線或 HTTP 請求。
"""
import json
import sqlite3
import urllib.request
from typing import Optional


class CardDatabaseService:
    """
    卡片資料庫的統一存取介面。
    提供搜尋卡片、以及查詢 CID 等功能。

    使用方法：
        db = CardDatabaseService()
        await db.initialize()  # 伺服器啟動時呼叫一次
        results = db.search("青眼白龍")
    """

    def __init__(self):
        # cards.cdb 的記憶體 SQLite 連線
        self._db: Optional[sqlite3.Connection] = None
        # passcode (str) → cid (str) 的對應字典
        self._passcode_to_cid: dict = {}

    # ============================================================
    # 初始化（伺服器啟動時呼叫）
    # ============================================================

    def initialize(self) -> None:
        """
        從網路載入 CID 對應表與 cards.cdb 到記憶體。
        這個方法應在 FastAPI 的 lifespan 啟動事件中呼叫。
        """
        self._load_cid_table()
        self._load_card_db()

    def close(self) -> None:
        """關閉資料庫連線（伺服器關閉時呼叫）"""
        if self._db:
            self._db.close()
            self._db = None

    def _load_cid_table(self) -> None:
        """從 salix5 的 GitHub 載入 passcode → CID 的對應表"""
        print("載入 CID 對應表 (cid_table.json) 到記憶體...")
        try:
            req = urllib.request.Request(
                "https://raw.githubusercontent.com/salix5/heliosphere/master/data/cid_table.json",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req) as response:
                cid_data = json.loads(response.read().decode("utf-8"))
                self._passcode_to_cid = {
                    str(passcode_val): cid_str
                    for cid_str, passcode_val in cid_data.items()
                }
            print(f"成功載入 {len(self._passcode_to_cid)} 筆 CID 對應資料。")
        except Exception as e:
            print(f"[警告] 載入 CID 對應表失敗: {e}")

    def _load_card_db(self) -> None:
        """從 salix5 的 GitHub 下載 cards.cdb 並載入為記憶體 SQLite"""
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
            # check_same_thread=False 讓 FastAPI 的非同步環境可以安全使用此連線
            self._db = sqlite3.connect(":memory:", check_same_thread=False)
            source_db.backup(self._db)
            source_db.close()

            import os
            os.remove("/tmp/temp_cards.cdb")
            print("成功載入 cards.cdb 到記憶體。")
        except Exception as e:
            print(f"[警告] 載入 cards.cdb 失敗: {e}")

    # ============================================================
    # 查詢介面（所有路由都只透過這些方法存取卡片資料）
    # ============================================================

    def is_ready(self) -> bool:
        """回傳資料庫是否已初始化完成"""
        return self._db is not None

    def search(self, query: str, limit: int = 50) -> list[dict]:
        """
        以關鍵字搜尋卡片（模糊搜尋）。

        Args:
            query: 搜尋關鍵字（例如：「青眼」）
            limit: 最多回傳的結果數量
        Returns:
            卡片資料的 list，每項包含 passcode, name, cid, type, atk, def, level,
            race, attribute, desc, image_url
        """
        if not self._db:
            return []

        try:
            cursor = self._db.cursor()
            cursor.execute(
                """
                SELECT t.id, t.name, d.type, d.atk, d.def,
                       d.level, d.race, d.attribute, t.desc
                FROM texts t
                JOIN datas d ON t.id = d.id
                WHERE t.name LIKE ?
                LIMIT ?
                """,
                (f"%{query}%", limit),
            )
            rows = cursor.fetchall()
        except Exception as e:
            print(f"搜尋卡片時發生錯誤: {e}")
            return []

        results = []
        for row in rows:
            pwd, name, c_type, atk, c_def, level, race, attr, desc = row
            passcode_str = str(pwd)
            cid = self._passcode_to_cid.get(passcode_str)
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
                    "image_url": f"https://raw.githubusercontent.com/salix5/query-data/gh-pages/pics/{passcode_str}.jpg",
                }
            )

        return results

    def get_cid_by_passcode(self, passcode: str) -> Optional[str]:
        """
        根據 passcode 查詢對應的 CID。

        Args:
            passcode: YGOPro 的 Passcode（8 位數 ID）
        Returns:
            CID 字串，若無對應則回傳 None
        """
        return self._passcode_to_cid.get(str(passcode))
