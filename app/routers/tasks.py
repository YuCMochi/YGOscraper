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
    讀取計算完成的最佳採購方案（plan.json），並將資料格式轉換為前端期望的結構。

    plan.json 原始格式（calculator_service 輸出）：
        { "sellers": { "賣家ID": { "items": [...], "items_subtotal": N } },
          "summary": { "total_items_cost", "total_shipping_cost", "grand_total", "sellers_count" } }

    轉換後回傳給前端的格式：
        { "total_cost": N, "total_item_cost": N, "total_shipping_cost": N,
          "plan": [{ "seller": "ID", "subtotal": N, "shipping_cost": N,
                     "items": [{ "name", "url", "card_name_zh", "price", "buy_count", "card_number" }] }] }

    若結果檔案不存在（尚未執行爬蟲/計算），回傳 404。
    """
    try:
        raw = storage.get_plan(project_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # --- 格式轉換：將後端結構轉為前端 ResultsPage.jsx 期望的格式 ---
    summary = raw.get("summary", {})
    sellers = raw.get("sellers", {})

    # 讀取購物車，取得有效運費（cart_settings 覆蓋 > global_settings > 60）
    try:
        cart_data = storage.get_cart(project_name)
        cart_s = cart_data.get("cart_settings", {})
        global_s = cart_data.get("global_settings", {})
        default_shipping = (
            cart_s.get("shipping_cost")
            if cart_s.get("shipping_cost") is not None
            else global_s.get("default_shipping_cost", 60)
        )
    except Exception:
        default_shipping = 60

    # 組裝賣家陣列（前端的 plan[]）
    plan = []
    for seller_id, seller_data in sellers.items():
        # 轉換每個商品的欄位名稱
        items = []
        for item in seller_data.get("items", []):
            product_id = item.get("product_id")
            items.append({
                "name": item.get("product_name", ""),
                # 用 product_id 組合露天商品頁面網址
                "url": (
                    f"https://www.ruten.com.tw/item/show?{product_id}"
                    if product_id
                    else ""
                ),
                "card_name_zh": item.get("search_card_name", ""),
                "price": item.get("price", 0),
                "buy_count": item.get("buy_qty", 0),
                "card_number": "",  # plan.json 目前不含卡號資訊
                "image_url": item.get("image_url", ""),
            })

        # 取第一個商品的 shipping_cost 作為該賣家的運費，若無則用預設值
        seller_shipping = (
            seller_data["items"][0].get("shipping_cost", default_shipping)
            if seller_data.get("items")
            else default_shipping
        )

        plan.append({
            "seller": seller_id,
            "subtotal": seller_data.get("items_subtotal", 0),
            "shipping_cost": seller_shipping,
            "items": items,
        })

    return {
        "total_cost": summary.get("grand_total", 0),
        "total_item_cost": summary.get("total_items_cost", 0),
        "total_shipping_cost": summary.get("total_shipping_cost", 0),
        "plan": plan,
    }
