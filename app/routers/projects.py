"""
app/routers/projects.py - 專案管理的 API 路由
===============================================
負責處理所有關於「專案」的操作：
- GET  /api/projects         : 取得所有專案的列表
- POST /api/projects         : 建立一個全新的專案
"""
import os
import json

from fastapi import APIRouter, HTTPException
from file_genarator import FileGenerator

# 建立這個 router 的實例，所有路由都會加上 /api 前綴
# tags 是用來在 /docs 頁面上分類顯示的標籤
router = APIRouter(prefix="/api", tags=["projects"])

# 初始化專案建立工具
_file_gen = FileGenerator()


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
    projects_info = []

    if os.path.exists("data"):
        for d in os.listdir("data"):
            project_path = os.path.join("data", d)
            if os.path.isdir(project_path):
                cart_path = os.path.join(project_path, "cart.json")
                # 預設的空預覽資料
                preview = {"id": d, "item_count": 0, "preview_names": []}

                # 嘗試讀取購物車以顯示預覽資料
                if os.path.exists(cart_path):
                    try:
                        with open(cart_path, "r", encoding="utf-8") as f:
                            cart_data = json.load(f)
                        items = cart_data.get("shopping_cart", [])
                        preview["item_count"] = len(items)
                        # 只顯示前 3 張卡做預覽
                        preview["preview_names"] = [
                            item.get("card_name_zh", "未知卡片") for item in items[:3]
                        ]
                    except Exception:
                        # 讀取失敗就顯示空預覽，不影響整個列表
                        pass

                projects_info.append(preview)

    # 依照專案 ID（時間戳）降序排列，最新的排最前面
    projects_info.sort(key=lambda x: x["id"], reverse=True)
    return projects_info


@router.post("/projects")
async def create_project():
    """
    建立一個全新的專案資料夾（以當下時間戳命名），並初始化空白的購物車檔案。
    
    回傳格式：
    { "path": "/absolute/path/to/project", "name": "20240101_120000" }
    """
    try:
        new_path = _file_gen.create_project_environment()
        return {"path": new_path, "name": os.path.basename(new_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
