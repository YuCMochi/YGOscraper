import json
import glob
import pandas as pd
import pulp
import datetime

def load_shopping_cart(cart_path='cart.json'):
    """從 cart.json 讀取購物車需求"""
    print(f"從 {cart_path} 載入購物車...")
    with open(cart_path, 'r', encoding='utf-8') as f:
        cart_data = json.load(f)
    
    needed_cards = {
        item['card_name_zh']: item['required_amount']
        for item in cart_data['shopping_cart']
    }
    shipping_fee = cart_data['global_settings']['default_shipping_cost']
    
    print(f"預計運費: {shipping_fee}")
    print("需求清單:")
    for name, amount in needed_cards.items():
        print(f"  - {name} (需 {amount} 張)")
    return needed_cards, shipping_fee

def load_market_data(needed_cards):
    """從 CSV 檔案讀取市場上的卡片資訊"""
    print("\n正在讀取市場資料...")
    csv_files = glob.glob('C_ruten*.csv')
    if not csv_files:
        print("錯誤：在根目錄下找不到任何 'C_ruten' 開頭的 CSV 檔案！")
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

def solve_best_combination(data, needed_cards, shipping_fee):
    """使用 PuLP 計算最佳購買組合 (修正版)"""
    print("\n正在計算最佳組合...")

    # --- 資料預處理 ---
    # `data` 現在是包含所有獨立商品資訊的 list of dicts
    sellers = set(item['seller_id'] for item in data)
    num_listings = len(data)

    # --- 建立數學模型 (PuLP) ---
    prob = pulp.LpProblem("Card_Optimizer", pulp.LpMinimize)

    # 變數 1: use_seller[賣家] -> 0或1 (二元變數)
    use_seller = pulp.LpVariable.dicts("UseSeller", sellers, cat='Binary')

    # 變數 2: buy_qty[i] -> 從第 i 個商品購買的數量 (整數變數)
    buy_qty = pulp.LpVariable.dicts("BuyQty", range(num_listings), lowBound=0, cat='Integer')

    # --- 設定限制條件 ---

    # 限制 1: 每張需要的卡，總購買量必須剛好等於需求量
    for card, required_amount in needed_cards.items():
        # 加總所有符合該卡名的商品的購買量
        potential_buys = [buy_qty[i] for i, listing in enumerate(data) if listing['search_card_name'] == card]
        
        if not potential_buys:
            print(f"\n警告：市場上找不到任何賣家販售 '{card}'！無法完成最佳化。")
            return
        prob += pulp.lpSum(potential_buys) == required_amount, f"Fulfill_{card.replace(' ', '_')}"

    # 限制 2: 向某個商品購買的數量，不能超過它的庫存
    for i in range(num_listings):
        prob += buy_qty[i] <= data[i]['stock_qty'], f"StockLimit_{i}"

    # 限制 3: 如果在某家店買了卡(buy_qty > 0)，則必須啟用該店的運費(use_seller=1)
    # 這裡我們對每個賣家下的所有商品進行關聯
    for seller_id in sellers:
        # 找出這個賣家的所有商品 index
        listings_from_seller = [i for i, listing in enumerate(data) if listing['seller_id'] == seller_id]
        for i in listings_from_seller:
            # 購買量 <= 該商品最大庫存 * 該賣家是否啟用
            prob += buy_qty[i] <= data[i]['stock_qty'] * use_seller[seller_id], f"ShippingLogic_{i}"

    # --- 設定目標函數 (總金額) ---
    # 1. 卡片總價格
    items_cost = pulp.lpSum([buy_qty[i] * data[i]['price'] for i in range(num_listings)])
    
    # 2. 運費總價格
    shipping_total = pulp.lpSum([use_seller[s] * shipping_fee for s in sellers])
    
    prob += items_cost + shipping_total

    # --- 求解 ---
    # 動態生成檔名，例如：20231214_152024.log
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{timestamp}.log"
    
    # 將問題寫入 .log 檔案以供除錯
    print(f"將 PuLP 問題寫入至 {log_filename}...")
    prob.writeLP(log_filename)
    
    # 使用 CBC 求解器，並可以增加時間限制
    solver = pulp.PULP_CBC_CMD(timeLimit=300, msg=1)
    prob.solve(solver)

    # --- 輸出結果 ---
    if pulp.LpStatus[prob.status] == 'Optimal':
        total_price = pulp.value(prob.objective)
        print(f"\n=== 找到最佳方案！總金額: ${int(total_price)} ===")
        
        final_plan = {}
        purchase_summary = []
        
        for i in range(num_listings):
            if buy_qty[i].varValue > 0:
                listing = data[i]
                quantity = int(buy_qty[i].varValue)
                seller_id = listing['seller_id']

                # 收集簡易購買清單的資訊
                purchase_summary.append({
                    "product_id": listing['product_id'],
                    "張數": quantity
                })
                
                if seller_id not in final_plan:
                    final_plan[seller_id] = []
                
                # 收集詳細購買清單的資訊
                final_plan[seller_id].append({
                    "card": listing['search_card_name'],
                    "price": listing['price'],
                    "quantity": quantity,
                    "product_name": listing['product_name'] 
                })

        # --- 新增：輸出簡易購買清單 ---
        if purchase_summary:
            print("\n---【最終購買清單】---")
            summary_df = pd.DataFrame(purchase_summary)
            # 使用 to_string() 讓表格對齊且不顯示 index
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
        print("可能原因：")
        print("1. 某張卡片的市場總庫存量小於您的需求量。")
        print("2. 求解器在時間限制內未找到解。")

def main():
    """主執行函數"""
    try:
        needed_cards, shipping_fee = load_shopping_cart()
        market_data = load_market_data(needed_cards)
        
        if market_data is not None and needed_cards:
            solve_best_combination(market_data, needed_cards, shipping_fee)
            
    except FileNotFoundError as e:
        print(f"\n錯誤：找不到檔案 {e.filename}。請確認 'cart.json' 是否存在。")
    except Exception as e:
        print(f"\n發生預期外的錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()