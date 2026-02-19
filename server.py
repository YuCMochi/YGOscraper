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
from file_genarator import FileGenerator
from konami_scraper import KonamiScraper

app = FastAPI(title="YGOscraper API", version="2.0.0")

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
    """List all existing projects."""
    if not os.path.exists("data"):
        return []
    projects = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
    projects.sort(reverse=True)
    return projects

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
    使用關鍵字搜尋卡片（Konami 官網）
    """
    if not q:
        return []
    
    try:
        scraper = KonamiScraper()
        results = scraper.search_by_keyword(q)
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
            # 從版本資料中提取卡號字串（scrape_cids 回傳 dict list）
            versions = data[str(cid)]
            card_numbers = [v['card_number'] for v in versions if v.get('card_number')]
        print(f"CID {cid} 的卡號: {card_numbers}")
        return {"cid": cid, "card_numbers": card_numbers}
    except Exception as e:
        print(f"爬取 CID {cid} 卡號時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"爬取卡號失敗: {str(e)}")

@app.get("/api/cards/name/{card_name}/card-numbers")
async def get_card_numbers_by_name(card_name: str):
    """
    根據卡片名稱（中文/日文）查找 CID，再爬取所有印刷卡號。
    
    因為 Konami DB 只有日文卡名，中文卡名無法直接搜尋。
    本端點會嘗試多種策略找到對應的日文卡片。
    """
    import unicodedata
    
    try:
        print(f"\n=== 搜尋卡片: {card_name} ===")
        
        # 策略 1：直接用傳入的卡名搜尋（日文名會直接匹配）
        search_results = konami_scraper.search_by_keyword(card_name)
        
        # 策略 2：如果沒結果，提取漢字（CJK 統一漢字）部分再搜尋
        # 例如「青眼雙爆裂龍」→ 提取「青眼雙爆裂龍」→ 逐步縮短為「青眼」
        if not search_results:
            # 提取所有漢字字元（共同用於中文和日文的部分）
            kanji_chars = ''.join(
                c for c in card_name 
                if '\u4e00' <= c <= '\u9fff'  # CJK 統一漢字
            )
            
            if kanji_chars:
                # 如果漢字部分與原始卡名不同（有非漢字字元被過濾），先用純漢字搜一次
                if kanji_chars != card_name:
                    print(f"完整名稱搜尋無結果，嘗試漢字部分: {kanji_chars}")
                    search_results = konami_scraper.search_by_keyword(kanji_chars)
                
                # 如果仍然沒結果，逐步縮短漢字進行搜尋
                if not search_results and len(kanji_chars) > 2:
                    # 嘗試前 2-4 個漢字（日文卡名中通常前幾個漢字是關鍵部分）
                    for length in [min(4, len(kanji_chars)), min(3, len(kanji_chars)), 2]:
                        partial = kanji_chars[:length]
                        if partial == kanji_chars:
                            continue  # 跳過與已嘗試相同的字串
                        print(f"嘗試部分漢字: {partial}")
                        search_results = konami_scraper.search_by_keyword(partial)
                        if search_results:
                            break
        
        if not search_results:
            print(f"所有搜尋策略均無結果: {card_name}")
            return {"card_name": card_name, "cid": None, "card_numbers": []}
        
        # 從搜尋結果中找最佳匹配
        # 優先選擇名稱中包含最多原始卡名漢字的結果
        best_match = search_results[0]
        kanji_in_name = ''.join(c for c in card_name if '\u4e00' <= c <= '\u9fff')
        
        if len(search_results) > 1 and kanji_in_name:
            # 計算每個結果與原始卡名的漢字匹配度
            def match_score(result_name):
                score = 0
                for c in kanji_in_name:
                    if c in result_name:
                        score += 1
                return score
            
            scored = [(match_score(r['name']), r) for r in search_results]
            scored.sort(key=lambda x: -x[0])
            best_match = scored[0][1]
            print(f"最佳匹配（漢字匹配度）: {best_match['name']} (分數: {scored[0][0]})")
        
        cid = best_match['cid']
        matched_name = best_match['name']
        print(f"找到匹配: {matched_name} (CID: {cid})")
        
        # 用 CID 爬取卡號
        data = konami_scraper.scrape_cids([cid])
        card_numbers = []
        if data and cid in data:
            versions = data[cid]
            card_numbers = [v['card_number'] for v in versions if v.get('card_number')]
            # 去重（同一個卡號可能有不同稀有度）
            card_numbers = list(dict.fromkeys(card_numbers))
        
        print(f"CID {cid} 找到 {len(card_numbers)} 個不重複卡號")
        if card_numbers[:5]:
            print(f"  前 5 個: {card_numbers[:5]}")
        
        return {
            "card_name": card_name,
            "matched_name": matched_name,
            "cid": cid,
            "card_numbers": card_numbers
        }
    except Exception as e:
        print(f"查找卡片 '{card_name}' 的卡號時發生錯誤: {e}")
        raise HTTPException(status_code=500, detail=f"爬取卡號失敗: {str(e)}")

DATA_DIR = "data"

if __name__ == "__main__":
    import uvicorn
    # 確保資料目錄存在
    os.makedirs(DATA_DIR, exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)

