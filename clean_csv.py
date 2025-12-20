import csv
import json
import os
import argparse

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
            
        # 取得所有我們要找的卡號 (用來過濾無關商品)
        all_target_ids = []
        for item in config.get('shopping_cart', []):
            all_target_ids.extend(item.get('target_ids', []))
            
        if not all_target_ids:
            print("警告: 設定檔中沒有任何目標卡號 (target_ids)。")
        else:
            print(f"已載入 {len(all_target_ids)} 個目標卡號。")
            
    except FileNotFoundError:
        print(f"錯誤: 找不到設定檔 {cart_config}。")
        return
    except json.JSONDecodeError:
        print(f"錯誤: 設定檔格式不正確 {cart_config}。")
        return

    # 2. 開始過濾資料
    cleaned_rows = []
    seller_excluded_count = 0
    
    try:
        with open(input_csv, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            for row in reader:
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
                
                # 過濾 4: 排除 ebay 相關商品 (通常運費高且久)
                if "ebay" in product_name.lower():
                    continue
                
                image_url = row.get('image_url', '')
                if "ebay" in image_url.lower():
                    continue

                # 過濾 5: 排除關鍵字 (如卡套、桌墊等)
                if any(keyword in product_name for keyword in exclude_keywords):
                    continue
                
                # 過濾 6: 確保商品名稱包含我們要找的卡號
                # 如果完全沒對應到任何卡號，這可能是不相關的搜尋結果
                if all_target_ids and not any(target_id in product_name for target_id in all_target_ids):
                    continue
                
                # 通過所有檢查，加入保留名單
                cleaned_rows.append(row)
                
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
