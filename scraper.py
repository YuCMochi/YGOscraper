import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import json
import time
from fake_useragent import UserAgent
import os

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RutenScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.base_url = "https://rtapi.ruten.com.tw/api"
        self.image_base_url = "https://gcs.rimg.com.tw"
        
        # 建立圖片儲存目錄
        self.image_dir = "product_images"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

    def _get_headers(self):
        """生成隨機的 User-Agent"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'application/json',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.ruten.com.tw/'
        }

    def search_products(self, keyword, limit=110, offset=1):
        """
        搜尋商品並獲取商品ID
        """
        url = f"{self.base_url}/search/v3/index.php/core/prod"
        params = {
            'q': keyword,
            'type': 'direct',
            'sort': 'rnk/dc',
            'limit': limit,
            'offset': offset
        }
        
        try:
            response = self.session.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"搜尋商品時發生錯誤: {e}")
            return None

    def get_product_details(self, product_ids):
        """
        獲取商品詳細資訊
        """
        if isinstance(product_ids, list):
            product_ids = ','.join(product_ids)
            
        url = f"{self.base_url}/prod/v2/index.php/prod"
        params = {'id': product_ids}
        
        try:
            response = self.session.get(url, params=params, headers=self._get_headers())
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
            
        full_url = f"{self.image_base_url}{image_path}"
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

    def process_products(self, keyword, max_items=110):
        """
        處理商品資料並儲存
        max_items: 想要爬取的商品數量
        """
        all_products = []
        items_collected = 0
        page = 1
        
        while items_collected < max_items:
            # 計算這一頁需要抓取的商品數量
            items_remaining = max_items - items_collected
            items_to_fetch = min(110, items_remaining)  # 每頁最多110個商品
            
            offset = (page - 1) * 110 + 1
            logger.info(f"正在處理第 {page} 頁，預計抓取 {items_to_fetch} 個商品")
            
            # 搜尋商品
            search_result = self.search_products(keyword, limit=items_to_fetch, offset=offset)
            if not search_result or 'Rows' not in search_result:
                break
                
            # 獲取商品ID列表
            product_ids = [row['Id'] for row in search_result['Rows']]
            
            # 獲取商品詳情
            product_details = self.get_product_details(product_ids)
            if not product_details:
                continue
                
            # 處理每個商品
            for product in product_details:
                if items_collected >= max_items:
                    break
                    
                try:
                    # 計算實際剩餘數量 = 庫存量 - 已售出數量
                    remaining_stock = product['StockQty'] - product['SoldQty']
                    
                    product_data = {
                        '商品ID': product['ProdId'],
                        '商品名稱': product['ProdName'],
                        '賣家ID': product['SellerId'],
                        '價格': int(product['PriceRange'][0]),
                        '剩餘數量': remaining_stock,
                        '最低運費': int(product['ShippingCost']),
                        '上架時間': product['PostTime']
                    }
                    all_products.append(product_data)
                    items_collected += 1
                    
                except Exception as e:
                    logger.error(f"處理商品 {product.get('ProdId')} 時發生錯誤: {e}")
            
            page += 1
            # 加入延遲避免請求過快
            time.sleep(2)
        
        return all_products

    def save_data(self, data, filename=None):
        """
        儲存爬取的資料
        """
        if not filename:
            filename = f"ruten_products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"資料已成功儲存到 {filename}")
        except Exception as e:
            logger.error(f"儲存資料時發生錯誤: {e}")

def main():
    scraper = RutenScraper()
    keyword = "黃金卿"  # 可以根據需求修改關鍵字
    products = scraper.process_products(keyword, max_items=50)  # 設定要爬取的商品數量
    scraper.save_data(products)

if __name__ == "__main__":
    main() 