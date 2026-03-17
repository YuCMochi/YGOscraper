"""
app/routers/tasks.py - 爬蟲執行與結果讀取的 API 路由
======================================================
負責啟動完整的採購流程（爬蟲→清洗→計算），以及讀取計算結果：
- POST /api/projects/{project_name}/run     : 依序執行三個腳本
- GET  /api/projects/{project_name}/results : 讀取 plan.json 計算結果

注意：目前仍使用 subprocess 呼叫腳本。
Phase 2（腳本模組化）完成後，將改為直接呼叫 Service 類別。
"""
import os
import sys
import subprocess

from fastapi import APIRouter, HTTPException
from app.services import storage

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/projects/{project_name}/run")
async def run_process(project_name: str):
    """
    啟動完整的採購流程，依序執行：
    1. scraper.py   → 爬取露天拍賣的商品資料
    2. clean_csv.py → 過濾不符合條件的商品
    3. caculator.py → 用線性規劃找出最省錢的購買組合
    
    全部成功後回傳 {"status": "completed"}。
    若其中任一步驟失敗，回傳 500 並說明哪個步驟出錯。
    """
    project_path = os.path.abspath(os.path.join("data", project_name))
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="找不到此專案")

    # 各步驟用到的檔案路徑
    cart_path = os.path.join(project_path, "cart.json")
    csv_path = os.path.join(project_path, "ruten_data.csv")
    clean_csv_path = os.path.join(project_path, "cleaned_ruten_data.csv")
    log_path = os.path.join(project_path, "caculate.log")
    plan_path = os.path.join(project_path, "plan.json")

    # 定義要依序執行的命令（[(命令列表, 步驟名稱), ...]）
    commands = [
        (
            [sys.executable, "scraper.py", "--cart", cart_path, "--output", csv_path],
            "Scraper（露天爬蟲）",
        ),
        (
            [sys.executable, "clean_csv.py", "--input", csv_path, "--output", clean_csv_path, "--cart", cart_path],
            "Cleaner（資料清洗）",
        ),
        (
            [sys.executable, "caculator.py", "--cart", cart_path, "--input_csv", clean_csv_path, "--output_log", log_path, "--output_json", plan_path],
            "Calculator（最佳組合計算）",
        ),
    ]

    try:
        for cmd, name in commands:
            print(f"正在執行 {name}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{name} 失敗：{result.stderr}")
                raise HTTPException(
                    status_code=500,
                    detail=f"{name} 執行失敗：{result.stderr}",
                )
            print(f"{name} 完成。")

        return {"status": "completed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_name}/results")
async def get_results(project_name: str):
    """
    讀取計算完成的最佳採購方案（plan.json）。
    若結果檔案不存在（尚未執行爬蟲/計算），回傳 404。
    """
    try:
        return storage.get_plan(project_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
