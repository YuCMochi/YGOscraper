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

def extract_card_name(file_path: str) -> Optional[str]:
    """從檔案名稱中提取卡片名稱"""
    # 嘗試從檔案名稱中提取卡片名稱
    # 假設檔名格式為 ruten_卡片名稱_日期_時間_cleaned.csv
    match = re.search(r'ruten_(.+?)_\d{8}_\d{6}', file_path)
    if match:
        return match.group(1)
    return None

def load_database(db_info: DatabaseInfo) -> List[Product]:
    """載入單個資料庫檔案"""
    try:
        print(f"載入資料庫：{db_info.url}")
        
        # 檢查檔案是否存在且不為空
        if not os.path.exists(db_info.url) or os.path.getsize(db_info.url) == 0:
            print(f"警告：資料庫檔案 {db_info.url} 不存在或為空檔案")
            return []
            
        # 嘗試讀取檔案的前幾行來檢查格式
        with open(db_info.url, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if not first_line or ',' not in first_line:
                print(f"警告：資料庫檔案 {db_info.url} 格式不正確，可能不是有效的CSV檔案")
                return []
        
        df = pd.read_csv(db_info.url)
        
        # 確保必要的欄位存在
        required_columns = ['product_id', 'seller_id', 'price', 'shipping_cost', 'stock_qty']
        if not all(col in df.columns for col in required_columns):
            print(f"警告：資料庫 {db_info.url} 缺少必要欄位，跳過")
            return []
        
        # 將資料轉換為 Product 物件
        products = []
        for _, row in df.iterrows():
            product = Product(
                product_id=str(row['product_id']),
                seller_id=str(row['seller_id']),
                price=int(row['price']),
                shipping_cost=int(row['shipping_cost']),
                stock_qty=int(row['stock_qty']),
                card_name=db_info.card_name
            )
            products.append(product)
        
        print(f"成功載入 {len(products)} 個商品")
        return products
    except Exception as e:
        print(f"載入資料庫 {db_info.url} 時發生錯誤：{e}")
        return []

def parallel_load_databases(databases: List[DatabaseInfo]) -> Tuple[List[Product], Dict[str, int]]:
    """並行載入多個資料庫檔案"""
    all_products = []
    target_quantities = {}
    
    # 使用線程池並行載入資料庫
    with ThreadPoolExecutor(max_workers=min(os.cpu_count(), len(databases))) as executor:
        results = list(executor.map(load_database, databases))
    
    # 合併結果
    for db_info, products in zip(databases, results):
        all_products.extend(products)
        target_quantities[db_info.card_name] = db_info.target_quantity
    
    print(f"總共載入 {len(all_products)} 個商品")
    return all_products, target_quantities

import argparse # 新增 argparse
import json     # 新增 json

def main():
    # --- 使用 argparse 解析命令行參數 ---
    parser = argparse.ArgumentParser(description='卡片購買優化器')
    parser.add_argument('--cart-json', type=str, required=True,
                        help='包含卡片名稱和目標數量的 JSON 字串')
    args = parser.parse_args()

    try:
        target_quantities = json.loads(args.cart_json)
        if not isinstance(target_quantities, dict):
            raise ValueError("購物車數據必須是 JSON 物件 (字典)")
        print("\n從參數讀取的購物車資訊：")
        for card_name, quantity in target_quantities.items():
            print(f"   卡片名稱：{card_name}")
            print(f"   購買數量：{quantity}")
            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(f"卡片 '{card_name}' 的數量必須是正整數")
    except json.JSONDecodeError:
        print("[錯誤] 無法解析 --cart-json 參數。請提供有效的 JSON 字串。")
        return
    except ValueError as e:
        print(f"[錯誤] 購物車數據格式錯誤: {e}")
        return
    except Exception as e:
        print(f"[錯誤] 處理購物車參數時發生未知錯誤: {e}")
        return

    # --- 自動尋找已清理的檔案 ---
    cleaned_files_pattern = "*_cleaned.csv" # 固定使用此模式
    csv_files = glob.glob(cleaned_files_pattern)
    if not csv_files:
        print(f"當前目錄下沒有找到任何符合 '{cleaned_files_pattern}' 的檔案！")
        print("請確保 clean_csv.py 已成功執行。")
        return

    print(f"\n找到以下已清理的 CSV 檔案 (共 {len(csv_files)} 個)：")
    databases = []
    found_cards = set()
    for file in csv_files:
        card_name = extract_card_name(file)
        if card_name:
            if card_name in target_quantities:
                quantity = target_quantities[card_name]
                databases.append(DatabaseInfo(file, quantity, card_name))
                found_cards.add(card_name)
                print(f"- {file} (卡片：{card_name}, 需求：{quantity})")
            else:
                print(f"- {file} (卡片：{card_name}, 警告：不在購物車需求中，將被忽略)")
        else:
            print(f"- {file} (警告：無法從檔名提取卡片名稱，將被忽略)")

    # 檢查是否所有需求的卡片都有對應的檔案
    missing_cards = set(target_quantities.keys()) - found_cards
    if missing_cards:
        print("\n[警告] 以下購物車中的卡片沒有找到對應的已清理 CSV 檔案：")
        for card in missing_cards:
            print(f"- {card}")
        print("[錯誤] 無法滿足所有卡片需求，流程中止。")
        return

    if not databases:
        print("\n[錯誤] 沒有找到任何與購物車需求匹配的已清理檔案。")
        return

    # --- 後續流程與原 main 函數類似 ---
    # 初始化優化器
    optimizer = CardOptimizer(max_sellers_per_card=100) # 可以調整此參數

    # 並行載入所有資料庫
    print("\n載入資料庫中...")
    # 注意：parallel_load_databases 現在直接使用 databases 列表
    all_products, loaded_target_quantities = parallel_load_databases(databases)

    if not all_products:
        print("沒有可用的商品資訊，程式結束。")
        return

    # 檢查每種卡片是否都有商品
    card_products = defaultdict(list)
    for product in all_products:
        card_products[product.card_name].append(product)
    
    missing_products = []
    for card_name, quantity in target_quantities.items():
        if card_name not in card_products or len(card_products[card_name]) == 0:
            missing_products.append(card_name)
    
    if missing_products:
        print("\n[錯誤] 以下卡片沒有找到任何商品資訊：")
        for card in missing_products:
            print(f"- {card}")
        print("無法滿足所有卡片需求，程式結束。")
        return

    # 使用優化後的算法計算
    print("\n計算最佳購買組合中...")
    # 使用從參數解析得到的 target_quantities
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
        product_map = {p.product_id: p for p in all_products} # 建立映射方便查找

        for product_id, quantity, card_name in result.purchase_combinations:
            # 找到對應的商品資訊
            # product = next((p for p in all_products if p.product_id == product_id), None) # 更安全的查找
            product = product_map.get(product_id)
            if product:
                seller_purchases[product.seller_id].append((product_id, quantity, card_name, product.price))
                # 確保只記錄一次運費
                if product.seller_id not in seller_shipping:
                     seller_shipping[product.seller_id] = product.shipping_cost
            else:
                print(f"[警告] 找不到商品 ID {product_id} 的詳細資訊。")


        # 顯示每個賣家的購買資訊
        total_shipping = sum(seller_shipping.values())
        calculated_total_price = 0

        for seller_id, purchases in seller_purchases.items():
            print(f"\n賣家 {seller_id}：")
            seller_item_total = 0
            shipping_cost = seller_shipping.get(seller_id, 0) # 獲取運費
            print(f"運費：{shipping_cost}")

            for p_id, qty, c_name, price in purchases:
                item_total = price * qty
                seller_item_total += item_total
                print(f"- 卡片 {c_name} 商品 {p_id}：{qty} 張，單價 {price}，小計 {item_total}")

            print(f"賣家商品小計：{seller_item_total}")
            calculated_total_price += seller_item_total

        calculated_total_price += total_shipping

        print(f"\n總運費：{total_shipping}")
        print(f"總商品價格：{calculated_total_price - total_shipping}")
        print(f"總計：{calculated_total_price}") # 使用計算出的總價
        # 驗證價格是否與 result.total_price 匹配
        if calculated_total_price != result.total_price:
             print(f"[驗證警告] 計算出的總價 ({calculated_total_price}) 與優化器報告的總價 ({result.total_price}) 不符，請檢查計算邏輯。")
        print(f"計算時間：{result.execution_time:.4f} 秒")
        print(f"迭代次數：{result.iteration_count}")


if __name__ == "__main__":
    main()