"""
app/services/cleaner_service.py - 爬蟲資料清洗服務
===================================================
從根目錄 clean_csv.py 重構而來，封裝為 DataCleaner 類別。

功能：清理露天拍賣爬蟲抓下來的原始 CSV 資料，過濾掉不符合條件的商品。

過濾規則（依序）：
0. 去重複（根據 product_id）
1. 黑名單賣家
2. 價格異常（超過 5000 元）
3. 有價差的商品（多種規格）
4. eBay 相關商品
5. 排除關鍵字（卡套、桌墊等）
6. 確保商品名稱包含目標卡號（Regex 精確匹配）
"""
import csv
import json
import os
import re
import logging

# 設定日誌
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    爬蟲資料清洗服務。

    使用方法：
        cleaner = DataCleaner()
        cleaner.clean(
            input_csv="data/project/ruten_data.csv",
            output_csv="data/project/cleaned_ruten_data.csv",
            cart_path="data/project/cart.json"
        )
    """

    def _check_card_code_match(self, target_code: str, text: str) -> bool:
        """
        使用 Regex 檢查卡號是否精確匹配，避免子字串誤判。

        例如：避免 "SD5" 匹配到 "YSD5"。

        規則：
        1. (?<![a-zA-Z]) : 前面不能是英文字母
        2. (?![0-9]) : 後面不能是數字

        Args:
            target_code: 目標卡號（例如 "DABL-JP035"）
            text: 要檢查的商品名稱

        Returns:
            bool: 是否精確匹配
        """
        pattern = r"(?<![a-zA-Z])" + re.escape(target_code) + r"(?![0-9])"
        return re.search(pattern, text, re.IGNORECASE) is not None

    def clean(self, input_csv: str, output_csv: str, cart_path: str) -> None:
        """
        清理爬蟲抓下來的原始 CSV 資料。

        Args:
            input_csv: 原始 CSV 檔案路徑
            output_csv: 清理後的 CSV 輸出路徑
            cart_path: 購物車設定檔路徑（用來讀取黑名單與目標卡號）

        Raises:
            FileNotFoundError: 找不到輸入檔案或設定檔
            RuntimeError: 處理過程中發生錯誤
        """
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        logger.info(f"正在處理檔案: {input_csv}")

        # ============================================================
        # 1. 讀取設定（黑名單與目標卡號）
        # ============================================================
        try:
            with open(cart_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到設定檔: {cart_path}")
        except json.JSONDecodeError:
            raise RuntimeError(f"設定檔格式不正確: {cart_path}")

        global_settings = config.get("global_settings", {})
        cart_settings = config.get("cart_settings", {})

        # 兩層設定合併（v0.4.0 方案 A）：
        # - 列表型：全域 + 專案 聯集
        # - 數值型：專案有值就覆蓋，None 就用全域
        exclude_keywords = list(set(
            global_settings.get("global_exclude_keywords", []) +
            cart_settings.get("exclude_keywords", [])
        ))
        logger.info(f"排除關鍵字（合併後）: {exclude_keywords}")

        exclude_sellers = list(set(
            global_settings.get("global_exclude_seller", []) +
            cart_settings.get("exclude_seller", [])
        ))
        if exclude_sellers:
            logger.info(f"排除賣家 ID（合併後）: {exclude_sellers}")

        # 建立卡片名稱 → 目標卡號的對應字典（用來做精確過濾）
        card_target_map = {}
        all_target_card_numbers = []

        for item in config.get("shopping_cart", []):
            c_name = item.get("card_name_zh")
            raw_ids = item.get("target_card_numbers", [])
            # target_card_numbers 可能是純字串或字典格式，統一轉為字串列表
            t_ids = []
            for tid in raw_ids:
                if isinstance(tid, dict):
                    cn = tid.get("card_number", "")
                    if cn:
                        t_ids.append(cn)
                elif isinstance(tid, str) and tid:
                    t_ids.append(tid)
            if c_name:
                card_target_map[c_name] = t_ids
            all_target_card_numbers.extend(t_ids)

        if not all_target_card_numbers:
            logger.warning("設定檔中沒有任何目標卡號 (target_card_numbers)。")
        else:
            logger.info(
                f"已載入 {len(all_target_card_numbers)} 個目標卡號，"
                f"涵蓋 {len(card_target_map)} 種卡片。"
            )

        # ============================================================
        # 2. 開始過濾資料
        # ============================================================
        cleaned_rows = []
        seller_excluded_count = 0
        seen_product_ids = set()  # 防止重複

        try:
            # 使用 utf-8-sig 以處理可能的 BOM (Byte Order Mark)
            with open(input_csv, "r", encoding="utf-8-sig") as infile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames

                for row in reader:
                    # 過濾 0: 去重複（根據 product_id）
                    p_id = row.get("product_id")
                    if p_id and p_id in seen_product_ids:
                        continue

                    # 過濾 1: 黑名單賣家
                    if row.get("seller_id") in exclude_sellers:
                        seller_excluded_count += 1
                        continue

                    # 過濾 2: 價格異常（超過 5000 可能是假貨或整盒賣）
                    try:
                        price = float(row.get("price", 0))
                        if price > 5000:
                            continue
                    except (ValueError, TypeError):
                        pass  # 價格不是數字就保留

                    # 過濾 3: 有價差的商品（多種規格，爬蟲無法確定是哪種）
                    if row.get("alt_price") == "1":
                        continue

                    product_name = row.get("product_name", "")
                    search_card_name = row.get("search_card_name", "")

                    # 過濾 4: 排除 eBay 相關商品（運費高且久）
                    if "ebay" in product_name.lower():
                        continue
                    image_url = row.get("image_url", "")
                    if "ebay" in image_url.lower():
                        continue

                    # 過濾 5: 排除關鍵字（卡套、桌墊等）
                    if any(keyword in product_name for keyword in exclude_keywords):
                        continue

                    # 過濾 6: 確保商品名稱包含目標卡號（Regex 精確匹配）
                    if search_card_name in card_target_map:
                        specific_targets = card_target_map[search_card_name]
                        if specific_targets and not any(
                            self._check_card_code_match(target_id, product_name)
                            for target_id in specific_targets
                        ):
                            continue
                    else:
                        # 退回使用全域檢查
                        if all_target_card_numbers and not any(
                            self._check_card_code_match(target_id, product_name)
                            for target_id in all_target_card_numbers
                        ):
                            continue

                    # 通過所有檢查，加入保留名單
                    cleaned_rows.append(row)
                    if p_id:
                        seen_product_ids.add(p_id)

        except FileNotFoundError:
            raise FileNotFoundError(f"找不到輸入檔案: {input_csv}")
        except Exception as e:
            raise RuntimeError(f"處理 CSV 時發生錯誤: {e}")

        # ============================================================
        # 3. 寫入結果檔案
        # ============================================================
        try:
            with open(output_csv, "w", encoding="utf-8", newline="") as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(cleaned_rows)

            if seller_excluded_count > 0:
                logger.info(f"已排除 {seller_excluded_count} 個黑名單賣家的商品。")
            logger.info(f"成功清理並保留 {len(cleaned_rows)} 筆資料。")
            logger.info(f"結果已儲存至: {output_csv}")

        except Exception as e:
            raise RuntimeError(f"寫入檔案時發生錯誤: {e}")
