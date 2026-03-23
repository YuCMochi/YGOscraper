"""
app/routers/tasks.py - 爬蟲執行與結果讀取的 API 路由
======================================================
負責啟動完整的採購流程（爬蟲→清洗→計算），以及讀取計算結果：
- POST /api/projects/{project_name}/run     : 依序執行三個步驟
- GET  /api/projects/{project_name}/results : 讀取 plan.json 計算結果

已改為直接 import Service 類別，不再使用 subprocess。
"""
import os
import logging

from fastapi import APIRouter, HTTPException
from app.services import storage
from app.services.ruten_scraper import RutenScraper
from app.services.cleaner_service import DataCleaner
from app.services.calculator_service import PurchaseOptimizer

# 設定日誌
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post("/projects/{project_name}/run")
async def run_process(project_name: str):
    """
    啟動完整的採購流程，依序執行：
    1. RutenScraper   → 爬取露天拍賣的商品資料
    2. DataCleaner    → 過濾不符合條件的商品
    3. PurchaseOptimizer → 用線性規劃找出最省錢的購買組合

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

    # ============================================================
    # 步驟 1：露天爬蟲（非同步）
    # ============================================================
    try:
        logger.info("步驟 1/3：正在執行露天爬蟲...")
        scraper = RutenScraper()
        await scraper.run(cart_path, csv_path)
        logger.info("步驟 1/3：露天爬蟲完成。")
    except Exception as e:
        logger.error(f"露天爬蟲失敗：{e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraper（露天爬蟲）執行失敗：{str(e)}",
        )

    # ============================================================
    # 步驟 2：資料清洗
    # ============================================================
    try:
        logger.info("步驟 2/3：正在執行資料清洗...")
        cleaner = DataCleaner()
        cleaner.clean(csv_path, clean_csv_path, cart_path)
        logger.info("步驟 2/3：資料清洗完成。")
    except Exception as e:
        logger.error(f"資料清洗失敗：{e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cleaner（資料清洗）執行失敗：{str(e)}",
        )

    # ============================================================
    # 步驟 3：最佳組合計算
    # ============================================================
    try:
        logger.info("步驟 3/3：正在執行最佳組合計算...")
        optimizer = PurchaseOptimizer()
        optimizer.optimize(cart_path, clean_csv_path, log_path, plan_path)
        logger.info("步驟 3/3：最佳組合計算完成。")
    except Exception as e:
        logger.error(f"最佳組合計算失敗：{e}")
        raise HTTPException(
            status_code=500,
            detail=f"Calculator（最佳組合計算）執行失敗：{str(e)}",
        )

    return {"status": "completed"}


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
