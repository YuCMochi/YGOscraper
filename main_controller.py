import os
import sys
import subprocess
import file_genarator # sic: matching the filename requested
from typing import Optional

class MainController:
    def __init__(self):
        self.project_path: Optional[str] = None
        self.file_gen = file_genarator.FileGenerator()

    def initialize_project(self) -> str:
        """
        Step 1: Create new project environment.
        Returns the path to the project folder.
        """
        print("Initializing new project...")
        self.project_path = self.file_gen.create_project_environment()
        print(f"Project initialized at: {self.project_path}")
        return self.project_path

    def wait_for_user_input(self):
        """
        Step 2: Simulate waiting for user/GUI to update cart.json.
        In a real GUI app, this would be an event or callback.
        For CLI, we just prompt the user.
        """
        if not self.project_path:
            raise ValueError("Project not initialized. Call initialize_project() first.")
        
        cart_path = os.path.join(self.project_path, "cart.json")
        print(f"\nREADY for user input.")
        print(f"Please update the shopping cart at: {cart_path}")
        print("Since this is an automated process, assuming cart.json is ready (copied from template).")
        # In a real scenario, we might wait for a signal here.
        return True

    def run_scraper(self):
        """
        Step 3: Run scraper.py
        Input: cart.json
        Output: ruten_data.csv
        """
        if not self.project_path:
            raise ValueError("Project not initialized.")

        cart_path = os.path.join(self.project_path, "cart.json")
        output_csv = os.path.join(self.project_path, "ruten_data.csv")
        
        print(f"\nRunning Scraper...")
        # Using subprocess to run the script as a separate process, mocking the 'MainController -> Scraper' call
        cmd = [sys.executable, "scraper.py", "--cart", cart_path, "--output", output_csv]
        subprocess.check_call(cmd)
        print("Scraper finished.")

    def run_cleaner(self):
        """
        Step 4: Run clean_csv.py
        Input: ruten_data.csv
        Output: cleaned_ruten_data.csv
        """
        if not self.project_path:
            raise ValueError("Project not initialized.")

        input_csv = os.path.join(self.project_path, "ruten_data.csv")
        output_csv = os.path.join(self.project_path, "cleaned_ruten_data.csv")
        cart_path = os.path.join(self.project_path, "cart.json") # Needed for blacklist settings

        print(f"\nRunning Cleaner...")
        cmd = [sys.executable, "clean_csv.py", "--input", input_csv, "--output", output_csv, "--cart", cart_path]
        subprocess.check_call(cmd)
        print("Cleaner finished.")

    def run_calculator(self):
        """
        Step 5: Run caculator.py
        Input: cleaned_ruten_data.csv
        Output: caculate.log, plan.json
        """
        if not self.project_path:
            raise ValueError("Project not initialized.")

        input_csv = os.path.join(self.project_path, "cleaned_ruten_data.csv")
        cart_path = os.path.join(self.project_path, "cart.json")
        output_log = os.path.join(self.project_path, "caculate.log")
        output_json = os.path.join(self.project_path, "plan.json")

        print(f"\nRunning Calculator...")
        cmd = [
            sys.executable, "caculator.py", 
            "--cart", cart_path, 
            "--input_csv", input_csv, 
            "--output_log", output_log,
            "--output_json", output_json
        ]
        subprocess.check_call(cmd)
        print("Calculator finished.")
        print(f"Final Plan saved to: {output_json}")

    def execute_workflow(self):
        """Executes the full workflow defined in README.md"""
        try:
            # 1. Create Files
            self.initialize_project()
            
            # 2. Wait for Input (Simulated)
            self.wait_for_user_input()
            
            # 3. Scraper
            self.run_scraper()
            
            # 4. Cleaner
            self.run_cleaner()
            
            # 5. Calculator
            self.run_calculator()
            
            print("\nWorkflow completed successfully.")
            return self.project_path
            
        except Exception as e:
            print(f"\nWorkflow failed: {e}")
            return None

# Interface for GUI integration
def start_process():
    controller = MainController()
    return controller.execute_workflow()

if __name__ == "__main__":
    start_process()
