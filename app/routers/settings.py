"""
app/routers/settings.py - 全域設定管理 API 路由
=================================================
負責讀取/更新跨專案的全域設定（data/global_settings.json）。

端點：
- GET  /api/settings : 讀取全域設定
- PUT  /api/settings : 更新全域設定
"""
from fastapi import APIRouter, HTTPException
from app.schemas import GlobalSettings
from app.services import storage

router = APIRouter(prefix="/api", tags=["settings"])


@router.get("/settings", response_model=GlobalSettings)
async def get_settings():
    """讀取全域設定（data/global_settings.json）。"""
    return storage.get_global_settings()


@router.put("/settings", response_model=GlobalSettings)
async def update_settings(settings: GlobalSettings):
    """
    更新全域設定。
    Pydantic 會自動驗證格式（例如數值範圍、型別）。
    更新後的設定會套用於之後新建的專案。
    """
    try:
        data = settings.model_dump()
        storage.save_global_settings(data)
        return data
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
