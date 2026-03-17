"""
app/services/storage.py - 專案資料的統一讀寫管理
=================================================
這個模組是所有「讀取/寫入 JSON 和 CSV 檔案」的唯一窗口（Repository Pattern）。

好處：
- 任何地方需要讀取購物車，只需呼叫 storage.get_cart(project_name)
- 格式驗證集中在這裡，不會到處散落 with open(...) 的程式碼
- 未來要換成資料庫（SQLite/PostgreSQL），只需修改這個檔案即可
"""
import os
import json
import copy  # 用於 deepcopy，確保預設結構每次回傳獨立的物件

# ============================================================
# 常數設定
# ============================================================
DATA_DIR = "data"

# 預設的空白購物車結構
_DEFAULT_CART = {
    "shopping_cart": [],
    "global_settings": {
        "default_shipping_cost": 60,
        "min_purchase_limit": 0,
        "global_exclude_keywords": [],
        "global_exclude_seller": [],
    },
}


def _get_project_dir(project_name: str) -> str:
    """回傳專案資料夾的絕對路徑"""
    return os.path.abspath(os.path.join(DATA_DIR, project_name))


def _get_cart_path(project_name: str) -> str:
    """回傳購物車檔案的絕對路徑"""
    return os.path.join(_get_project_dir(project_name), "cart.json")


def _get_plan_path(project_name: str) -> str:
    """回傳採購計畫（計算結果）檔案的絕對路徑"""
    return os.path.join(_get_project_dir(project_name), "plan.json")


# ============================================================
# 購物車讀寫
# ============================================================

def get_cart(project_name: str) -> dict:
    """
    讀取指定專案的購物車內容。
    若購物車不存在，回傳預設的空白結構（不拋出例外）。

    Args:
        project_name: 專案名稱（即 data/ 下的資料夾名稱）
    Returns:
        購物車資料的 dict
    """
    path = _get_cart_path(project_name)

    if not os.path.exists(path):
        # deepcopy 確保每次回傳的是完全獨立的新物件
        # 若用 dict(_DEFAULT_CART)，巢狀的 global_settings 仍是同一個參考（淺拷貝 Bug）
        return copy.deepcopy(_DEFAULT_CART)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 確保 global_settings 欄位存在（向下兼容舊格式）
        if "global_settings" not in data:
            # deepcopy 確保補丁進去的是獨立的新物件
            data["global_settings"] = copy.deepcopy(_DEFAULT_CART["global_settings"])
        return data
    except (json.JSONDecodeError, IOError) as e:
        raise RuntimeError(f"讀取購物車 {path} 失敗: {e}") from e


def save_cart(project_name: str, cart_data: dict) -> None:
    """
    將購物車資料儲存至 JSON 檔案。

    Args:
        project_name: 專案名稱
        cart_data: 要儲存的購物車 dict
    Raises:
        RuntimeError: 寫入失敗時拋出
    """
    path = _get_cart_path(project_name)

    # 確保資料夾存在
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cart_data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        raise RuntimeError(f"儲存購物車 {path} 失敗: {e}") from e


# ============================================================
# 採購計畫結果讀取
# ============================================================

def get_plan(project_name: str) -> dict:
    """
    讀取計算完成的採購計畫（plan.json）。

    Args:
        project_name: 專案名稱
    Returns:
        採購計畫的 dict
    Raises:
        FileNotFoundError: 若 plan.json 尚未生成
        RuntimeError: 讀取失敗時
    """
    path = _get_plan_path(project_name)

    if not os.path.exists(path):
        raise FileNotFoundError(f"專案 '{project_name}' 的計算結果尚未產生")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise RuntimeError(f"讀取計算結果 {path} 失敗: {e}") from e


# ============================================================
# 專案列表查詢
# ============================================================

def list_projects() -> list[dict]:
    """
    掃描 data/ 目錄，回傳所有專案的預覽資訊。

    Returns:
        依建立時間降序排列的專案列表，每項包含 id, item_count, preview_names
    """
    projects = []

    if not os.path.exists(DATA_DIR):
        return projects

    for folder_name in os.listdir(DATA_DIR):
        project_path = os.path.join(DATA_DIR, folder_name)
        if not os.path.isdir(project_path):
            continue

        preview = {"id": folder_name, "item_count": 0, "preview_names": []}

        try:
            cart = get_cart(folder_name)
            items = cart.get("shopping_cart", [])
            preview["item_count"] = len(items)
            # 只取前 3 張卡的名稱作為預覽
            preview["preview_names"] = [
                item.get("card_name_zh", "未知卡片") for item in items[:3]
            ]
        except Exception:
            pass  # 讀取失敗就顯示空預覽，不影響其他專案

        projects.append(preview)

    # 依 ID（時間戳）降序排列，最新的排最前面
    projects.sort(key=lambda x: x["id"], reverse=True)
    return projects
