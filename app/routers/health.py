"""
app/routers/health.py - 外部依賴健康檢查 API
================================================
檢查 config.py 中的外部 URL 是否可達，供前端顯示服務狀態。
"""
import asyncio
import logging
from typing import List

import httpx
from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.config import (
    CARD_IMAGE_BASE_URL,
    CARDS_CDB_URL,
    CID_TABLE_URL,
    KONAMI_DB_BASE_URL,
    RUTEN_API_BASE_URL,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["health"])


# ============================================================
# Schema（回應格式）
# ============================================================

class DependencyStatus(BaseModel):
    """單一外部依賴的檢查結果"""
    name: str           # 服務名稱（給人看的）
    url: str            # 檢查的 URL
    ok: bool            # 是否正常
    status_code: int | None = None   # HTTP 狀態碼（若有回應）
    error: str | None = None         # 錯誤訊息（若有）


class HealthCheckResponse(BaseModel):
    """整體健康檢查回應"""
    all_ok: bool                        # 是否全部正常
    results: List[DependencyStatus]     # 各依賴的檢查結果


class VersionResponse(BaseModel):
    """版本號回應"""
    version: str


# ============================================================
# 要檢查的外部服務清單
# ============================================================

_DEPENDENCIES = [
    {"name": "salix5 卡片資料庫 (CDB)", "url": CARDS_CDB_URL},
    {"name": "salix5 CID 對照表", "url": CID_TABLE_URL},
    {"name": "salix5 卡圖", "url": CARD_IMAGE_BASE_URL},
    {"name": "Konami 官方 DB", "url": KONAMI_DB_BASE_URL},
    {"name": "露天拍賣 API", "url": RUTEN_API_BASE_URL},
]


# ============================================================
# API 端點
# ============================================================

async def _check_one(client: httpx.AsyncClient, dep: dict) -> DependencyStatus:
    """
    檢查單一 URL 是否可達（用 HEAD 請求，不下載內容）。
    超時設定 5 秒，避免阻塞太久。
    """
    try:
        resp = await client.head(dep["url"], timeout=5.0, follow_redirects=True)
        ok = resp.status_code < 400
        return DependencyStatus(
            name=dep["name"],
            url=dep["url"],
            ok=ok,
            status_code=resp.status_code,
        )
    except httpx.HTTPError as e:
        return DependencyStatus(
            name=dep["name"],
            url=dep["url"],
            ok=False,
            error=str(type(e).__name__),
        )


@router.get("/version", response_model=VersionResponse)
async def get_version(request: Request) -> VersionResponse:
    """回傳應用程式版本號，從 FastAPI app.version 讀取。"""
    return VersionResponse(version=request.app.version)


@router.get("/health/dependencies", response_model=HealthCheckResponse)
async def check_dependencies():
    """
    檢查所有外部依賴服務是否可達。
    會並行發送 HEAD 請求，通常 1-3 秒內完成。
    """
    async with httpx.AsyncClient() as client:
        tasks = [_check_one(client, dep) for dep in _DEPENDENCIES]
        results = await asyncio.gather(*tasks)

    all_ok = all(r.ok for r in results)

    if not all_ok:
        failed = [r.name for r in results if not r.ok]
        logger.warning(f"外部依賴檢查異常: {failed}")

    return HealthCheckResponse(all_ok=all_ok, results=results)
