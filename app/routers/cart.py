"""
app/routers/cart.py - 購物車管理的 API 路由
============================================
負責處理特定專案的購物車讀寫操作：
- GET  /api/projects/{project_name}/cart : 讀取購物車內容
- POST /api/projects/{project_name}/cart : 儲存/更新購物車內容
"""
from fastapi import APIRouter, HTTPException
from app.schemas import CartData
from app.services import storage

router = APIRouter(prefix="/api", tags=["cart"])


@router.get("/projects/{project_name}/cart")
async def get_cart(project_name: str):
    """讀取特定專案的購物車內容（cart.json）。"""
    try:
        return storage.get_cart(project_name)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_name}/cart")
async def save_cart(project_name: str, cart_data: CartData):
    """
    儲存/更新特定專案的購物車內容（cart.json）。
    Pydantic 會在資料進入此處前自動驗證格式。
    """
    try:
        # model_dump 將 Pydantic Model 轉為 dict，by_alias=True 確保 "def" 欄位正確輸出
        data_dict = cart_data.model_dump(mode="json", by_alias=True)
        storage.save_cart(project_name, data_dict)
        return {"status": "success"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
