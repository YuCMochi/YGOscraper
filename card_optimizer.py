import time
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import pandas as pd
from collections import defaultdict
import os
import re
import glob
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from datetime import datetime

@dataclass
class DatabaseInfo:
    url: str
    target_quantity: int
    card_name: str

@dataclass
class Product:
    product_id: str
    seller_id: str
    price: int
    shipping_cost: int
    stock_qty: int
    card_name: str
    effective_price: float = 0.0  # 新增有效價格欄位

@dataclass
class PurchaseResult:
    total_price: int
    purchase_combinations: List[Tuple[str, int, str]]  # (product_id, quantity, card_name)
    execution_time: float
    iteration_count: int = 0  # 新增迭代次數統計

class CardOptimizer:
    def __init__(self, max_sellers_per_card: int = 100):
        self.best_solution = None
        self.best_price = float('inf')
        self.start_time = 0
        self.max_sellers_per_card = max_sellers_per_card
        self.iteration_count = 0
        self.progress_interval = 1000  # 進度顯示間隔

    def preprocess_data(self, products: List[Product], target_quantities: Dict[str, int]) -> List[Product]:
        """
        對每種卡片進行預處理：
        1. 如果商品數量 <= 110，保留所有商品
        2. 如果商品數量 > 110，過濾掉價格前四分之一高的商品
        """
        # 按卡片類型分組商品
        card_products = defaultdict(list)
        for product in products:
            card_products[product.card_name].append(product)
        
        pruned_products = []
        
        # 對每種卡片的商品進行預處理
        for card_name, items in card_products.items():
            demand = target_quantities[card_name]
            
            # 計算每個商品的性價比（價格 + 平均運費分攤）
            for item in items:
                item.effective_price = item.price + (item.shipping_cost / demand)
            
            # 按性價比排序
            items.sort(key=lambda x: x.effective_price)
            
            # 根據商品數量決定過濾策略
            if len(items) > 110:
                # 過濾掉價格前四分之一高的商品
                q3_index = int(len(items) * 0.75)  # 第三四分位數
                filtered_items = items[:q3_index]
                print(f"卡片 {card_name} 有 {len(items)} 個商品，過濾後保留 {len(filtered_items)} 個")
                pruned_products.extend(filtered_items)
            else:
                # 保留所有商品
                print(f"卡片 {card_name} 有 {len(items)} 個商品，保留全部")
                pruned_products.extend(items)
        
        return pruned_products

    def find_optimal_purchase(self, products: List[Product], target_quantities: Dict[str, int]) -> PurchaseResult:
        """
        使用兩階段算法尋找最佳購買組合
        """
        self.start_time = time.time()
        self.best_solution = None
        self.best_price = float('inf')
        self.iteration_count = 0
        
        # 過濾掉庫存為 0 的商品
        available_products = [p for p in products if p.stock_qty > 0]
        
        if not available_products:
            print("警告：沒有可用的商品，嘗試從所有商品中尋找...")
            available_products = products
        
        print("\n開始預處理數據...")
        # 預處理數據
        pruned_products = self.preprocess_data(available_products, target_quantities)
        print(f"預處理完成，共保留 {len(pruned_products)} 個商品")
        
        print("\n開始第一階段：貪心算法...")
        # 階段1：貪心算法獲得初始解
        initial_solution = self.greedy_initial_solution(pruned_products, target_quantities)
        initial_price = self.calculate_total_price(initial_solution, pruned_products)
        print(f"貪心算法完成，初始價格：{initial_price}")
        
        # 檢查是否所有需求都滿足
        remaining_quantities = target_quantities.copy()
        for product_id, quantity, card_name in initial_solution:
            remaining_quantities[card_name] -= quantity
        
        if any(qty > 0 for qty in remaining_quantities.values()):
            print("警告：部分卡片需求未完全滿足，但已找到可行解")
        
        print("\n開始第二階段：局部搜索優化...")
        # 階段2：局部搜索優化
        final_solution = self.local_search_optimization(initial_solution, pruned_products, target_quantities)
        
        execution_time = time.time() - self.start_time
        return PurchaseResult(self.best_price, final_solution or initial_solution, execution_time, self.iteration_count)

    def calculate_total_price(self, solution: List[Tuple[str, int, str]], products: List[Product]) -> int:
        """
        計算解決方案的總價格
        """
        total_price = 0
        used_sellers = set()
        product_map = {p.product_id: p for p in products}
        
        for product_id, quantity, _ in solution:
            product = product_map[product_id]
            total_price += product.price * quantity
            
            if product.seller_id not in used_sellers:
                total_price += product.shipping_cost
                used_sellers.add(product.seller_id)
        
        return total_price

    def greedy_initial_solution(self, products: List[Product], target_quantities: Dict[str, int]) -> List[Tuple[str, int, str]]:
        """
        貪心算法：每種卡從當前最低價賣家購買，確保總能找到可行解
        """
        solution = []
        remaining_quantities = target_quantities.copy()
        self.best_price = 0
        
        # 按卡片類型分組商品
        card_products = defaultdict(list)
        for product in products:
            card_products[product.card_name].append(product)
        
        # 對每種卡片進行處理
        for card_name, items in card_products.items():
            if remaining_quantities[card_name] <= 0:
                continue
                
            # 按價格排序
            items.sort(key=lambda x: x.price)
            
            # 嘗試從不同賣家購買，直到滿足需求
            for item in items:
                if remaining_quantities[card_name] <= 0:
                    break
                    
                max_buy = min(remaining_quantities[card_name], item.stock_qty)
                if max_buy > 0:
                    solution.append((item.product_id, max_buy, card_name))
                    self.best_price += item.price * max_buy
                    remaining_quantities[card_name] -= max_buy
        
        # 如果還有未滿足的需求，從剩餘商品中購買
        if any(qty > 0 for qty in remaining_quantities.values()):
            print("警告：部分卡片需求未完全滿足，嘗試從其他賣家購買...")
            for product in products:
                card_name = product.card_name
                if remaining_quantities[card_name] <= 0:
                    continue
                    
                max_buy = min(remaining_quantities[card_name], product.stock_qty)
                if max_buy > 0:
                    solution.append((product.product_id, max_buy, card_name))
                    self.best_price += product.price * max_buy
                    remaining_quantities[card_name] -= max_buy
        
        # 計算總運費
        used_sellers = set()
        for product_id, _, _ in solution:
            product = next(p for p in products if p.product_id == product_id)
            if product.seller_id not in used_sellers:
                self.best_price += product.shipping_cost
                used_sellers.add(product.seller_id)
        
        return solution

    def local_search_optimization(self, initial_solution: List[Tuple[str, int, str]], 
                                products: List[Product], 
                                target_quantities: Dict[str, int]) -> List[Tuple[str, int, str]]:
        """
        局部搜索：嘗試將卡片轉移到已使用的賣家來減少運費
        """
        # 建立賣家到商品的映射
        seller_products = defaultdict(list)
        for product in products:
            seller_products[product.seller_id].append(product)
        
        # 建立商品ID到商品的映射
        product_map = {p.product_id: p for p in products}
        
        # 建立當前解決方案的賣家集合
        current_sellers = set()
        for product_id, _, _ in initial_solution:
            product = product_map[product_id]
            current_sellers.add(product.seller_id)
        
        improved = True
        current_solution = initial_solution.copy()
        last_improvement_time = time.time()
        
        while improved:
            improved = False
            self.iteration_count += 1
            
            # 顯示進度
            if self.iteration_count % self.progress_interval == 0:
                current_time = time.time()
                elapsed = current_time - self.start_time
                print(f"迭代次數：{self.iteration_count}，當前價格：{self.best_price}，已用時：{elapsed:.2f}秒")
            
            # 嘗試將卡片轉移到其他賣家
            for i, (product_id, quantity, card_name) in enumerate(current_solution):
                current_product = product_map[product_id]
                
                # 尋找其他可能提供此卡的賣家
                for seller_id in current_sellers:
                    if seller_id == current_product.seller_id:
                        continue
                    
                    # 檢查該賣家是否提供此卡
                    for other_product in seller_products[seller_id]:
                        if (other_product.card_name == card_name and 
                            other_product.stock_qty >= quantity and
                            other_product.price < current_product.price):
                            
                            # 計算成本變化
                            old_cost = current_product.price * quantity
                            new_cost = other_product.price * quantity
                            
                            if new_cost < old_cost:
                                # 更新解決方案
                                current_solution[i] = (other_product.product_id, quantity, card_name)
                                self.best_price += (new_cost - old_cost)
                                improved = True
                                last_improvement_time = time.time()
                                break
                    if improved:
                        break
                if improved:
                    break
            
            # 如果超過30秒沒有改進，提前結束
            if time.time() - last_improvement_time > 30:
                print("超過30秒沒有改進，提前結束優化")
                break
        
        return current_solution

