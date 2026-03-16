"""
app/routers/cart.py - 購物車管理的 API 路由
============================================
負責處理特定專案的購物車讀寫操作：
- GET  /api/projects/{project_name}/cart : 讀取購物車內容
- POST /api/projects/{project_name}/cart : 儲存/更新購物車內容
"""
import os
import json

from fastapi import APIRouter, HTTPException
from app.schemas import CartData, GlobalSettings

router = APIRouter(prefix="/api", tags=["cart"])


@router.get("/projects/{project_name}/cart")
async def get_cart(project_name: str):
    """
    讀取特定專案的購物車內容（cart.json）。
    若該專案的 cart.json 不存在，會回傳一份空白的預設結構。
    """
    path = os.path.abspath(os.path.join("data", project_name, "cart.json"))
    
    if not os.path.exists(path):
        # 回傳預設的空購物車結構
        return {
            "shopping_cart": [],
            "global_settings": {
                "default_shipping_cost": 60,
                "min_purchase_limit": 0,
                "global_exclude_keywords": [],
                "global_exclude_seller": [],
            },
        }
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取購物車失敗: {str(e)}")


@router.post("/projects/{project_name}/cart")
async def save_cart(project_name: str, cart_data: CartData):
    """
    儲存/更新特定專案的購物車內容（cart.json）。
    
    Pydantic 會在資料進入這裡之前自動驗證格式。
    若格式錯誤（如缺少必填欄位），FastAPI 會自動回傳 422 錯誤說明。
    """
    path = os.path.abspath(os.path.join("data", project_name, "cart.json"))
    
    try:
        # model_dump() 將 Pydantic Model 轉回 dict，exclude_none=False 保留所有欄位
        # mode="json" 確保特殊型別（如 Union）正確序列化
        data_dict = cart_data.model_dump(mode="json", by_alias=True)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"儲存購物車失敗: {str(e)}")
