import json
import pandas as pd
import pulp
import datetime
import os
import argparse

def load_shopping_cart(cart_path='data/cart.json'):
    """讀取購物車設定，了解使用者想買什麼"""
    print(f"正在讀取購物車設定: {cart_path}...")
    with open(cart_path, 'r', encoding='utf-8') as f:
        cart_data = json.load(f)
    
    # 建立需求清單：{卡片名稱: 需要數量}
    needed_cards = {
        item['card_name_zh']: item['required_amount']
        for item in cart_data['shopping_cart']
    }
    
    settings = cart_data.get('global_settings', {})
    shipping_fee = settings.get('default_shipping_cost', 60)
    min_purchase_limit = settings.get('min_purchase_limit', 0)
    
    print(f"預設運費: {shipping_fee} 元")
    if min_purchase_limit > 0:
        print(f"賣家最低消費限制: {min_purchase_limit} 元")
    
    print("本次購物清單:")
    for name, amount in needed_cards.items():
        print(f"  - {name} (需 {amount} 張)")
    return needed_cards, shipping_fee, min_purchase_limit

def load_market_data(needed_cards, market_data_path):
    """讀取清理後的市場資料 CSV"""
    print(f"\n正在讀取市場行情資料: {market_data_path}...")
    
    if not os.path.exists(market_data_path):
        print(f"錯誤：找不到檔案 {market_data_path}！")
        return None
    
    # 讀取 CSV，並確保賣家 ID 是文字格式 (避免變成科學記號)
    df = pd.read_csv(market_data_path, dtype={'seller_id': str})
    
    # 只保留我們需要的卡片資料
    market_data = df[df['search_card_name'].isin(needed_cards.keys())].copy()
    
    # 過濾掉庫存是 0 的無效商品
    original_count = len(market_data)
    market_data = market_data[market_data['stock_qty'] > 0]
    filtered_count = len(market_data)
    
    if original_count > filtered_count:
        print(f"已過濾掉 {original_count - filtered_count} 筆無庫存商品。ளி")

    # 幫每個商品加上一個唯一的編號，讓數學模型可以識別
    market_data['listing_id'] = market_data.index
    
    # 轉成字典列表格式
    card_listings = market_data.to_dict('records')

    print(f"有效商品數量: {len(card_listings)} 筆。ளி")
    return card_listings

