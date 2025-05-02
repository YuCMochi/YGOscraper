import subprocess
import json
import os
import sys
import glob
import asyncio
from datetime import datetime

# --- 設定路徑 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARD_SEARCHER_DIR = os.path.join(BASE_DIR, "card-searcher")
CART_FILE = os.path.join(CARD_SEARCHER_DIR, "cart.json")
SCRAPER_SCRIPT = os.path.join(BASE_DIR, "scraper.py")
CLEAN_SCRIPT = os.path.join(BASE_DIR, "clean_csv.py")
OPTIMIZER_SCRIPT = os.path.join(BASE_DIR, "card_optimizer.py")
PYTHON_EXECUTABLE = sys.executable # 使用當前的 Python 解釋器

# --- 輔助函數 ---
def run_script(script_path, args=[]):
    """執行指定的 Python 腳本並等待其完成"""
    command = [PYTHON_EXECUTABLE, script_path] + args
    print(f"\n[執行中] {' '.join(command)}")
    try:
        # 使用 run 而不是 call，以便更好地控制和獲取輸出（如果需要）
        result = subprocess.run(command, check=True, text=True, capture_output=True, cwd=BASE_DIR)
        print(f"[成功] {script_path} 執行完畢。")
        print("輸出:\n", result.stdout)
        if result.stderr:
            print("錯誤輸出:\n", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[錯誤] 執行 {script_path} 失敗。返回碼: {e.returncode}")
        print("錯誤訊息:\n", e.stderr)
        return False
    except FileNotFoundError:
        print(f"[錯誤] 找不到腳本: {script_path}")
        return False

async def run_scraper_async(card_name):
    """異步執行 scraper.py"""
    # 確保輸出檔名包含卡片名稱以便後續識別
    # 注意：scraper.py 預設檔名包含時間戳，這裡我們先遵循它
    # output_filename = f"ruten_{card_name}.csv" # 理想情況
    command = [PYTHON_EXECUTABLE, SCRAPER_SCRIPT, '-k', card_name]
    print(f"\n[執行中 (非同步)] {' '.join(command)}")
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=BASE_DIR
    )
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"[成功] {SCRAPER_SCRIPT} 為 '{card_name}' 執行完畢。")
        if stdout:
            print(f"輸出 ({card_name}):\n{stdout.decode()}")
        return True
    else:
        print(f"[錯誤] 執行 {SCRAPER_SCRIPT} 為 '{card_name}' 失敗。返回碼: {process.returncode}")
        if stderr:
            print(f"錯誤訊息 ({card_name}):\n{stderr.decode()}")
        return False