def extract_card_name(filename: str) -> str:
    """
    從檔案名稱中提取卡片名稱
    例如：ruten_EP16-JP033_20250419_021459.csv -> EP16-JP033
    """
    match = re.search(r'ruten_([A-Z0-9-]+)_', filename)
    if match:
        return match.group(1)
    return ""

def get_database_input():
    """
    獲取使用者輸入的資料庫資訊
    """
    print("\n=== 卡片購買優化器 ===")
    print("請選擇輸入方式：")
    print("1. 手動輸入資料庫")
    print("2. 批次輸入資料庫（使用當前目錄下的所有已清理的CSV檔案）")
    
    while True:
        try:
            choice = int(input("請選擇（1或2）："))
            if choice in [1, 2]:
                break
            print("請輸入1或2！")
        except ValueError:
            print("請輸入有效的數字！")
    
    databases = []
    
    if choice == 1:
        # 手動輸入模式
        while True:
            print("\n--- 資料庫資訊 ---")
            url = input("請輸入資料庫連結（輸入 'done' 結束輸入）：").strip()
            
            if url.lower() == 'done':
                if not databases:
                    print("至少需要輸入一個資料庫！")
                    continue
                break
                
            if not os.path.exists(url):
                print(f"檔案 {url} 不存在，請重新輸入！")
                continue
                
            # 檢查是否為已清理的檔案
            if not url.endswith('_cleaned.csv'):
                print(f"警告：檔案 {url} 不是已清理的檔案（必須以 '_cleaned.csv' 結尾）")
                print("請先使用 clean_csv.py 清理檔案")
                continue
                
            while True:
                try:
                    quantity = int(input("請輸入在此資料庫要購買的卡片數量："))
                    if quantity > 0:
                        break
                    print("數量必須大於0，請重新輸入！")
                except ValueError:
                    print("請輸入有效的數字！")
            
            # 從檔案名稱中提取卡片名稱
            card_name = extract_card_name(os.path.basename(url))
            if not card_name:
                print("無法從檔案名稱中提取卡片名稱，請手動輸入：")
                card_name = input().strip()
                if not card_name:
                    print("卡片名稱不能為空！")
                    continue
            
            databases.append(DatabaseInfo(url, quantity, card_name))
    else:
        # 批次輸入模式
        csv_files = glob.glob("*_cleaned.csv")
        if not csv_files:
            print("當前目錄下沒有找到任何已清理的CSV檔案！")
            print("請先使用 clean_csv.py 清理檔案")
            return []
            
        print("\n找到以下已清理的CSV檔案：")
        card_files = {}  # 用於儲存卡片名稱和對應的檔案
        for i, file in enumerate(csv_files, 1):
            card_name = extract_card_name(file)
            if card_name:
                card_files[card_name] = file
                print(f"{i}. {file} (卡片：{card_name})")
            else:
                print(f"{i}. {file} (警告：無法提取卡片名稱)")
        
        if not card_files:
            print("沒有找到有效的卡片檔案！")
            return []
        
        print("\n請輸入每種卡片的購買數量：")
        print("格式：數量1,數量2,...")
        print("例如：3,2 表示第一個檔案買3張，第二個檔案買2張")
        
        while True:
            try:
                input_str = input("請輸入：").strip()
                if not input_str:
                    print("輸入不能為空！")
                    continue
                
                # 解析輸入
                quantities = [int(qty.strip()) for qty in input_str.split(',')]
                
                # 檢查數量是否足夠
                if len(quantities) != len(card_files):
                    print(f"需要輸入 {len(card_files)} 個數量，但只輸入了 {len(quantities)} 個")
                    continue
                
                # 檢查數量是否都為正數
                if any(qty <= 0 for qty in quantities):
                    print("所有數量必須大於0！")
                    continue
                
                # 建立資料庫資訊
                for (card_name, file), quantity in zip(card_files.items(), quantities):
                    databases.append(DatabaseInfo(file, quantity, card_name))
                break
                
            except ValueError:
                print("請輸入有效的數字！")
            except Exception as e:
                print(f"輸入格式錯誤：{e}")
    
    return databases

