import json
import glob
import pandas as pd
import pulp
import datetime
import os

def load_shopping_cart(cart_path='data/cart.json'):
    """從 cart.json 讀取購物車需求"""
    print(f"從 {cart_path} 載入購物車...")
    with open(cart_path, 'r', encoding='utf-8') as f:
        cart_data = json.load(f)
    
    needed_cards = {
        item['card_name_zh']: item['required_amount']
        for item in cart_data['shopping_cart']
    }
    
    settings = cart_data.get('global_settings', {})
    shipping_fee = settings.get('default_shipping_cost', 60)
    min_purchase_limit = settings.get('min_purchase_limit', 0)
    
    print(f"預計運費: {shipping_fee}")
    if min_purchase_limit > 0:
        print(f"單一商家最低消費金額 (不含運費): {min_purchase_limit}")
    
    print("需求清單:")
    for name, amount in needed_cards.items():
        print(f"  - {name} (需 {amount} 張)")
    return needed_cards, shipping_fee, min_purchase_limit

def load_market_data(needed_cards):
    """從 CSV 檔案讀取市場上的卡片資訊"""
    print("\n正在讀取市場資料...")
    csv_files = glob.glob('data/C_ruten*.csv')
    if not csv_files:
        print("錯誤：在 'data' 目錄下找不到任何 'C_ruten' 開頭的 CSV 檔案！")
        return None
    
    print(f"找到以下檔案: {', '.join(csv_files)}")
    # 增加 dtype={'seller_id': str} 確保賣家ID被當作字串處理
    df = pd.concat((pd.read_csv(f, dtype={'seller_id': str}) for f in csv_files), ignore_index=True)
    
    # 過濾出我們需要的卡片
    market_data = df[df['search_card_name'].isin(needed_cards.keys())].copy()
    
    # 【修正】過濾掉庫存 <= 0 的商品，這是造成無解的根本原因
    original_count = len(market_data)
    market_data = market_data[market_data['stock_qty'] > 0]
    filtered_count = len(market_data)
    if original_count > filtered_count:
        print(f"過濾掉 {original_count - filtered_count} 個庫存小於或等於 0 的無效商品。")

    # 增加一個獨一無二的商品ID，以便 PuLP 區分
    market_data['listing_id'] = market_data.index
    
    # 轉換為 pulp 需要的格式
    card_listings = market_data.to_dict('records')

    print(f"從市場資料中找到 {len(card_listings)} 個相關商品。")
    return card_listings

