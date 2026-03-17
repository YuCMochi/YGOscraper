"""
app/services/project_service.py - 專案建立服務
===============================================
負責建立新專案的資料夾環境與初始化購物車。
這個檔案是原本 `file_genarator.py` 的重構版本：
- 修正拼字錯誤 (genarator → generator)
- 改用 app/services/storage.py 管理預設結構，避免重複定義
"""
import os
import datetime
import shutil

from app.services.storage import DATA_DIR, _DEFAULT_CART
import json


class ProjectService:
    """
    負責建立新專案目錄與初始購物車設定。

    使用方法：
        service = ProjectService()
        path = service.create_project()
    """

    def __init__(self, base_dir: str = DATA_DIR):
        """
        Args:
            base_dir: 專案資料夾的根目錄，預設為 'data'
        """
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def create_project(self) -> str:
        """
        建立一個以「現在時間」命名的新專案資料夾，
        並初始化一份空白的購物車設定檔（cart.json）。

        若 data/cart.json 存在（模板），會複製一份過去；
        否則建立全新的空白購物車。

        Returns:
            新建立的專案資料夾的絕對路徑
        """
        # 以時間戳作為專案 ID（例如：20231220_120000）
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_path = os.path.join(self.base_dir, timestamp)
        os.makedirs(project_path, exist_ok=True)
        print(f"已建立專案資料夾: {project_path}")

        target_cart_path = os.path.join(project_path, "cart.json")
        template_cart_path = os.path.join(self.base_dir, "cart.json")

        if os.path.exists(template_cart_path):
            # 若有模板購物車，直接複製
            shutil.copy(template_cart_path, target_cart_path)
            print(f"已從模板複製購物車到: {target_cart_path}")
        else:
            # 否則建立空白購物車
            with open(target_cart_path, "w", encoding="utf-8") as f:
                json.dump(_DEFAULT_CART, f, ensure_ascii=False, indent=4)
            print(f"已建立空白購物車: {target_cart_path}")

        return os.path.abspath(project_path)
