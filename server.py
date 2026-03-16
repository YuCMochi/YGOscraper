from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import sys
import subprocess
import asyncio
import sqlite3
import urllib.request
from contextlib import asynccontextmanager
from file_genarator import FileGenerator
from konami_scraper import KonamiScraper

_PASSCODE_TO_CID_MAP = {}
_LOCAL_CARD_DB = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _LOCAL_CARD_DB, _PASSCODE_TO_CID_MAP
    
    print("載入外部卡片資料庫 (cid_table.json) 到記憶體...")
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/salix5/heliosphere/master/data/cid_table.json", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            cid_data = json.loads(response.read().decode('utf-8'))
            for cid_str, passcode_val in cid_data.items():
                _PASSCODE_TO_CID_MAP[str(passcode_val)] = cid_str
        print(f"成功載入 {len(_PASSCODE_TO_CID_MAP)} 筆 CID 對應資料。")
    except Exception as e:
        print(f"載入 CID 對應資料失敗: {e}")

    print("載入外部卡片資料庫 (cards.cdb) 到記憶體...")
    try:
        req = urllib.request.Request("https://raw.githubusercontent.com/salix5/cdb/gh-pages/cards.cdb", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            db_data = response.read()
            
        with open('/tmp/temp_cards.cdb', 'wb') as f:
            f.write(db_data)
            
        source_db = sqlite3.connect('/tmp/temp_cards.cdb')
        # check_same_thread=False is important for FastAPI async endpoints
        _LOCAL_CARD_DB = sqlite3.connect(':memory:', check_same_thread=False)
        source_db.backup(_LOCAL_CARD_DB)
        source_db.close()
        os.remove('/tmp/temp_cards.cdb')
        print("成功載入 cards.cdb 到記憶體。")
    except Exception as e:
        print(f"載入 cards.cdb 失敗: {e}")
        
    yield
    
    if _LOCAL_CARD_DB:
        _LOCAL_CARD_DB.close()

app = FastAPI(title="YGOscraper API", version="2.0.0", lifespan=lifespan)

__version__ = "2.0.0"

# --- Configuration ---
# Allow requests from React dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize utilities
konami_scraper = KonamiScraper()
file_gen = FileGenerator()

# --- Models ---
class ProjectCreate(BaseModel):
    pass # No fields needed for creation currently

class CartItem(BaseModel):
    card_name_zh: str
    target_card_numbers: List[str]
    required_amount: int
    ui_inputVisible: Optional[bool] = False
    ui_inputValue: Optional[str] = ""

class GlobalSettings(BaseModel):
    default_shipping_cost: int
    min_purchase_limit: int
    global_exclude_keywords: List[str]
    global_exclude_seller: List[str]

class CartData(BaseModel):
    shopping_cart: List[CartItem]
    global_settings: GlobalSettings

# --- API Endpoints ---

@app.get("/api/projects")
async def get_project_list():
    """List all existing projects with preview info."""
    projects_info = []
    if os.path.exists("data"):
        for d in os.listdir("data"):
            project_path = os.path.join("data", d)
            if os.path.isdir(project_path):
                cart_path = os.path.join(project_path, "cart.json")
                preview = {"id": d, "item_count": 0, "preview_names": []}
                
                # Try to read cart.json for preview info
                if os.path.exists(cart_path):
                    try:
                        with open(cart_path, 'r', encoding='utf-8') as f:
                            cart_data = json.load(f)
                            items = cart_data.get('shopping_cart', [])
                            preview['item_count'] = len(items)
                            # Get up to 3 card names for preview
                            preview['preview_names'] = [item.get('card_name_zh', '未知卡片') for item in items[:3]]
                    except Exception:
                        pass # Ignore parsing errors for preview
                
                projects_info.append(preview)
    
    # Sort by project ID (timestamp) descending
    projects_info.sort(key=lambda x: x["id"], reverse=True)
    return projects_info

@app.post("/api/projects")
async def create_project():
    """Create a new project."""
    try:
        new_path = file_gen.create_project_environment()
        return {"path": new_path, "name": os.path.basename(new_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_name}/cart")
async def get_cart(project_name: str):
    """Get cart.json for a specific project."""
    path = os.path.abspath(os.path.join("data", project_name, "cart.json"))
    if not os.path.exists(path):
        # Return default empty cart structure
        return {"shopping_cart": [], "global_settings": {
            "default_shipping_cost": 60,
            "min_purchase_limit": 0,
            "global_exclude_keywords": [],
            "global_exclude_seller": []
        }}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading cart: {str(e)}")

@app.post("/api/projects/{project_name}/cart")
async def save_cart(project_name: str, cart_data: CartData):
    """Save cart.json."""
    path = os.path.abspath(os.path.join("data", project_name, "cart.json"))
    try:
        # Convert Pydantic model to dict
        data_dict = cart_data.model_dump()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=4)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving cart: {str(e)}")



@app.post("/api/projects/{project_name}/run")
async def run_process(project_name: str):
    """Run the full scraper -> cleaner -> calculator process."""
    project_path = os.path.abspath(os.path.join("data", project_name))
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")

    cart_path = os.path.join(project_path, "cart.json")
    csv_path = os.path.join(project_path, "ruten_data.csv")
    clean_csv_path = os.path.join(project_path, "cleaned_ruten_data.csv")
    log_path = os.path.join(project_path, "caculate.log")
    plan_path = os.path.join(project_path, "plan.json")

    # Define commands
    commands = [
        ([sys.executable, "scraper.py", "--cart", cart_path, "--output", csv_path], "Scraper"),
        ([sys.executable, "clean_csv.py", "--input", csv_path, "--output", clean_csv_path, "--cart", cart_path], "Cleaner"),
        ([sys.executable, "caculator.py", "--cart", cart_path, "--input_csv", clean_csv_path, "--output_log", log_path, "--output_json", plan_path], "Calculator")
    ]

    # We will use a streaming response or just return immediate status and let client poll?
    # For simplicity, we'll execute synchronously for now, or use background tasks.
    # Given the previous app used 'eel' with log updates, streaming logs would be ideal.
    # But for MVP Refactor, let's just run it and return success/fail. Log file is available.
    
    # Using specific python executable from env if possible, or sys.executable
    python_exec = sys.executable 

    try:
        for cmd, name in commands:
            print(f"Running {name}...")
            # We want to capture output to log file or print
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{name} failed: {result.stderr}")
                raise HTTPException(status_code=500, detail=f"{name} failed: {result.stderr}")
            print(f"{name} completed.")
        
        return {"status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_name}/results")
async def get_results(project_name: str):
    """Get plan.json results."""
    path = os.path.abspath(os.path.join("data", project_name, "plan.json"))
    if not os.path.exists(path):
         raise HTTPException(status_code=404, detail="Results not found")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading results: {str(e)}")

@app.get("/api/cards/search")
async def search_cards(q: str):
    """
    使用本地揮發性記憶體中的 SQLite (cards.cdb) 進行關鍵字搜尋卡片
    返回卡名、卡圖 URL、Passcode、CID
    """
    if not q or not _LOCAL_CARD_DB:
        return []
    
    try:
        cursor = _LOCAL_CARD_DB.cursor()
        # 查詢符合條件的卡片。限制回傳數量例如前 50 筆
        cursor.execute("""
            SELECT t.id, t.name, d.type, d.atk, d.def, d.level, d.race, d.attribute, t.desc 
            FROM texts t 
            JOIN datas d ON t.id = d.id 
            WHERE t.name LIKE ? LIMIT 50
        """, (f"%{q}%",))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            pwd, name, c_type, atk, c_def, level, race, attr, desc = row
            passcode_str = str(pwd)
            cid = _PASSCODE_TO_CID_MAP.get(passcode_str)
            # 建立回傳資料結構，附加卡圖網址與 CID 以及屬性
            results.append({
                "passcode": passcode_str,
                "name": name,
                "cid": cid,
                "type": c_type,
                "atk": atk,
                "def": c_def,
                "level": level,
                "race": race,
                "attribute": attr,
                "desc": desc,
                "image_url": f"https://raw.githubusercontent.com/salix5/query-data/gh-pages/pics/{passcode_str}.jpg"
            })
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cards/cid/{cid}/card-numbers")
async def get_card_numbers_by_cid(cid: int):
    """
    根據 CID（Konami 資料庫 ID）爬取該卡片的所有卡號。
    例如 CID=4007 → 卡號 ['DABL-JP035', 'SD43-JP001', ...]
    """
    try:
        print(f"正在爬取 CID {cid} 的卡號...")
        data = konami_scraper.scrape_cids([str(cid)])
        card_numbers = []
        if data and str(cid) in data:
            # 從版本資料中提取完整資訊（保留稀有度等）
            versions = data[str(cid)]
            for v in versions:
                if v.get('card_number'):
                    card_numbers.append({
                        "card_number": v['card_number'],
                        "rarity_name": v.get('rarity_name', ''),
                        "pack_name": v.get('pack_name', '')
                    })
        print(f"CID {cid} 的卡號版本: {len(card_numbers)} 個")
        return {"cid": cid, "card_numbers": card_numbers}
    except Exception as e:
        print(f"爬取 CID {cid} 卡號時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"爬取卡號失敗: {str(e)}")

# get_card_numbers_by_name 已廢棄，因為透過記憶體資料庫搜尋出來的卡片已經附帶 CID 
# 前端加入購物車時可直接呼叫 /api/cards/cid/{cid}/card-numbers

DATA_DIR = "data"

if __name__ == "__main__":
    import uvicorn
    # 確保資料目錄存在
    os.makedirs(DATA_DIR, exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)

