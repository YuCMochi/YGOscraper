import csv
import json
import glob
import os

def clean_latest_ruten_csv():
    # 1. 尋找最新的 ruten*.csv 檔案
    try:
        list_of_files = glob.glob('ruten*.csv')
        if not list_of_files:
            print("未找到以 'ruten' 開頭的 CSV 檔案。")
            return
        latest_file = max(list_of_files, key=os.path.getmtime)
        print(f"正在處理最新的檔案: {latest_file}")
    except Exception as e:
        print(f"尋找最新的 CSV 檔案時發生錯誤: {e}")
        return

    # 2. 從 cart.json 讀取設定
    try:
        with open('cart.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        global_settings = config.get('global_settings', {})
        # 讀取排除關鍵字
        exclude_keywords = global_settings.get('global_exclude_keywords', [])
        print(f"排除關鍵字: {exclude_keywords}")
        # 讀取排除的賣家 ID
        exclude_sellers = global_settings.get('global_exclude_seller', [])
        if exclude_sellers:
            print(f"排除賣家 ID: {exclude_sellers}")
            
        # 讀取所有目標卡號
        all_target_ids = []
        for item in config.get('shopping_cart', []):
            all_target_ids.extend(item.get('target_ids', []))
        if not all_target_ids:
            print("警告: 在 cart.json 中找不到任何 target_ids。")
        else:
            print(f"已載入 {len(all_target_ids)} 個目標卡號。")
    except FileNotFoundError:
        print("錯誤: 找不到 cart.json。")
        return
    except json.JSONDecodeError:
        print("錯誤: 無法解析 cart.json。")
        return

    # 3. 處理 CSV 檔案
    cleaned_rows = []
    seller_excluded_count = 0
    try:
        with open(latest_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            for row in reader:
                # 依黑名單賣家ID過濾
                if row.get('seller_id') in exclude_sellers:
                    seller_excluded_count += 1
                    continue

                # 依價格過濾
                try:
                    price = float(row.get('price', 0))
                    if price > 5000:
                        continue
                except (ValueError, TypeError):
                    # 保留價格不是有效數字或缺失的行
                    pass

                product_name = row.get('product_name', '')
                
                # 新增篩選條件：刪除商品名稱中含有 "ebay" 的商品 (不分大小寫)
                if "ebay" in product_name.lower():
                    continue
                
                # 新增篩選條件：刪除 image_url 中含有 "ebay" 的商品 (不分大小寫)
                image_url = row.get('image_url', '')
                if "ebay" in image_url.lower():
                    continue

                # 依排除關鍵字過濾
                if any(keyword in product_name for keyword in exclude_keywords):
                    continue
                
                # 依目標卡號過濾
                if all_target_ids and not any(target_id in product_name for target_id in all_target_ids):
                    continue
                
                cleaned_rows.append(row)
    except FileNotFoundError:
        print(f"錯誤: 找不到 {latest_file}。")
        return
    except Exception as e:
        print(f"處理 CSV 時發生錯誤: {e}")
        return
        
    # 4. 寫入新檔案並（選擇性）移除舊檔案
    output_filename = f"C_{os.path.basename(latest_file)}"
    
    try:
        with open(output_filename, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_rows)
        
        if seller_excluded_count > 0:
            print(f"因賣家黑名單排除了 {seller_excluded_count} 個商品。")
        print(f"成功清理 {len(cleaned_rows)} 行。")
        print(f"清理後的檔案儲存為: {output_filename}")
        
        # os.remove(latest_file)
        # print(f"原始檔案 '{latest_file}' 已被移除。")

    except Exception as e:
        print(f"寫入新的 CSV 檔案時發生錯誤: {e}")

if __name__ == "__main__":
    clean_latest_ruten_csv()