@lru_cache(maxsize=1000)
def load_products_from_database(url: str, card_name: str) -> List[Product]:
    """
    從資料庫載入商品資訊（使用緩存）
    """
    try:
        # 這裡假設資料庫是CSV格式
        df = pd.read_csv(url)
        products = []
        
        for idx, row in df.iterrows():
            try:
                product = Product(
                    product_id=str(row['product_id']),
                    seller_id=str(row['seller_id']),
                    price=int(row['price']),
                    shipping_cost=int(row['shipping_cost']),
                    stock_qty=int(row['stock_qty']),
                    card_name=card_name
                )
                products.append(product)
            except (KeyError, ValueError) as e:
                print(f"處理商品資料時發生錯誤：{e}")
                continue
        
        return products
    except Exception as e:
        print(f"載入資料庫時發生錯誤：{e}")
        return []

def parallel_load_databases(databases: List[DatabaseInfo]) -> Tuple[List[Product], Dict[str, int]]:
    """
    並行載入所有資料庫
    """
    all_products = []
    target_quantities = {}
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for db in databases:
            future = executor.submit(load_products_from_database, db.url, db.card_name)
            futures.append((future, db))
        
        for future, db in futures:
            products = future.result()
            if products:
                all_products.extend(products)
                target_quantities[db.card_name] = db.target_quantity
    
    return all_products, target_quantities