def solve_best_combination(data, needed_cards, shipping_fee, min_purchase_limit, log_path=None, output_json_path=None):
    """
    核心演算法：使用 PuLP (線性規劃) 找出最省錢的買法
    目標：商品總價 + 運費 = 最低
    """
    print("\n正在計算最佳購買組合 (啟動數學模型)...")

    # --- 1. 建立索引 (就像圖書館的目錄) ---
    # 讓我們可以快速找到「某張卡有哪些賣家賣」以及「某個賣家賣哪些卡」
    num_listings = len(data)
    card_to_indices = {}
    seller_to_indices = {}
    
    for i, item in enumerate(data):
        c_name = item['search_card_name']
        s_id = item['seller_id']
        
        if c_name not in card_to_indices:
            card_to_indices[c_name] = []
        card_to_indices[c_name].append(i)
        
        if s_id not in seller_to_indices:
            seller_to_indices[s_id] = []
        seller_to_indices[s_id].append(i)

    sellers = list(seller_to_indices.keys())

    # --- 2. 預先檢查 (防呆機制) ---
    # 如果市場上某張卡的總庫存根本不夠買，直接報錯，不用算了
    for card, required in needed_cards.items():
        indices = card_to_indices.get(card, [])
        total_stock = sum(data[i]['stock_qty'] for i in indices)
        if total_stock < required:
            print(f"\n[無法計算] 卡片 '{card}' 市場總庫存 ({total_stock}) 不足，您需要 ({required}) 張。ளி")
            return

    # --- 3. 設定數學題目 ---
    # 我們要解的是一個「最小化」問題 (Minimize)
    prob = pulp.LpProblem("Card_Optimizer", pulp.LpMinimize)

    # 定義變數 (電腦可以調整的開關)
    # use_seller[賣家ID]: 0=不跟這家買, 1=要跟這家買
    use_seller = pulp.LpVariable.dicts("UseSeller", sellers, cat='Binary')
    
    # buy_qty[商品ID]: 這個商品要買幾張？ (整數，不能是負的)
    buy_qty = pulp.LpVariable.dicts("BuyQty", range(num_listings), lowBound=0, cat='Integer')

    # --- 4. 設定規則 (Constraints) ---

    # 規則 A: 需求滿足 - 每種卡片買到的數量，必須等於您想要的數量
    for card, required_amount in needed_cards.items():
        indices = card_to_indices[card] 
        prob += pulp.lpSum([buy_qty[i] for i in indices]) == required_amount, f"Fulfill_{card}"

    # 規則 B: 庫存與運費 - 
    # 1. 買的數量不能超過賣家庫存
    # 2. 如果跟這個賣家買了東西 (buy_qty > 0)，就必須支付運費 (use_seller = 1)
    for s_id in sellers:
        seller_indices = seller_to_indices[s_id]
        seller_var = use_seller[s_id]
        
        for i in seller_indices:
            stock = data[i]['stock_qty']
            # 數學式：購買量 <= 庫存量 * 有沒有啟用該賣家
            # 如果 use_seller 是 0，那購買量就被強制壓成 0
            prob += buy_qty[i] <= stock * seller_var, f"Link_Stock_Seller_{i}"

    # 規則 C: 最低消費 - 如果有設定低消
    if min_purchase_limit > 0:
        for s_id in sellers:
            seller_indices = seller_to_indices[s_id]
            seller_var = use_seller[s_id]
            
            # 該賣家所有商品的總金額
            seller_items_cost = pulp.lpSum([buy_qty[i] * data[i]['price'] for i in seller_indices])
            
            # 如果啟用了賣家 (seller_var=1)，總金額必須 >= 低消
            prob += seller_items_cost >= min_purchase_limit * seller_var, f"Min_Purchase_Limit_{s_id}"

    # --- 5. 設定目標 (Objective) ---
    # 我們希望 (所有商品總價 + 所有運費) 越低越好
    items_cost = pulp.lpSum([buy_qty[i] * data[i]['price'] for i in range(num_listings)])
    shipping_total = pulp.lpSum([use_seller[s] * shipping_fee for s in sellers])
    
    prob += items_cost + shipping_total

    # --- 6. 開始求解 ---
    if not log_path:
        # 如果沒指定日誌路徑，就用時間當檔名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = f"data/{timestamp}.log"
    
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    print(f"正在記錄計算過程: {log_path}")
    prob.writeLP(log_path)
    
    # 呼叫求解器 (設定時間限制 300秒)
    solver = pulp.PULP_CBC_CMD(timeLimit=300, msg=1, gapRel=0.0)
    prob.solve(solver)

    # --- 7. 輸出結果 ---
    if pulp.LpStatus[prob.status] == 'Optimal':
        total_price_with_shipping = pulp.value(prob.objective)
        print(f"\n=== 計算成功！最佳總金額 (含運費): ${int(total_price_with_shipping)} ===")
        
        # 整理結果轉為 JSON
        final_json_output = {
            "sellers": {},
            "summary": {}
        }
        
        # 整理每個賣家的購買清單
        temp_sellers = {}
        for i in range(num_listings):
            if buy_qty[i].varValue and buy_qty[i].varValue > 0:
                listing = data[i]
                quantity = int(buy_qty[i].varValue)
                seller_id = listing['seller_id']

                if seller_id not in temp_sellers:
                    temp_sellers[seller_id] = []
                
                item_details = {
                    'buy_qty': quantity,
                    'search_card_name': listing.get('search_card_name'),
                    'product_id': listing.get('product_id'),
                    'product_name': listing.get('product_name'),
                    'seller_id': seller_id,
                    'price': listing.get('price'),
                    'shipping_cost': listing.get('shipping_cost', shipping_fee),
                    'post_time': listing.get('post_time'),
                    'image_url': listing.get('image_url'),
                }
                temp_sellers[seller_id].append(item_details)
        
        # 計算小計
        all_items_cost = 0
        sorted_seller_ids = sorted(temp_sellers.keys())

        for seller_id in sorted_seller_ids:
            items = temp_sellers[seller_id]
            seller_items_cost = sum(item['price'] * item['buy_qty'] for item in items)
            all_items_cost += seller_items_cost
            final_json_output["sellers"][seller_id] = {
                "items": items,
                "items_subtotal": int(seller_items_cost)
            }
        
        # 總結資訊
        num_sellers = len(temp_sellers)
        total_shipping_cost = num_sellers * shipping_fee
        final_json_output['summary'] = {
            'total_items_cost': int(all_items_cost),
            'total_shipping_cost': int(total_shipping_cost),
            'grand_total': int(all_items_cost + total_shipping_cost),
            'sellers_count': num_sellers
        }

        # 寫入 JSON 檔案
        if not output_json_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_json_path = f"data/purchase_plan_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

        print(f"\n方案已儲存至: {output_json_path}")
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(final_json_output, f, ensure_ascii=False, indent=4)
        
        # 在終端機印出簡單結果
        print("\n--- 購買方案摘要 ---")
        print(json.dumps(final_json_output['summary'], ensure_ascii=False, indent=4))

    else:
        print(f"\n[失敗] 無法找到最佳解。狀態代碼: {pulp.LpStatus[prob.status]}")
        print("可能原因：條件太嚴苛（例如低消太高、庫存不足），或是運算超時。")

def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description='購買方案最佳化計算器')
    parser.add_argument('--cart', default='data/cart.json', help='購物車設定檔路徑')
    parser.add_argument('--input_csv', required=True, help='市場資料 CSV 路徑')
    parser.add_argument('--output_log', default=None, help='運算日誌輸出路徑')
    parser.add_argument('--output_json', default=None, help='結果 JSON 輸出路徑')
    args = parser.parse_args()

    try:
        # 載入資料
        needed_cards, shipping_fee, min_purchase_limit = load_shopping_cart(args.cart)
        market_data = load_market_data(needed_cards, args.input_csv)
        
        # 執行計算
        if market_data is not None and needed_cards:
            solve_best_combination(
                market_data, 
                needed_cards, 
                shipping_fee, 
                min_purchase_limit, 
                args.output_log, 
                args.output_json
            )
            
    except FileNotFoundError as e:
        print(f"\n錯誤：找不到檔案 {e.filename}。")
    except Exception as e:
        print(f"\n發生預期外的錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
