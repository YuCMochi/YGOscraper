import requests
import pandas as pd
from datetime import datetime
import logging
import json
import time
from fake_useragent import UserAgent
import os
import argparse
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 常數定義
BASE_URL = "https://rtapi.ruten.com.tw/api"
IMAGE_BASE_URL = "https://gcs.rimg.com.tw"
DEFAULT_TIMEOUT = 10
DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 3
ITEMS_PER_PAGE = 110
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

class RutenScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 設定重試機制
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 建立圖片儲存目錄
        self.image_dir = "product_images"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

    def _get_headers(self):
        """生成隨機的 User-Agent"""
        try:
            return {
                'User-Agent': self.ua.random,
                'Accept': 'application/json',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.ruten.com.tw/'
            }
        except Exception as e:
            logger.warning(f"生成 User-Agent 時發生錯誤，使用預設值: {e}")
            return {
                'User-Agent': DEFAULT_USER_AGENT,
                'Accept': 'application/json',
                'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.ruten.com.tw/'
            }

    def search_products(self, keyword, limit=ITEMS_PER_PAGE, offset=1):
        """
        搜尋商品並獲取商品ID
        """
        url = f"{BASE_URL}/search/v3/index.php/core/prod"
        params = {
            'q': keyword,
            'type': 'direct',
            'sort': 'rnk/dc',
            'limit': limit,
            'offset': offset
        }
        
        try:
            response = self.session.get(url, params=params, headers=self._get_headers(), timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            result = response.json()
            
            # 檢查總商品數量
            if result and 'TotalRows' in result:
                total_rows = result['TotalRows']
                if total_rows < limit:
                    logger.info(f"搜尋結果只有 {total_rows} 個商品，調整爬取數量")
                    return result, total_rows
                    
            return result, limit
        except requests.RequestException as e:
            logger.error(f"搜尋商品時發生錯誤: {e}")
            return None, 0

    def get_product_details(self, product_ids):
        """
        獲取商品詳細資訊
        """
        if isinstance(product_ids, list):
            product_ids = ','.join(product_ids)
            
        url = f"{BASE_URL}/prod/v2/index.php/prod"
        params = {'id': product_ids}
        
        try:
            response = self.session.get(url, params=params, headers=self._get_headers(), timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"獲取商品詳情時發生錯誤: {e}")
            return None

    def download_image(self, image_path, product_id):
        """
        下載商品圖片
        """
        if not image_path:
            return None
            
        full_url = f"{IMAGE_BASE_URL}{image_path}"
        try:
            response = self.session.get(full_url, headers=self._get_headers())
            response.raise_for_status()
            
            # 儲存圖片
            file_extension = image_path.split('.')[-1]
            filename = f"{self.image_dir}/{product_id}.{file_extension}"
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        except Exception as e:
            logger.error(f"下載圖片時發生錯誤: {e}")
            return None

    def _extract_product_data(self, product):
        """
        從商品資料中提取所需資訊
        """
        try:
            remaining_stock = product.get('StockQty', 0) - product.get('SoldQty', 0)
            price_range = product.get('PriceRange', [0])
            
            return {
                '商品ID': product.get('ProdId', ''),
                '商品名稱': product.get('ProdName', ''),
                '賣家ID': product.get('SellerId', ''),
                '價格': int(price_range[0]),
                '剩餘數量': remaining_stock,
                '最低運費': int(product.get('ShippingCost', 0)),
                '上架時間': product.get('PostTime', '')
            }
        except Exception as e:
            logger.error(f"處理商品資料時發生錯誤: {e}")
            return None

    def process_products(self, keyword, max_items=ITEMS_PER_PAGE):
        """
        處理商品資料並儲存
        max_items: 想要爬取的商品數量
        """
        all_products = []
        items_collected = 0
        page = 1
        actual_max_items = max_items  # 實際可爬取的最大數量
        
        while items_collected < actual_max_items:
            retry_count = 0
            while retry_count < MAX_RETRIES:
                try:
                    # 計算這一頁需要抓取的商品數量
                    items_remaining = actual_max_items - items_collected
                    items_to_fetch = min(ITEMS_PER_PAGE, items_remaining)
                    
                    offset = (page - 1) * ITEMS_PER_PAGE + 1
                    logger.info(f"正在處理第 {page} 頁，預計抓取 {items_to_fetch} 個商品")
                    
                    # 搜尋商品
                    search_result, available_items = self.search_products(keyword, limit=items_to_fetch, offset=offset)
                    if not search_result or 'Rows' not in search_result:
                        logger.warning(f"第 {page} 頁沒有找到商品，嘗試重試...")
                        retry_count += 1
                        time.sleep(DEFAULT_RETRY_DELAY)
                        continue
                    
                    # 如果是第一頁，檢查並調整實際可爬取的最大數量
                    if page == 1:
                        actual_max_items = min(max_items, available_items)
                        logger.info(f"實際可爬取的商品數量：{actual_max_items}")
                    
                    # 獲取商品ID列表
                    product_ids = [row['Id'] for row in search_result['Rows']]
                    
                    # 獲取商品詳情
                    product_details = self.get_product_details(product_ids)
                    if not product_details:
                        logger.warning(f"無法獲取第 {page} 頁商品詳情，嘗試重試...")
                        retry_count += 1
                        time.sleep(DEFAULT_RETRY_DELAY)
                        continue
                    
                    # 處理每個商品
                    for product in product_details:
                        if items_collected >= actual_max_items:
                            break
                            
                        product_data = self._extract_product_data(product)
                        if product_data:
                            all_products.append(product_data)
                            items_collected += 1
                    
                    break  # 如果成功處理完這一頁，跳出重試循環
                    
                except Exception as e:
                    logger.error(f"處理第 {page} 頁時發生錯誤: {e}")
                    retry_count += 1
                    time.sleep(DEFAULT_RETRY_DELAY)
            
            if retry_count >= MAX_RETRIES:
                logger.error(f"第 {page} 頁處理失敗，跳過此頁")
            
            page += 1
            time.sleep(DEFAULT_RETRY_DELAY)
        
        return all_products

    def save_data(self, data, filename=None):
        """
        儲存爬取的資料
        """
        if not filename:
            filename = f"ruten_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # 確保檔案副檔名為 .csv
        if not filename.lower().endswith('.csv'):
            filename += '.csv'
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"資料已成功儲存到 {filename}")
        except Exception as e:
            logger.error(f"儲存資料時發生錯誤: {e}")

