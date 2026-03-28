import os
import json
import datetime
import shutil

class FileGenerator:
    def __init__(self, base_dir='data'):
        # 設定基礎資料夾路徑，預設為 'data'
        self.base_dir = base_dir
        # 如果資料夾不存在，就建立它
        os.makedirs(self.base_dir, exist_ok=True)

    def create_project_environment(self) -> str:
        """
        建立一個以「現在時間」命名的專案資料夾，並準備好購物車設定檔。
        回傳: 新建立的資料夾完整路徑
        """
        # 1. 取得現在時間，格式為：年月日_時分秒 (例如：20231220_120000)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 2. 組合出完整的資料夾路徑
        project_path = os.path.join(self.base_dir, timestamp)
        
        # 3. 實際建立資料夾
        os.makedirs(project_path, exist_ok=True)
        print(f"已建立專案資料夾: {project_path}")

        # 4. 準備購物車設定檔 (cart.json)
        # 目標路徑：新資料夾裡面
        target_cart_path = os.path.join(project_path, "cart.json")
        
        # 模板路徑：專案根目錄下的 data 資料夾裡面是否有預設的 cart.json
        template_cart_path = os.path.join(self.base_dir, "cart.json")
        
        if os.path.exists(template_cart_path):
            # 如果有找到模板，直接複製一份過去
            shutil.copy(template_cart_path, target_cart_path)
            print(f"已從模板複製購物車設定檔到: {target_cart_path}")
        else:
            # 如果沒找到模板，就建立一個全新的空白設定檔
            print("未找到模板，正在建立全新的空白購物車設定檔...")
            default_cart_structure = {
                "global_settings": {
                    "default_shipping_cost": 60,  # 預設運費
                    "min_purchase_limit": 0,      # 最低消費限制
                    "global_exclude_keywords": [], # 要排除的關鍵字
                    "global_exclude_seller": []    # 要排除的賣家 ID
                },
                "shopping_cart": [] # 購物清單 (空白)
            }
            # 將設定寫入檔案
            with open(target_cart_path, 'w', encoding='utf-8') as f:
                json.dump(default_cart_structure, f, ensure_ascii=False, indent=4)
            print(f"已建立空白設定檔: {target_cart_path}")

        # 回傳新資料夾的絕對路徑，方便後續程式使用
        return os.path.abspath(project_path)

if __name__ == "__main__":
    # 這是測試用的區塊，直接執行此檔案時會跑這裡
    generator = FileGenerator()
    new_project_dir = generator.create_project_environment()
    print(f"測試完成，新專案位置: {new_project_dir}")