# --- 主流程 ---
async def main():
    print("=== 開始執行卡片比價流程 ===")

    # 1. 讀取購物車
    print(f"\n--- 步驟 1: 讀取購物車 ---")
    if not os.path.exists(CART_FILE):
        print(f"[錯誤] 找不到購物車檔案: {CART_FILE}")
        print("請先在 card-searcher 目錄下建立 cart.json 檔案。")
        return
    try:
        with open(CART_FILE, 'r', encoding='utf-8') as f:
            cart_data = json.load(f)
        if not cart_data:
            print("[錯誤] 購物車是空的。")
            return
        print(f"成功讀取購物車，共 {len(cart_data)} 種卡片。")
        print("購物車內容:", cart_data)
    except json.JSONDecodeError:
        print(f"[錯誤] 無法解析購物車檔案: {CART_FILE}。請檢查 JSON 格式。")
        return
    except Exception as e:
        print(f"[錯誤] 讀取購物車時發生錯誤: {e}")
        return

    # 2. 執行爬蟲 (並行)
    print(f"\n--- 步驟 2: 執行爬蟲 ---")
    tasks = [run_scraper_async(card_name) for card_name in cart_data.keys()]
    scraper_results = await asyncio.gather(*tasks) # Store results

    # Check if all scrapers succeeded before proceeding
    if not all(scraper_results):
        print("[錯誤] 部分爬蟲腳本執行失敗，流程中止。")
        return
    print("所有爬蟲任務執行完畢。")

    # 3. 執行清理 (針對每個爬蟲產生的檔案)
    print(f"\n--- 步驟 3: 清理數據 ---")
    all_cleaned_files = []
    cleaning_successful = True
    for card_name in cart_data.keys():
        # 尋找該卡片對應的原始 CSV 檔案 (假設檔名格式固定)
        # 注意：這裡假設 scraper.py 產生的檔案都在 BASE_DIR
        # 使用更精確的模式匹配，避免匹配到 _cleaned.csv
        raw_csv_pattern = os.path.join(BASE_DIR, f"ruten_{card_name}_????????_??????.csv")
        raw_csv_files = glob.glob(raw_csv_pattern)

        if not raw_csv_files:
            print(f"[警告] 找不到卡片 '{card_name}' 的原始 CSV 檔案 (模式: {os.path.basename(raw_csv_pattern)})。跳過清理。")
            # Consider if this should be a fatal error
            # cleaning_successful = False
            # break
            continue

        # 假設每個關鍵字只產生一個檔案，取最新的（如果有多個）
        # Sorting might be needed if multiple files can exist per keyword
        raw_csv_file = max(raw_csv_files, key=os.path.getctime) # Get the latest file if multiple match
        print(f"找到原始檔案: {os.path.basename(raw_csv_file)}，準備清理...")

        # 執行清理腳本，傳入檔案路徑和關鍵字
        if not run_script(CLEAN_SCRIPT, [raw_csv_file, card_name]):
            print(f"[錯誤] 清理卡片 '{card_name}' 的檔案 ({os.path.basename(raw_csv_file)}) 失敗。")
            cleaning_successful = False
            # Decide whether to stop immediately or continue cleaning others
            # break
        else:
            # clean_csv.py 應該會輸出清理後的檔名，我們在這裡驗證一下
            cleaned_file_expected = f"{os.path.splitext(raw_csv_file)[0]}_cleaned.csv"
            if os.path.exists(cleaned_file_expected):
                 print(f"成功清理檔案: {os.path.basename(cleaned_file_expected)}")
                 all_cleaned_files.append(cleaned_file_expected)
            else:
                 print(f"[警告] 清理腳本聲稱成功，但找不到預期的輸出檔案: {cleaned_file_expected}")
                 # Decide if this is critical
                 # cleaning_successful = False
                 # break

    if not cleaning_successful:
        print("[錯誤] 部分或全部數據清理失敗，流程中止。")
        return

    if not all_cleaned_files:
        print("[錯誤] 沒有成功清理任何數據檔案，無法進行優化。")
        return

    # 4. 執行優化
    # 這裡不再需要 glob 尋找 cleaned_files，因為 card_optimizer.py 會自己找
    print(f"\n--- 步驟 4: 計算最優組合 ---")
    # cleaned_files = glob.glob(os.path.join(BASE_DIR, "*_cleaned.csv")) # No longer needed here
    # if not cleaned_files:
    #     print("[錯誤] 找不到任何清理後的 CSV 檔案 (*_cleaned.csv)。") # Optimizer will handle this
    #     return

    # print(f"找到 {len(cleaned_files)} 個已清理的檔案:") # Optimizer will print found files
    # for f in cleaned_files:
    #     print(f"- {os.path.basename(f)}")

    # 將購物車數據轉換為 JSON 字串傳遞給優化器
    cart_json_string = json.dumps(cart_data)

    # 呼叫優化器腳本，傳遞購物車數據
    # card_optimizer.py 會自動尋找 *_cleaned.csv
    if not run_script(OPTIMIZER_SCRIPT, ['--cart-json', cart_json_string]):
         print("[錯誤] 優化腳本執行失敗。")
         return

    print("\n=== 流程執行完畢 ===")

if __name__ == "__main__":
    # 在 Windows 上設定異步事件循環策略以避免錯誤
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())