def get_user_input():
    """
    獲取使用者輸入的參數
    """
    print("\n=== 露天拍賣商品爬蟲 ===")
    print("請輸入以下資訊：")
    
    while True:
        keyword = input("\n請輸入搜尋關鍵字：").strip()
        if keyword:
            break
        print("關鍵字不能為空，請重新輸入！")
    
    while True:
        try:
            number = input("請輸入要爬取的商品數量（預設50）：").strip()
            if not number:
                number = 50
                break
            number = int(number)
            if number > 0:
                break
            print("數量必須大於0，請重新輸入！")
        except ValueError:
            print("請輸入有效的數字！")
    
    output = input("請輸入輸出檔案名稱（選填，直接按Enter使用預設名稱）：").strip()
    
    return keyword, number, output if output else None

def main():
    # 檢查是否有命令列參數
    if len(sys.argv) > 1:
        # 使用命令列參數
        parser = argparse.ArgumentParser(description='露天拍賣商品爬蟲')
        parser.add_argument('-k', '--keyword', type=str, required=True, help='搜尋關鍵字')
        parser.add_argument('-n', '--number', type=int, default=50, help='要爬取的商品數量（預設：50）')
        parser.add_argument('-o', '--output', type=str, help='輸出檔案名稱（選填）')
        
        args = parser.parse_args()
        keyword, number, output = args.keyword, args.number, args.output
    else:
        # 使用互動式介面
        keyword, number, output = get_user_input()
    
    # 初始化爬蟲
    scraper = RutenScraper()
    
    # 執行爬蟲
    print(f"\n開始搜尋關鍵字：{keyword}")
    print(f"預計爬取商品數量：{number}")
    products = scraper.process_products(keyword, max_items=number)
    
    # 儲存資料
    if output:
        output_file = output
    else:
        output_file = f"ruten_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    scraper.save_data(products, output_file)
    print(f"\n爬蟲完成！資料已儲存至：{output_file}")

if __name__ == "__main__":
    main() 