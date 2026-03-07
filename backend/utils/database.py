"""
BrandKin AI - OSS Database Models
Serverless JSON Document Store using Alibaba Cloud OSS for project state tracking.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path

# Important: we import the unified OSS/Local handler which transparently handles local dev vs FC
from .oss_handler import oss_handler

logger = logging.getLogger(__name__)

class Database:
    """OSS JSON Document manager for BrandKin AI.
    
    Replaces RDS MySQL with simple JSON files stored under the `db/` prefix in your OSS bucket.
    This saves costs and runs entirely serverless.
    """
    
    def __init__(self):
        # Database prefix in OSS bucket to separate database files from assets
        self.prefix = "db"
    
    def _now(self) -> str:
        """Helper to get current ISO timestamp string."""
        return datetime.now(timezone.utc).isoformat()
    
    def _get_doc(self, key: str) -> Optional[Dict]:
        """Fetch and parse a JSON document from OSS."""
        oss_key = f"{self.prefix}/{key}"
        try:
            if oss_handler.object_exists(oss_key):
                data_bytes = oss_handler.download_to_memory(oss_key)
                return json.loads(data_bytes.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"Error reading document {oss_key}: {e}")
            return None

    def _save_doc(self, key: str, data: Dict):
        """Stringify and save a JSON document to OSS."""
        oss_key = f"{self.prefix}/{key}"
        json_bytes = json.dumps(data, default=str).encode('utf-8')
        oss_handler.upload_data(json_bytes, oss_key)

    def init_schema(self):
        """No-op for OSS Database. Schemas are implicit JSON structures."""
        logger.info("OSS JSON Database initialized. No rigid schema required.")
        pass

    # Project operations
    def create_project(self, project_id: str, brand_brief: Dict) -> bool:
        """Create a new project document."""
        doc = {
            "project_id": project_id,
            "brand_brief": brand_brief,
            "status": "initialized",
            "current_stage": 0,
            "created_at": self._now(),
            "updated_at": self._now(),
            "completed_at": None,
            "error_message": None
        }
        self._save_doc(f"projects/{project_id}/state.json", doc)
        return True

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project state by ID."""
        return self._get_doc(f"projects/{project_id}/state.json")

    def update_project_status(self, project_id: str, status: str, stage: Optional[int] = None, error: Optional[str] = None):
        """Update project status and stage in its state file."""
        doc = self.get_project(project_id)
        if not doc:
            return
        
        doc["status"] = status
        doc["updated_at"] = self._now()
        
        if stage is not None:
            doc["current_stage"] = stage
        if error:
            doc["error_message"] = error
            
        if status == 'completed' and stage == 7:
            # Special logic for final assembly completion
            doc["completed_at"] = self._now()
            
        self._save_doc(f"projects/{project_id}/state.json", doc)

    # Asset operations
    def create_asset(self, asset_id: str, project_id: str, asset_type: str, stage: int, metadata: Optional[Dict] = None):
        """Create a new asset record within the project's assets list."""
        assets_key = f"projects/{project_id}/assets.json"
        assets_doc = self._get_doc(assets_key) or {"items": []}
        
        new_asset = {
            "asset_id": asset_id,
            "project_id": project_id,
            "asset_type": asset_type,
            "stage": stage,
            "oss_url": None,
            "transparent_url": None,
            "metadata": metadata,
            "is_selected": False,
            "created_at": self._now()
        }
        assets_doc["items"].append(new_asset)
        self._save_doc(assets_key, assets_doc)
        
        # Save index for fast lookups without scanning
        self._save_doc(f"index/assets/{asset_id}.json", {"project_id": project_id})

    def update_asset_urls(self, asset_id: str, oss_url: Optional[str] = None, transparent_url: Optional[str] = None):
        """Update URLs utilizing the asset index."""
        index_key = f"index/assets/{asset_id}.json"
        index = self._get_doc(index_key)
        
        if not index:
            # Fallback scan utilizing pathlib to handle cross-platform slashes
            all_project_dirs = oss_handler.list_objects(prefix=f"{self.prefix}/projects/")
            for p in all_project_dirs:
                # Replace Windows slashes for consistent splitting
                p_norm = str(p).replace('\\', '/')
                parts = p_norm.split('/')
                if len(parts) > 2:
                    pid = parts[2]
                    assets_doc = self._get_doc(f"projects/{pid}/assets.json")
                    if assets_doc:
                        for asset in assets_doc.get("items", []):
                            if asset["asset_id"] == asset_id:
                                self._update_asset_in_project(pid, asset_id, oss_url, transparent_url)
                                return
        else:
            self._update_asset_in_project(index["project_id"], asset_id, oss_url, transparent_url)

    def _update_asset_in_project(self, project_id: str, asset_id: str, oss_url: Optional[str], transparent_url: Optional[str]):
        assets_key = f"projects/{project_id}/assets.json"
        assets_doc = self._get_doc(assets_key)
        if assets_doc:
            for asset in assets_doc.get("items", []):
                if asset["asset_id"] == asset_id:
                    if oss_url:
                        asset["oss_url"] = oss_url
                    if transparent_url:
                        asset["transparent_url"] = transparent_url
            self._save_doc(assets_key, assets_doc)

    def select_asset(self, asset_id: str):
        """Mark asset as selected."""
        all_project_dirs = oss_handler.list_objects(prefix=f"{self.prefix}/projects/")
        for p in all_project_dirs:
            p_norm = str(p).replace('\\', '/')
            parts = p_norm.split('/')
            if len(parts) > 2:
                pid = parts[2]
                assets_key = f"projects/{pid}/assets.json"
                assets_doc = self._get_doc(assets_key)
                if assets_doc:
                    for asset in assets_doc.get("items", []):
                        if asset["asset_id"] == asset_id:
                            asset["is_selected"] = True
                            self._save_doc(assets_key, assets_doc)
                            return

    def get_project_assets(self, project_id: str, asset_type: Optional[str] = None) -> List[Dict]:
        """Get all assets for a project."""
        assets_doc = self._get_doc(f"projects/{project_id}/assets.json")
        if not assets_doc:
            return []
        
        items = assets_doc.get("items", [])
        if asset_type:
            items = [item for item in items if item.get("asset_type") == asset_type]
            
        items.sort(key=lambda x: x.get("created_at", ""))
        return items

    def create_generation(self, generation_id: str, project_id: str, stage: int, input_params: Dict):
        """Create a generation tracking record."""
        gens_key = f"projects/{project_id}/generations.json"
        gens_doc = self._get_doc(gens_key) or {"items": []}
        
        new_gen = {
            "generation_id": generation_id,
            "project_id": project_id,
            "stage": stage,
            "status": "processing",
            "retry_count": 0,
            "input_params": input_params,
            "output_result": None,
            "error_message": None,
            "started_at": self._now(),
            "completed_at": None
        }
        gens_doc["items"].append(new_gen)
        self._save_doc(gens_key, gens_doc)
        
        self._save_doc(f"index/generations/{generation_id}.json", {"project_id": project_id})

    def complete_generation(self, generation_id: str, output_result: Optional[Dict] = None, error: Optional[str] = None):
        """Mark generation as completed or failed."""
        index = self._get_doc(f"index/generations/{generation_id}.json")
        if not index:
            all_project_dirs = oss_handler.list_objects(prefix=f"{self.prefix}/projects/")
            project_ids = []
            for p in all_project_dirs:
                p_norm = str(p).replace('\\', '/')
                parts = p_norm.split('/')
                if len(parts) > 2:
                    project_ids.append(parts[2])
            project_ids = list(set(project_ids))
        else:
            project_ids = [index["project_id"]]
            
        for pid in project_ids:
            gens_key = f"projects/{pid}/generations.json"
            gens_doc = self._get_doc(gens_key)
            if gens_doc:
                for gen in gens_doc.get("items", []):
                    if gen["generation_id"] == generation_id:
                        gen["completed_at"] = self._now()
                        if error:
                            gen["status"] = "failed"
                            gen["error_message"] = error
                        else:
                            gen["status"] = "completed"
                            if output_result is not None:
                                gen["output_result"] = output_result
                        self._save_doc(gens_key, gens_doc)
                        return

    # Code export operations
    def save_code_export(self, export_id: str, project_id: str, component_data: Dict):
        """Save generated React component."""
        exports_key = f"projects/{project_id}/code_exports.json"
        exports_doc = self._get_doc(exports_key) or {"items": []}
        
        new_export = {
            "export_id": export_id,
            "project_id": project_id,
            "component_name": component_data.get('component_name'),
            "react_code": component_data.get('react_code'),
            "css_keyframes": component_data.get('css_keyframes'),
            "usage_snippet": component_data.get('usage_snippet'),
            "created_at": self._now()
        }
        exports_doc["items"].append(new_export)
        self._save_doc(exports_key, exports_doc)

    def get_code_exports(self, project_id: str) -> List[Dict]:
        """Get all code exports for a project."""
        exports_doc = self._get_doc(f"projects/{project_id}/code_exports.json")
        if not exports_doc:
            return []
        items = exports_doc.get("items", [])
        items.sort(key=lambda x: x.get("created_at", ""))
        return items

    # Brand kit operations
    def save_brand_kit(self, kit_id: str, project_id: str, zip_url: str, signed_url: str, expires_at: datetime):
        """Save brand kit assembly info."""
        doc = {
            "kit_id": kit_id,
            "project_id": project_id,
            "zip_url": zip_url,
            "signed_url": signed_url,
            "url_expires_at": expires_at.isoformat() if expires_at else None,
            "download_count": 0,
            "created_at": self._now()
        }
        self._save_doc(f"projects/{project_id}/brand_kit_{kit_id}.json", doc)

    def get_brand_kit(self, project_id: str) -> Optional[Dict]:
        """Get the latest brand kit for a project."""
        # Find all brand kits for this project
        kit_files = oss_handler.list_objects(prefix=f"{self.prefix}/projects/{project_id}/brand_kit_")
        if not kit_files:
            return None
            
        # Get latest by sorting string names (since created_at makes them monotonically increasing, or we just read all and sort)
        kits = []
        for file_key in kit_files:
            # Strip db/ prefix
            key = file_key[len(self.prefix)+1:]
            doc = self._get_doc(key)
            if doc:
                kits.append(doc)
                
        if not kits:
            return None
            
        kits.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return kits[0]

# Singleton instance
db = Database()
