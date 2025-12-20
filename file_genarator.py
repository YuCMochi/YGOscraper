import os
import json
import datetime
import shutil

class FileGenerator:
    def __init__(self, base_dir='data'):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def create_project_environment(self) -> str:
        """
        Creates a new timestamped directory in the base_dir and initializes a blank cart.json.
        Returns the absolute path to the newly created project directory.
        """
        # Create timestamped directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_path = os.path.join(self.base_dir, timestamp)
        os.makedirs(project_path, exist_ok=True)
        print(f"Created project directory: {project_path}")

        # Create blank cart.json
        cart_path = os.path.join(project_path, "cart.json")
        
        # Check if there is a default cart.json in data/ to use as template
        template_cart_path = os.path.join(self.base_dir, "cart.json")
        
        if os.path.exists(template_cart_path):
            shutil.copy(template_cart_path, cart_path)
            print(f"Copied template cart.json to {cart_path}")
        else:
            # Create a default empty structure if no template exists
            default_cart_structure = {
                "global_settings": {
                    "default_shipping_cost": 60,
                    "min_purchase_limit": 0,
                    "global_exclude_keywords": [],
                    "global_exclude_seller": []
                },
                "shopping_cart": []
            }
            with open(cart_path, 'w', encoding='utf-8') as f:
                json.dump(default_cart_structure, f, ensure_ascii=False, indent=4)
            print(f"Created new blank cart.json at {cart_path}")

        return os.path.abspath(project_path)

if __name__ == "__main__":
    generator = FileGenerator()
    new_project_dir = generator.create_project_environment()
    print(f"New project initialized at: {new_project_dir}")