def main():
    # 獲取資料庫資訊
    databases = get_database_input()
    if not databases:
        print("沒有可用的資料庫，程式結束。")
        return
    
    # 顯示輸入的資料庫資訊
    print("\n已輸入的資料庫資訊：")
    for i, db in enumerate(databases, 1):
        print(f"{i}. 資料庫連結：{db.url}")
        print(f"   卡片名稱：{db.card_name}")
        print(f"   購買數量：{db.target_quantity}")
    
    # 確認是否開始計算
    while True:
        confirm = input("\n是否開始計算？（y/n）：").lower()
        if confirm in ['y', 'n']:
            break
        print("請輸入 y 或 n！")
    
    if confirm == 'n':
        print("已取消計算。")
        return
    
    # 初始化優化器
    optimizer = CardOptimizer(max_sellers_per_card=100)
    
    # 並行載入所有資料庫
    print("\n載入資料庫中...")
    all_products, target_quantities = parallel_load_databases(databases)
    
    if not all_products:
        print("沒有可用的商品資訊，程式結束。")
        return
    
    # 使用優化後的算法計算
    print("\n計算最佳購買組合中...")
    result = optimizer.find_optimal_purchase(all_products, target_quantities)
    
    print("\n計算結果：")
    if result.total_price == float('inf'):
        print("無法找到滿足需求的購買組合。")
    else:
        print(f"總價格：{result.total_price}")
        print(f"迭代次數：{result.iteration_count}")
        print(f"計算時間：{result.execution_time:.4f} 秒")
        print("\n購買組合：")
        
        # 按賣家分組購買組合
        seller_purchases = defaultdict(list)
        seller_shipping = {}
        for product_id, quantity, card_name in result.purchase_combinations:
            # 找到對應的商品資訊
            product = next(p for p in all_products if p.product_id == product_id)
            seller_purchases[product.seller_id].append((product_id, quantity, card_name, product.price))
            seller_shipping[product.seller_id] = product.shipping_cost
        
        # 顯示每個賣家的購買資訊
        total_shipping = 0
        for seller_id, purchases in seller_purchases.items():
            print(f"\n賣家 {seller_id}：")
            print(f"運費：{seller_shipping[seller_id]}")
            total_shipping += seller_shipping[seller_id]
            
            for product_id, quantity, card_name, price in purchases:
                print(f"- 卡片 {card_name} 商品 {product_id}：{quantity} 張，單價 {price}，小計 {price * quantity}")
        
        print(f"\n總運費：{total_shipping}")
        print(f"總商品價格：{result.total_price - total_shipping}")
        print(f"總計：{result.total_price}")
        print(f"計算時間：{result.execution_time:.4f} 秒")
        print(f"迭代次數：{result.iteration_count}")

if __name__ == "__main__":
    main() 