def solve_best_combination(data, needed_cards, shipping_fee, min_purchase_limit):
    """使用 PuLP 計算最佳購買組合 (白話註解優化版)"""
    print("\n正在計算最佳組合 (算法優化中)...")

    # --- 1. 資料整理 (就像把亂七八糟的傳單分類整理好) ---
    num_listings = len(data)
    
    # 【優化重點 1】建立快速查找表
    # 原本的寫法：每次要找某張卡，都要把整疊傳單(data)從頭翻到尾。
    # 現在的寫法：先花一點時間做目錄。
    #   - card_to_indices: 想買「青眼白龍」？直接翻到第 5, 12, 80 頁。
    #   - seller_to_indices: 想看「賣家A」賣什麼？直接翻到第 5, 6, 7 頁。
    card_to_indices = {} 
    seller_to_indices = {}
    
    for i, item in enumerate(data):
        c_name = item['search_card_name']
        s_id = item['seller_id']
        
        # 建立卡片目錄
        if c_name not in card_to_indices:
            card_to_indices[c_name] = []
        card_to_indices[c_name].append(i)
        
        # 建立賣家目錄
        if s_id not in seller_to_indices:
            seller_to_indices[s_id] = []
        seller_to_indices[s_id].append(i)

    sellers = list(seller_to_indices.keys())

    # --- 2. 提早檢查 (就像出門前先打電話問老闆有沒有貨) ---
    # 【優化重點 2】提早檢測無解
    # 原本的寫法：不管有沒有貨，先架設超級電腦算半天，最後才說無解。
    # 現在的寫法：先算一下市場總庫存，如果不夠您要的量，直接報錯，不用浪費時間算錢了。
    for card, required in needed_cards.items():
        indices = card_to_indices.get(card, [])
        total_stock = sum(data[i]['stock_qty'] for i in indices)
        if total_stock < required:
            print(f"\n錯誤：市場上 '{card}' 的總庫存 ({total_stock}) 不足需求量 ({required})！無法求解。")
            return

    # --- 3. 設定數學模型 (告訴電腦我們的目標) ---
    prob = pulp.LpProblem("Card_Optimizer", pulp.LpMinimize)

    # 變數定義 (電腦可以調整的數字)
    # use_seller: 這個賣家要不要用？ (0=不用, 1=要用)
    use_seller = pulp.LpVariable.dicts("UseSeller", sellers, cat='Binary')
    # buy_qty: 這個商品要買幾張？
    buy_qty = pulp.LpVariable.dicts("BuyQty", range(num_listings), lowBound=0, cat='Integer')

    # --- 4. 設定限制規則 (給電腦的購買守則) ---

    # 規則 A: 每種卡片都要買齊
    for card, required_amount in needed_cards.items():
        # 直接查目錄，不用再從頭翻資料了 (速度變快很多)
        indices = card_to_indices[card] 
        prob += pulp.lpSum([buy_qty[i] for i in indices]) == required_amount, f"Fulfill_{card}"

    # 規則 B: 庫存與運費邏輯
    # 【優化重點 3】邏輯合併
    # 原本寫了兩條規則：1.不能買超過庫存 2.如果不付運費就不能買。
    # 現在合併成一句話：「購買量 必須小於或等於 (庫存量 x 有沒有付運費)」
    #  - 如果沒付運費 (use_seller=0)，購買量就必須 <= 0 (也就是不能買)。
    #  - 如果有付運費 (use_seller=1)，購買量就必須 <= 庫存量 (正常買)。
    for s_id in sellers:
        seller_indices = seller_to_indices[s_id] # 直接查賣家目錄
        seller_var = use_seller[s_id]
        
        for i in seller_indices:
            stock = data[i]['stock_qty']
            prob += buy_qty[i] <= stock * seller_var, f"Link_Stock_Seller_{i}"

    # 規則 C: 處理單一商家低消限制
    if min_purchase_limit > 0:
        for s_id in sellers:
            seller_indices = seller_to_indices[s_id]
            seller_var = use_seller[s_id]
            
            # 計算該賣家的商品總金額
            seller_items_cost = pulp.lpSum([buy_qty[i] * data[i]['price'] for i in seller_indices])
            
            # 如果啟用賣家(seller_var=1)，商品總額必須 >= 低消。
            # 如果未啟用(seller_var=0)，商品總額為0，此條件 (0 >= 0) 自然滿足。
            prob += seller_items_cost >= min_purchase_limit * seller_var, f"Min_Purchase_Limit_{s_id}"

    # --- 5. 設定目標 (我們想要什麼最少？) ---
    # 商品總價
    items_cost = pulp.lpSum([buy_qty[i] * data[i]['price'] for i in range(num_listings)])
    # 運費總價 (有啟用的賣家才算運費)
    shipping_total = pulp.lpSum([use_seller[s] * shipping_fee for s in sellers])
    
    # 目標：總花費越少越好
    prob += items_cost + shipping_total

    # --- 6. 開始計算 ---
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"data/{timestamp}.log"
    print(f"將問題寫入記錄檔 {log_filename}...")
    prob.writeLP(log_filename)
    
    # 叫電腦開始算 (gapRel=0.0 代表我要精確解，不接受大概的答案)
    solver = pulp.PULP_CBC_CMD(timeLimit=300, msg=1, gapRel=0.0)
    prob.solve(solver)

    # --- 輸出結果 (跟原本一樣，沒動) ---
    if pulp.LpStatus[prob.status] == 'Optimal':
        total_price = pulp.value(prob.objective)
        print(f"\n=== 找到最佳方案！總金額: ${int(total_price)} ===")
        
        final_plan = {}
        purchase_summary = []
        
        for i in range(num_listings):
            val = buy_qty[i].varValue
            if val and val > 0:
                listing = data[i]
                quantity = int(val)
                seller_id = listing['seller_id']

                purchase_summary.append({
                    "product_id": listing['product_id'],
                    "張數": quantity
                })
                
                if seller_id not in final_plan:
                    final_plan[seller_id] = []
                
                final_plan[seller_id].append({
                    "card": listing['search_card_name'],
                    "price": listing['price'],
                    "quantity": quantity,
                    "product_name": listing['product_name'] 
                })

        if purchase_summary:
            print("\n---【最終購買清單】---")
            summary_df = pd.DataFrame(purchase_summary)
            print(summary_df.to_string(index=False))
            print("----------------------")
        
        grand_total_check = 0
        for seller_id, items in sorted(final_plan.items()):
            seller_item_cost = sum(i['price'] * i['quantity'] for i in items)
            subtotal = seller_item_cost + shipping_fee
            grand_total_check += subtotal
            
            print(f"\n--- 商家ID: {seller_id} ---")
            print(f"  運費: {shipping_fee}")
            print(f"  小計: {int(subtotal)}")
            print("  購買明細:")
            for item in items:
                print(f"    - [{item['card']}] {item['product_name']} (${item['price']}) x {item['quantity']} 張")
        
        print("\n==========================================")
        print(f"驗算總金額: {int(grand_total_check)}")

    else:
        print(f"\n無法找到最佳解。狀態: {pulp.LpStatus[prob.status]}")
        print("可能原因：求解器在時間限制內未找到解，或者邏輯上有衝突。")

def main():
    """主執行函數"""
    try:
        # 確保 'data' 目錄存在
        os.makedirs('data', exist_ok=True)
        
        needed_cards, shipping_fee, min_purchase_limit = load_shopping_cart()
        market_data = load_market_data(needed_cards)
        
        if market_data is not None and needed_cards:
            solve_best_combination(market_data, needed_cards, shipping_fee, min_purchase_limit)
            
    except FileNotFoundError as e:
        print(f"\n錯誤：找不到檔案 {e.filename}。請確認 'cart.json' 是否存在於 'data' 目錄中。")
    except Exception as e:
        print(f"\n發生預期外的錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()