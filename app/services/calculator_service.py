"""
app/services/calculator_service.py - 最佳購買組合計算服務
==========================================================
從根目錄 caculator.py 重構而來，封裝為 PurchaseOptimizer 類別。
修正歷史拼字錯誤：caculator → calculator

功能：使用 PuLP（線性規劃）找出最省錢的購買方案。
目標函數：商品總價 + 運費 = 最小化
"""
import json
import os
import datetime
import logging

import pandas as pd
import pulp

# 設定日誌
logger = logging.getLogger(__name__)


class PurchaseOptimizer:
    """
    購買方案最佳化計算器。

    使用 PuLP 線性規劃求解器，在所有可能的購買組合中
    找到「商品總價 + 運費」最低的方案。

    使用方法：
        optimizer = PurchaseOptimizer()
        optimizer.optimize(
            cart_path="data/project/cart.json",
            input_csv="data/project/cleaned_ruten_data.csv",
            output_log="data/project/caculate.log",
            output_json="data/project/plan.json"
        )
    """

    def _load_shopping_cart(self, cart_path: str) -> tuple:
        """
        讀取購物車設定，了解使用者想買什麼。

        Args:
            cart_path: 購物車 JSON 檔案路徑

        Returns:
            tuple: (needed_cards, shipping_fee, min_purchase_limit)
                - needed_cards: {卡片名稱: 需要數量}
                - shipping_fee: 預設運費
                - min_purchase_limit: 賣家最低消費門檻
        """
        logger.info(f"正在讀取購物車設定: {cart_path}...")
        with open(cart_path, "r", encoding="utf-8") as f:
            cart_data = json.load(f)

        # 建立需求清單：{卡片名稱: 需要數量}
        needed_cards = {
            item["card_name_zh"]: item["required_amount"]
            for item in cart_data["shopping_cart"]
        }

        settings = cart_data.get("global_settings", {})
        cart_s = cart_data.get("cart_settings", {})

        # 兩層設定合併（v0.4.0）：cart_settings 有值就覆蓋 global_settings
        shipping_fee = cart_s.get("shipping_cost") if cart_s.get("shipping_cost") is not None else settings.get("default_shipping_cost", 60)
        min_purchase_limit = cart_s.get("min_purchase") if cart_s.get("min_purchase") is not None else settings.get("min_purchase_limit", 0)

        logger.info(f"預設運費: {shipping_fee} 元")
        if min_purchase_limit > 0:
            logger.info(f"賣家最低消費限制: {min_purchase_limit} 元")

        logger.info("本次購物清單:")
        for name, amount in needed_cards.items():
            logger.info(f"  - {name} (需 {amount} 張)")

        return needed_cards, shipping_fee, min_purchase_limit

    def _load_market_data(self, needed_cards: dict, market_data_path: str) -> list:
        """
        讀取清理後的市場資料 CSV。

        Args:
            needed_cards: 需求清單 {卡片名稱: 數量}
            market_data_path: 清理後的 CSV 路徑

        Returns:
            list: 有效商品的 dict 列表

        Raises:
            FileNotFoundError: 找不到市場資料檔案
            RuntimeError: 無有效商品可計算
        """
        logger.info(f"正在讀取市場行情資料: {market_data_path}...")

        if not os.path.exists(market_data_path):
            raise FileNotFoundError(f"找不到市場資料檔案: {market_data_path}")

        # 讀取 CSV，確保賣家 ID 是文字格式（避免變成科學記號）
        df = pd.read_csv(market_data_path, dtype={"seller_id": str})

        # 只保留我們需要的卡片資料
        market_data = df[df["search_card_name"].isin(needed_cards.keys())].copy()

        # 過濾掉庫存是 0 的無效商品
        original_count = len(market_data)
        market_data = market_data[market_data["stock_qty"] > 0]
        filtered_count = len(market_data)

        if original_count > filtered_count:
            logger.info(f"已過濾掉 {original_count - filtered_count} 筆無庫存商品。")

        # 幫每個商品加上唯一編號
        market_data["listing_id"] = market_data.index

        # 轉成字典列表格式
        card_listings = market_data.to_dict("records")

        logger.info(f"有效商品數量: {len(card_listings)} 筆。")

        if not card_listings:
            raise RuntimeError("市場資料中沒有任何有效商品，無法計算。")

        return card_listings

    def _solve(
        self,
        data: list,
        needed_cards: dict,
        shipping_fee: int,
        min_purchase_limit: int,
        log_path: str,
        output_json_path: str,
    ) -> dict:
        """
        核心演算法：使用 PuLP（線性規劃）找出最省錢的買法。

        Args:
            data: 有效商品列表
            needed_cards: 需求清單
            shipping_fee: 預設運費
            min_purchase_limit: 最低消費門檻
            log_path: 運算日誌輸出路徑
            output_json_path: 結果 JSON 輸出路徑

        Returns:
            dict: 最佳採購方案（包含 sellers 和 summary）

        Raises:
            RuntimeError: 計算失敗（庫存不足、條件太嚴苛等）
        """
        logger.info("正在計算最佳購買組合（啟動數學模型）...")

        # --- 1. 建立索引 ---
        num_listings = len(data)
        card_to_indices = {}
        seller_to_indices = {}

        for i, item in enumerate(data):
            c_name = item["search_card_name"]
            s_id = item["seller_id"]

            if c_name not in card_to_indices:
                card_to_indices[c_name] = []
            card_to_indices[c_name].append(i)

            if s_id not in seller_to_indices:
                seller_to_indices[s_id] = []
            seller_to_indices[s_id].append(i)

        sellers = list(seller_to_indices.keys())

        # --- 2. 預先檢查（防呆機制）---
        for card, required in needed_cards.items():
            indices = card_to_indices.get(card, [])
            total_stock = sum(data[i]["stock_qty"] for i in indices)
            if total_stock < required:
                raise RuntimeError(
                    f"卡片 '{card}' 市場總庫存 ({total_stock}) 不足，"
                    f"您需要 ({required}) 張。"
                )

        # --- 3. 設定數學題目（最小化問題）---
        prob = pulp.LpProblem("Card_Optimizer", pulp.LpMinimize)

        # use_seller[賣家ID]: 0=不跟這家買, 1=要跟這家買
        use_seller = pulp.LpVariable.dicts("UseSeller", sellers, cat="Binary")

        # buy_qty[商品ID]: 這個商品要買幾張？（整數，不能是負的）
        buy_qty = pulp.LpVariable.dicts(
            "BuyQty", range(num_listings), lowBound=0, cat="Integer"
        )

        # --- 4. 設定規則 (Constraints) ---

        # 規則 A: 每種卡片買到的數量必須等於需求量
        for card, required_amount in needed_cards.items():
            indices = card_to_indices[card]
            prob += (
                pulp.lpSum([buy_qty[i] for i in indices]) == required_amount,
                f"Fulfill_{card}",
            )

        # 規則 B: 庫存與運費連動
        for s_id in sellers:
            seller_indices = seller_to_indices[s_id]
            seller_var = use_seller[s_id]

            for i in seller_indices:
                stock = data[i]["stock_qty"]
                # 購買量 <= 庫存量 * 是否啟用該賣家
                prob += buy_qty[i] <= stock * seller_var, f"Link_Stock_Seller_{i}"

        # 規則 C: 最低消費
        if min_purchase_limit > 0:
            for s_id in sellers:
                seller_indices = seller_to_indices[s_id]
                seller_var = use_seller[s_id]
                seller_items_cost = pulp.lpSum(
                    [buy_qty[i] * data[i]["price"] for i in seller_indices]
                )
                prob += (
                    seller_items_cost >= min_purchase_limit * seller_var,
                    f"Min_Purchase_Limit_{s_id}",
                )

        # --- 5. 設定目標：商品總價 + 運費 → 最小化 ---
        items_cost = pulp.lpSum(
            [buy_qty[i] * data[i]["price"] for i in range(num_listings)]
        )
        shipping_total = pulp.lpSum([use_seller[s] * shipping_fee for s in sellers])
        prob += items_cost + shipping_total

        # --- 6. 開始求解 ---
        if not log_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = f"data/{timestamp}.log"

        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logger.info(f"正在記錄計算過程: {log_path}")
        prob.writeLP(log_path)

        # 呼叫求解器（時間限制 300 秒）
        solver = pulp.PULP_CBC_CMD(timeLimit=300, msg=1, gapRel=0.0)
        prob.solve(solver)

        # --- 7. 輸出結果 ---
        if pulp.LpStatus[prob.status] != "Optimal":
            raise RuntimeError(
                f"無法找到最佳解。狀態: {pulp.LpStatus[prob.status]}。"
                "可能原因：條件太嚴苛（例如低消太高、庫存不足），或是運算超時。"
            )

        total_price_with_shipping = pulp.value(prob.objective)
        logger.info(
            f"計算成功！最佳總金額（含運費）: ${int(total_price_with_shipping)}"
        )

        # 整理結果轉為 JSON
        final_json_output = {"sellers": {}, "summary": {}}

        temp_sellers = {}
        for i in range(num_listings):
            if buy_qty[i].varValue and buy_qty[i].varValue > 0:
                listing = data[i]
                quantity = int(buy_qty[i].varValue)
                seller_id = listing["seller_id"]

                if seller_id not in temp_sellers:
                    temp_sellers[seller_id] = []

                item_details = {
                    "buy_qty": quantity,
                    "search_card_name": listing.get("search_card_name"),
                    "product_id": listing.get("product_id"),
                    "product_name": listing.get("product_name"),
                    "seller_id": seller_id,
                    "price": listing.get("price"),
                    "shipping_cost": listing.get("shipping_cost", shipping_fee),
                    "post_time": listing.get("post_time"),
                    "image_url": listing.get("image_url"),
                }
                temp_sellers[seller_id].append(item_details)

        # 計算小計
        all_items_cost = 0
        sorted_seller_ids = sorted(temp_sellers.keys())

        for seller_id in sorted_seller_ids:
            items = temp_sellers[seller_id]
            seller_items_cost = sum(item["price"] * item["buy_qty"] for item in items)
            all_items_cost += seller_items_cost
            final_json_output["sellers"][seller_id] = {
                "items": items,
                "items_subtotal": int(seller_items_cost),
            }

        # 總結資訊
        num_sellers = len(temp_sellers)
        total_shipping_cost = num_sellers * shipping_fee
        final_json_output["summary"] = {
            "total_items_cost": int(all_items_cost),
            "total_shipping_cost": int(total_shipping_cost),
            "grand_total": int(all_items_cost + total_shipping_cost),
            "sellers_count": num_sellers,
        }

        # 寫入 JSON 檔案
        if not output_json_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_json_path = f"data/purchase_plan_{timestamp}.json"

        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(final_json_output, f, ensure_ascii=False, indent=4)

        logger.info(f"方案已儲存至: {output_json_path}")
        return final_json_output

    def optimize(
        self,
        cart_path: str,
        input_csv: str,
        output_log: str = None,
        output_json: str = None,
    ) -> dict:
        """
        執行完整的最佳化計算流程。

        依序執行：
        1. 讀取購物車需求
        2. 讀取市場資料
        3. 線性規劃求解

        Args:
            cart_path: 購物車 JSON 路徑
            input_csv: 清理後的市場資料 CSV 路徑
            output_log: 運算日誌輸出路徑（可選）
            output_json: 結果 JSON 輸出路徑（可選）

        Returns:
            dict: 最佳採購方案

        Raises:
            FileNotFoundError: 找不到輸入檔案
            RuntimeError: 計算過程中發生錯誤
        """
        # 載入資料
        needed_cards, shipping_fee, min_purchase_limit = self._load_shopping_cart(
            cart_path
        )
        market_data = self._load_market_data(needed_cards, input_csv)

        # 執行計算
        return self._solve(
            market_data,
            needed_cards,
            shipping_fee,
            min_purchase_limit,
            output_log,
            output_json,
        )
