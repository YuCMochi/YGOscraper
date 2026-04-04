import json
import os
import subprocess
import sys

import eel
from file_genarator import FileGenerator
from konami_scraper import KonamiScraper

# --- 初始化區段 ---

# 告訴 Eel 所有的網頁檔案（HTML, CSS, JS）都放在 'web' 資料夾中
eel.init('web')

# 初始化 Konami 爬蟲工具，用於抓取卡片詳細資訊
konami_scraper = KonamiScraper()

# --- Python 暴露給前端 (JavaScript) 呼叫的函式區段 ---

@eel.expose
def fetch_card_details(cid):
    """
    根據卡片 ID (CID) 從 Konami 官網抓取詳細資訊。
    這在前端搜尋卡片並決定要加入哪些卡號時非常有用。
    """
    try:
        print(f"正在抓取 CID 的詳細資料: {cid}")
        # scrape_cids 會回傳一個字典，格式為 {cid: [版本列表]}
        data = konami_scraper.scrape_cids([str(cid)])
        if data and str(cid) in data:
            return data[str(cid)]
        return []
    except Exception as e:
        print(f"抓取卡片詳情時發生錯誤: {e}")
        return []

@eel.expose
def get_project_list():
    """
    掃描 'data' 資料夾，回傳所有已存在的專案名稱列表（資料夾名稱）。
    用於前端的專案載入下拉選單。
    """
    if not os.path.exists("data"):
        return []
    # 取得 data 目錄下所有的子資料夾名稱
    projects = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
    # 依照名稱排序（通常是時間戳記，由新到舊）
    projects.sort(reverse=True)
    return projects

@eel.expose
def create_new_project():
    """
    建立一個全新的專案環境（包含自動生成的資料夾與初始的 cart.json）。
    回傳新專案的完整路徑。
    """
    try:
        fg = FileGenerator()
        new_path = fg.create_project_environment()
        return new_path
    except Exception as e:
        print(f"建立專案時發生錯誤: {e}")
        return None

@eel.expose
def load_project(project_name):
    """
    根據專案名稱回傳其在電腦中的完整絕對路徑。
    """
    path = os.path.abspath(os.path.join("data", project_name))
    if os.path.exists(path):
        return path
    return None

@eel.expose
def read_cart_json(project_path):
    """
    讀取指定專案路徑下的 cart.json（購物車設定檔）。
    如果檔案不存在，則回傳預設的空白結構。
    """
    cart_path = os.path.join(project_path, "cart.json")
    if os.path.exists(cart_path):
        try:
            with open(cart_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            # 讀取失敗時回傳錯誤訊息與基本結構
            return {"error": str(e), "shopping_cart": [], "global_settings": {}}
    return {"shopping_cart": [], "global_settings": {}}

@eel.expose
def save_cart_json(project_path, cart_data):
    """
    將前端編輯好的購物車資料儲存回專案資料夾中的 cart.json。
    """
    cart_path = os.path.join(project_path, "cart.json")
    try:
        with open(cart_path, 'w', encoding='utf-8') as f:
            # indent=4 讓產出的 JSON 檔案易於人類閱讀，ensure_ascii=False 確保中文顯示正常
            json.dump(cart_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"儲存購物車時發生錯誤: {e}")
        return False

@eel.expose
def run_full_process(project_path):
    """
    核心功能：依照順序執行「爬蟲 -> 清理 -> 計算」完整流程。
    這是一個長時運作的函式，會將進度即時回傳給前端。
    """
    
    # 內部輔助函式：同時在 Python 終端機與前端網頁顯示 Log
    def log(msg):
        print(msg)
        eel.appendLog(msg) # 呼叫前端 JS 註冊的 appendLog 函式

    # 定義各個步驟所需的檔案路徑
    cart_path = os.path.join(project_path, "cart.json")
    csv_path = os.path.join(project_path, "ruten_data.csv")
    clean_csv_path = os.path.join(project_path, "cleaned_ruten_data.csv")
    log_path = os.path.join(project_path, "caculate.log")
    plan_path = os.path.join(project_path, "plan.json")

    # 定義要依序執行的外部 Python 指令
    commands = [
        (
            [sys.executable, "scraper.py", "--cart", cart_path, "--output", csv_path],
            "正在執行: 爬蟲模組 (從露天抓取商品資料)..."
        ),
        (
            [sys.executable, "clean_csv.py", "--input", csv_path, "--output", clean_csv_path, "--cart", cart_path],
            "正在執行: 資料清理 (排除黑名單與無效商品)..."
        ),
        (
            [sys.executable, "caculator.py", "--cart", cart_path, "--input_csv", clean_csv_path, "--output_log", log_path, "--output_json", plan_path],
            "正在執行: 最佳化計算 (尋找最便宜組合)..."
        )
    ]

    for cmd, desc in commands:
        log(f"--- {desc} ---")
        try:
            # 啟動子程序執行腳本
            process = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 實時讀取腳本輸出的每一行文字，並推送到網頁畫面上
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    log(output.strip())
            
            # 檢查執行結果狀態碼
            rc = process.poll()
            if rc != 0:
                err = process.stderr.read()
                log(f"錯誤詳情: {err}")
                log("流程因錯誤而終止。")
                return False
                
        except Exception as e:
            log(f"執行發生例外狀況: {e}")
            return False
            
    log("✅ 所有步驟執行完成！請查看「計算結果」分頁。")
    return True

@eel.expose
def get_results(project_path):
    """
    讀取計算完成後的產出檔案 plan.json，並傳回給前端顯示結果。
    """
    plan_path = os.path.join(project_path, "plan.json")
    if os.path.exists(plan_path):
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"error": "JSON 格式無效"}
    return {"error": "找不到結果檔案"}

# --- 程式進入點 ---

if __name__ == '__main__':
    try:
        # 啟動 Eel 應用程式，開啟 index.html 視窗，並設定預設大小
        print("系統啟動中...")
        eel.start('index.html', size=(1200, 800))
    except (SystemExit, MemoryError, KeyboardInterrupt):
        # 處理正常關閉或使用者中斷的情況
        print("系統已關閉。")
        pass