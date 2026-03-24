"""
app/config.py - 外部服務 URL 與設定的統一管理
===============================================
所有會存取外部服務的 URL 都集中在這裡。
當上游資源的網址變動時，只需要修改這一個檔案。

使用方法：
    from app.config import CARDS_CDB_URL, CID_TABLE_URL
"""

# ============================================================
# salix5 GitHub 資源（卡片資料庫相關）
# ============================================================

# 卡片資料庫（SQLite 格式），啟動時下載並載入記憶體
CARDS_CDB_URL = (
    "https://github.com/salix5/cdb/releases/download/snapshot/cards.cdb"
)

# Passcode → CID 的對照表（JSON 格式），啟動時下載並載入記憶體
CID_TABLE_URL = (
    "https://raw.githubusercontent.com/salix5/heliosphere/master/data/cid_table.json"
)

# 卡片圖片的 Base URL，使用時需在後面加上 "{passcode}.jpg"
CARD_IMAGE_BASE_URL = (
    "https://raw.githubusercontent.com/salix5/query-data/refs/heads/master/pics/"
)

# ============================================================
# Konami 官方資料庫（爬蟲用）
# ============================================================

# Konami 官方卡片資料庫的搜尋頁面，使用時需帶入 cid 參數
# 完整格式：f"{KONAMI_DB_BASE_URL}?ope=2&cid={cid}&request_locale=ja"
KONAMI_DB_BASE_URL = (
    "https://www.db.yugioh-card.com/yugiohdb/card_search.action"
)

# ============================================================
# 露天拍賣 API（爬蟲用）
# ============================================================

# 露天拍賣的 API Base URL
RUTEN_API_BASE_URL = "https://rtapi.ruten.com.tw/api"

# 露天拍賣商品圖片的 Base URL
RUTEN_IMAGE_BASE_URL = "https://gcs.rimg.com.tw"
