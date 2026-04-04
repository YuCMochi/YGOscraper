import argparse
import csv
import json
import os
import re


def check_card_code_match(target_code, text):
    """
    使用 Regex 檢查卡號是否精確匹配，避免子字串誤判 (如 SD5 匹配到 YSD5)。
    邏輯：
    1. (?<![a-zA-Z]) : 前面不能是英文字母 (避免 YSD5 被當作 SD5)
       - 但允許前面是數字 (處理連在一起的卡號，如 ...014SD5...)
       - 也允許前面是符號或空格
    2. (?![0-9]) : 後面不能是數字 (確保卡號數字部分已結束)
    """
    # 轉義 target_code 中的特殊字元 (雖然卡號通常只有英數和橫線，但保險起見)
    # 忽略大小寫 (re.IGNORECASE)
    pattern = r'(?<![a-zA-Z])' + re.escape(target_code) + r'(?![0-9])'
    return re.search(pattern, text, re.IGNORECASE) is not None

def clean_ruten_csv(input_csv, output_csv, cart_config='data/cart.json'):
    """
    清理爬蟲抓下來的原始 CSV 資料
    input_csv: 原始檔案路徑
    output_csv: 清理後的檔案儲存路徑
    cart_config: 購物車設定檔路徑 (用來讀取黑名單)
    """
    
    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    print(f"正在處理檔案: {input_csv}")

    # 1. 讀取設定 (黑名單與關鍵字)
    try:
        with open(cart_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        global_settings = config.get('global_settings', {})
        
        # 取得排除關鍵字
        exclude_keywords = global_settings.get('global_exclude_keywords', [])
        print(f"排除關鍵字: {exclude_keywords}")
        
        # 取得排除賣家
        exclude_sellers = global_settings.get('global_exclude_seller', [])
        if exclude_sellers:
            print(f"排除賣家 ID: {exclude_sellers}")
            
        # 建立卡片名稱對應目標卡號的字典 (用來做精確過濾)
        card_target_map = {}
        all_target_card_numbers = [] # 保留原本變數以防萬一，或用於統計
        
        for item in config.get('shopping_cart', []):
            c_name = item.get('card_name_zh')
            # target_card_numbers 對應 README 中的 card_number (e.g., DABL-JP035)
            t_ids = item.get('target_card_numbers', [])
            if c_name:
                card_target_map[c_name] = t_ids
            all_target_card_numbers.extend(t_ids)
            
        if not all_target_card_numbers:
            print("警告: 設定檔中沒有任何目標卡號 (target_card_numbers)。")
        else:
            print(f"已載入 {len(all_target_card_numbers)} 個目標卡號，涵蓋 {len(card_target_map)} 種卡片。")
            
    except FileNotFoundError:
        print(f"錯誤: 找不到設定檔 {cart_config}。")
        return
    except json.JSONDecodeError:
        print(f"錯誤: 設定檔格式不正確 {cart_config}。")
        return

    # 2. 開始過濾資料
    cleaned_rows = []
    seller_excluded_count = 0
    seen_product_ids = set() # 用來記錄已經處理過的商品 ID，防止重複
    
    try:
        # 使用 utf-8-sig 以處理可能的 BOM (Byte Order Mark)
        with open(input_csv, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            for row in reader:
                # 過濾 0: 去重複 (根據 product_id)
                p_id = row.get('product_id')
                if p_id and p_id in seen_product_ids:
                    continue
                
                # 過濾 1: 黑名單賣家
                if row.get('seller_id') in exclude_sellers:
                    seller_excluded_count += 1
                    continue

                # 過濾 2: 價格異常 (超過 5000 可能是假貨或整盒賣，先過濾)
                try:
                    price = float(row.get('price', 0))
                    if price > 5000:
                        continue
                except (ValueError, TypeError):
                    pass # 價格不是數字就保留
                
                # 過濾 3: 有價差的商品 (alt_price=1 代表有多種規格，爬蟲無法確定是哪種，故排除)
                if row.get('alt_price') == '1':
                    continue

                product_name = row.get('product_name', '')
                search_card_name = row.get('search_card_name', '')
                
                # 過濾 4: 排除 ebay 相關商品 (通常運費高且久)
                if "ebay" in product_name.lower():
                    continue
                
                image_url = row.get('image_url', '')
                if "ebay" in image_url.lower():
                    continue

                # 過濾 5: 排除關鍵字 (如卡套、桌墊等)
                if any(keyword in product_name for keyword in exclude_keywords):
                    continue
                
                # 過濾 6: 確保商品名稱包含該卡片特定的目標卡號 (Strict Mode) + Regex 檢查
                # 只有當商品名稱包含 "該卡片" 指定的 target_card_numbers 中的至少一個時，才保留
                if search_card_name in card_target_map:
                    specific_targets = card_target_map[search_card_name]
                    # 使用 Regex 檢查取代原本的 simple substring check
                    if specific_targets and not any(check_card_code_match(target_id, product_name) for target_id in specific_targets):
                        continue
                else:
                    # 如果找不到對應的卡片名稱 (可能是舊資料或欄位缺失)，退回使用全域檢查
                    if all_target_card_numbers and not any(check_card_code_match(target_id, product_name) for target_id in all_target_card_numbers):
                        continue
                
                # 通過所有檢查，加入保留名單並記錄 ID
                cleaned_rows.append(row)
                if p_id:
                    seen_product_ids.add(p_id)
                
    except FileNotFoundError:
        print(f"錯誤: 找不到輸入檔案 {input_csv}。")
        return
    except Exception as e:
        print(f"處理 CSV 時發生錯誤: {e}")
        return
        
    # 3. 寫入結果檔案
    try:
        with open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)
        
        if seller_excluded_count > 0:
            print(f"已排除 {seller_excluded_count} 個黑名單賣家的商品。")
        print(f"成功清理並保留 {len(cleaned_rows)} 筆資料。")
        print(f"結果已儲存至: {output_csv}")

    except Exception as e:
        print(f"寫入檔案時發生錯誤: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CSV 資料清理工具')
    parser.add_argument('--input', required=True, help='原始 CSV 檔案路徑')
    parser.add_argument('--output', required=True, help='輸出 CSV 檔案路徑')
    parser.add_argument('--cart', default='data/cart.json', help='設定檔路徑')
    
    args = parser.parse_args()
    clean_ruten_csv(args.input, args.output, args.cart)