import os
import sys
import subprocess
import file_genarator # 引用剛剛寫好的檔案產生器
from typing import Optional

class MainController:
    def __init__(self):
        # 專案路徑一開始是空的，等初始化後會有值
        self.project_path: Optional[str] = None
        # 準備好檔案產生工具
        self.file_gen = file_genarator.FileGenerator()

    def initialize_project(self) -> str:
        """
        步驟 1: 初始化
        建立這一次任務專用的資料夾環境。
        """
        print("正在初始化新專案環境...")
        self.project_path = self.file_gen.create_project_environment()
        print(f"專案環境已準備就緒: {self.project_path}")
        return self.project_path

    def wait_for_user_input(self):
        """
        步驟 2: 等待使用者
        在這個階段，程式會暫停（或是模擬暫停），讓使用者有機會去編輯 cart.json。
        在未來的 GUI 版本中，這裡會是一個「等待按鈕按下」的事件。
        """
        if not self.project_path:
            raise ValueError("錯誤：專案尚未初始化，請先執行 initialize_project()。")
        
        cart_path = os.path.join(self.project_path, "cart.json")
        print(f"\n[系統等待中]")
        print(f"請確認購物車設定檔內容正確: {cart_path}")
        print("由於這是自動化流程，系統將假設您已設定完成，繼續執行下一步...")
        return True

    def run_scraper(self):
        """
        步驟 3: 執行爬蟲 (Scraper)
        讀取: cart.json (購物清單)
        產出: ruten_data.csv (原始商品資料)
        """
        if not self.project_path:
            raise ValueError("錯誤：專案尚未初始化。")

        # 設定輸入與輸出的檔案路徑
        cart_path = os.path.join(self.project_path, "cart.json")
        output_csv = os.path.join(self.project_path, "ruten_data.csv")
        
        print(f"\n[啟動爬蟲模組]...")
        # 呼叫 scraper.py 並傳入參數
        cmd = [sys.executable, "scraper.py", "--cart", cart_path, "--output", output_csv]
        subprocess.check_call(cmd)
        print("爬蟲任務完成。")

    def run_cleaner(self):
        """
        步驟 4: 執行清理 (Cleaner)
        讀取: ruten_data.csv (原始資料)
        產出: cleaned_ruten_data.csv (乾淨的資料)
        """
        if not self.project_path:
            raise ValueError("錯誤：專案尚未初始化。")

        input_csv = os.path.join(self.project_path, "ruten_data.csv")
        output_csv = os.path.join(self.project_path, "cleaned_ruten_data.csv")
        cart_path = os.path.join(self.project_path, "cart.json") # 需要讀取裡面的黑名單設定

        print(f"\n[啟動資料清理模組]...")
        # 呼叫 clean_csv.py 並傳入參數
        cmd = [sys.executable, "clean_csv.py", "--input", input_csv, "--output", output_csv, "--cart", cart_path]
        subprocess.check_call(cmd)
        print("資料清理完成。")

    def run_calculator(self):
        """
        步驟 5: 執行計算 (Calculator)
        讀取: cleaned_ruten_data.csv (乾淨資料)
        產出: caculate.log (計算過程), plan.json (最終購買方案)
        """
        if not self.project_path:
            raise ValueError("錯誤：專案尚未初始化。")

        input_csv = os.path.join(self.project_path, "cleaned_ruten_data.csv")
        cart_path = os.path.join(self.project_path, "cart.json")
        output_log = os.path.join(self.project_path, "caculate.log")
        output_json = os.path.join(self.project_path, "plan.json")

        print(f"\n[啟動最佳化計算模組]...")
        # 呼叫 caculator.py 並傳入參數
        cmd = [
            sys.executable, "caculator.py", 
            "--cart", cart_path, 
            "--input_csv", input_csv, 
            "--output_log", output_log,
            "--output_json", output_json
        ]
        subprocess.check_call(cmd)
        print("計算完成。")
        print(f"最佳購買方案已儲存於: {output_json}")

    def execute_workflow(self):
        """
        執行完整的工作流程 (Workflow)
        依照 README.md 設計的順序執行。
        """
        try:
            # 1. 建立檔案與環境
            self.initialize_project()
            
            # 2. 等待使用者輸入
            self.wait_for_user_input()
            
            # 3. 執行爬蟲
            self.run_scraper()
            
            # 4. 執行清理
            self.run_cleaner()
            
            # 5. 執行計算
            self.run_calculator()
            
            print("\n所有工作流程執行成功！")
            return self.project_path
            
        except Exception as e:
            print(f"\n工作流程發生錯誤: {e}")
            return None

# 這是給未來 GUI 程式呼叫的接口
def start_process():
    controller = MainController()
    return controller.execute_workflow()

if __name__ == "__main__":
    # 如果直接執行此檔案，就開始跑流程
    start_process()