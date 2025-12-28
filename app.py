import eel
import os
import json
import sys
import subprocess
import time
from file_genarator import FileGenerator

# Initialize Eel with the web directory
eel.init('web')

@eel.expose
def get_project_list():
    """Returns a list of project names."""
    if not os.path.exists("data"):
        return []
    projects = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
    projects.sort(reverse=True)
    return projects

@eel.expose
def create_new_project():
    """Creates a new project and returns its path."""
    try:
        fg = FileGenerator()
        new_path = fg.create_project_environment()
        return new_path
    except Exception as e:
        print(f"Error creating project: {e}")
        return None

@eel.expose
def load_project(project_name):
    """Returns the full path of a project given its name."""
    path = os.path.abspath(os.path.join("data", project_name))
    if os.path.exists(path):
        return path
    return None

@eel.expose
def read_cart_json(project_path):
    """Reads cart.json from the project path."""
    cart_path = os.path.join(project_path, "cart.json")
    if os.path.exists(cart_path):
        try:
            with open(cart_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e), "shopping_cart": [], "global_settings": {}}
    return {"shopping_cart": [], "global_settings": {}}

@eel.expose
def save_cart_json(project_path, cart_data):
    """Saves cart.json to the project path."""
    cart_path = os.path.join(project_path, "cart.json")
    try:
        with open(cart_path, 'w', encoding='utf-8') as f:
            json.dump(cart_data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving cart: {e}")
        return False

@eel.expose
def run_full_process(project_path):
    """Runs the scraper, cleaner, and calculator."""
    
    def log(msg):
        print(msg)
        eel.appendLog(msg) # Call JS function

    cart_path = os.path.join(project_path, "cart.json")
    csv_path = os.path.join(project_path, "ruten_data.csv")
    clean_csv_path = os.path.join(project_path, "cleaned_ruten_data.csv")
    log_path = os.path.join(project_path, "caculate.log")
    plan_path = os.path.join(project_path, "plan.json")

    commands = [
        (
            [sys.executable, "scraper.py", "--cart", cart_path, "--output", csv_path],
            "正在執行: 爬蟲模組..."
        ),
        (
            [sys.executable, "clean_csv.py", "--input", csv_path, "--output", clean_csv_path, "--cart", cart_path],
            "正在執行: 資料清理..."
        ),
        (
            [sys.executable, "caculator.py", "--cart", cart_path, "--input_csv", clean_csv_path, "--output_log", log_path, "--output_json", plan_path],
            "正在執行: 最佳化計算..."
        )
    ]

    for cmd, desc in commands:
        log(f"--- {desc} ---")
        try:
            process = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Real-time output streaming
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    log(output.strip())
            
            rc = process.poll()
            if rc != 0:
                err = process.stderr.read()
                log(f"錯誤: {err}")
                log("流程終止。")
                return False
                
        except Exception as e:
            log(f"執行例外: {e}")
            return False
            
    log("✅ 所有步驟執行完成！請查看結果分頁。")
    return True

@eel.expose
def get_results(project_path):
    """Reads plan.json and returns it."""
    plan_path = os.path.join(project_path, "plan.json")
    if os.path.exists(plan_path):
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"error": "Invalid JSON"}
    return {"error": "Not found"}

if __name__ == '__main__':
    # Start the application
    try:
        eel.start('index.html', size=(1200, 800))
    except (SystemExit, MemoryError, KeyboardInterrupt):
        # We handle these to allow clean exit
        pass
