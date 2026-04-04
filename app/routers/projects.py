"""
app/routers/projects.py - 專案管理的 API 路由
===============================================
負責處理所有關於「專案」的操作：
- GET  /api/projects : 取得所有專案的列表
- POST /api/projects : 建立一個全新的專案
"""
import os

from fastapi import APIRouter, HTTPException

from app.services import storage
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api", tags=["projects"])

# 初始化專案建立服務
_project_service = ProjectService()


@router.get("/projects")
async def get_project_list():
    """
    取得所有已建立的專案列表，並附上預覽資訊。
    
    回傳格式：
    [
      { "id": "20240101_120000", "item_count": 3, "preview_names": ["青眼白龍", ...] },
      ...
    ]
    """
    return storage.list_projects()


@router.post("/projects")
async def create_project():
    """
    建立一個全新的專案資料夾（以當下時間戳命名），並初始化空白的購物車檔案。
    """
    try:
        new_path = _project_service.create_project()
        return {"path": new_path, "name": os.path.basename(new_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """
    軟刪除專案：將專案資料夾移到 _legacy/trash/（可手動恢復）。
    """
    try:
        storage.delete_project(project_id)
        return {"message": f"專案 '{project_id}' 已刪除"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
