import os
import sys

# Add backend directory to path
sys.path.append(os.path.abspath('backend'))

from utils.database import db

def test_db():
    print("Initializing Database test...")
    
    # 1. Create a project
    pid = "test_project_123"
    db.create_project(pid, {"brand_name": "Test Brand"})
    print("Project created.")
    
    # 2. Get the project
    proj = db.get_project(pid)
    print(f"Retrieved Project: {proj}")
    
    # 3. Create an asset
    db.create_asset("asset_img_1", pid, "mascot", 2, {"prompt": "yellow duck"})
    print("Asset created.")
    
    # 4. Get assets
    assets = db.get_project_assets(pid)
    print(f"Retrieved Assets: {assets}")
    
    # 5. Update asset URL
    db.update_asset_urls("asset_img_1", "https://oss-url.com/img.png")
    
    assets_updated = db.get_project_assets(pid)
    print(f"Updated Assets: {assets_updated}")

if __name__ == "__main__":
    test_db()
