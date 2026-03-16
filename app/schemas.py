"""
app/schemas.py - 統一的 Pydantic 資料模型定義
=================================================
這個檔案是後端資料的「守門員」。
所有進出 API 的資料格式都在這裡統一定義，確保格式正確。
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union


# ============================================================
# 卡號相關 Schema
# ============================================================

class CardNumberInfo(BaseModel):
    """
    單一卡號版本的完整資訊。
    例如：{ "card_number": "DABL-JP035", "rarity_name": "Secret Rare", "pack_name": "..." }
    """
    card_number: str
    rarity_name: Optional[str] = ""
    pack_name: Optional[str] = ""


# ============================================================
# 購物車項目 Schema
# ============================================================

class CartItemFull(BaseModel):
    """
    購物車中單一卡片的完整資料。
    
    這個 Model 修正了以前版本的三個問題：
    1. 增加了前端會傳送的 passcode, cid, type, atk, def... 等欄位
    2. target_card_numbers 改為支援「物件格式（含稀有度）」與「舊版字串格式」的聯合型別
    3. 所有非必要欄位都設定為 Optional，避免前端舊資料造成 422 錯誤
    """
    # 必填欄位
    card_name_zh: str                                                    # 繁體中文卡名
    required_amount: int = Field(default=1, ge=1)                       # 需要的數量 (最少1)

    # 卡片識別碼（新版前端會傳送，舊資料可能缺少）
    passcode: Optional[str] = None                                       # YGOPro 的 Passcode (8位數ID)
    cid: Optional[int] = None                                           # Konami 官方資料庫 ID (用於爬卡號)

    # 卡片屬性（從 cards.cdb 取得）
    type: Optional[int] = None                                          # 卡片類型 (以位元旗標儲存)
    atk: Optional[int] = None                                          # 攻擊力
    def_: Optional[int] = Field(default=None, alias="def")             # 守備力 (def 是 Python 保留字，需用別名)
    level: Optional[int] = None                                        # 等級/階級
    race: Optional[int] = None                                         # 種族 (以位元旗標儲存)
    attribute: Optional[int] = None                                    # 屬性 (以位元旗標儲存)
    image_url: Optional[str] = None                                    # 卡圖網址

    # 目標卡號列表：支援新版（含稀有度的物件）與舊版（純字串）兩種格式
    target_card_numbers: List[Union[CardNumberInfo, str]] = Field(default_factory=list)

    # UI 狀態暫存欄位（前端會傳送，後端不使用，但需要接收以免 422）
    ui_inputVisible: Optional[bool] = False
    ui_inputValue: Optional[str] = ""

    class Config:
        # 允許使用 alias（例如 "def" 對應 def_）
        populate_by_name = True


# ============================================================
# 全域設定 Schema
# ============================================================

class GlobalSettings(BaseModel):
    """購物車的全域設定"""
    default_shipping_cost: int = Field(default=60)             # 預設運費（元）
    min_purchase_limit: int = Field(default=0)                 # 賣家最低消費門檻（0 = 不設限）
    global_exclude_keywords: List[str] = Field(default_factory=list)  # 排除的關鍵字（如：卡套）
    global_exclude_seller: List[str] = Field(default_factory=list)    # 封鎖的賣家 ID 列表


# ============================================================
# 購物車整體 Schema
# ============================================================

class CartData(BaseModel):
    """
    整份購物車資料（cart.json 的完整結構）。
    """
    shopping_cart: List[CartItemFull] = Field(default_factory=list)
    global_settings: GlobalSettings = Field(default_factory=GlobalSettings)


# ============================================================
# 專案相關 Schema
# ============================================================

class ProjectCreate(BaseModel):
    """建立新專案的請求（目前不需要任何參數）"""
    pass


class ProjectPreview(BaseModel):
    """用於專案列表頁的簡易預覽資訊"""
    id: str                                                     # 專案 ID（時間戳）
    item_count: int = 0                                         # 購物車內的卡片數量
    preview_names: List[str] = Field(default_factory=list)     # 前幾張卡片的名稱（用於預覽）
