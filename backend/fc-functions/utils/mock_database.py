"""
BrandKin AI - Mock Database for Local Development
File-based persistent storage when MySQL is not available
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class MockDatabase:
    """File-based mock database for local testing with persistence."""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'local_storage')
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_file = os.path.join(self.data_dir, 'mock_database.json')
        
        self.projects: Dict[str, Dict] = {}
        self.assets: Dict[str, List[Dict]] = {}
        self.generations: Dict[str, List[Dict]] = {}
        self.code_exports: Dict[str, List[Dict]] = {}
        self.brand_kits: Dict[str, List[Dict]] = {}
        
        self._load()
    
    def _load(self):
        """Load data from file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.projects = data.get('projects', {})
                    self.assets = data.get('assets', {})
                    self.generations = data.get('generations', {})
                    self.code_exports = data.get('code_exports', {})
                    self.brand_kits = data.get('brand_kits', {})
            except Exception as e:
                print(f"Failed to load mock database: {e}")
    
    def _save(self):
        """Save data to file."""
        try:
            # Convert datetime objects to strings for JSON serialization
            data = {
                'projects': {},
                'assets': self.assets,
                'generations': self.generations,
                'code_exports': self.code_exports,
                'brand_kits': self.brand_kits
            }
            
            for pid, project in self.projects.items():
                proj_copy = project.copy()
                for key in ['created_at', 'updated_at', 'completed_at']:
                    if proj_copy.get(key) and hasattr(proj_copy[key], 'isoformat'):
                        proj_copy[key] = proj_copy[key].isoformat()
                data['projects'][pid] = proj_copy
            
            with open(self.db_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save mock database: {e}")
    
    def create_project(self, project_id: str, brand_brief: Dict) -> bool:
        """Create a new project."""
        self.projects[project_id] = {
            'project_id': project_id,
            'brand_brief': brand_brief,
            'status': 'initialized',
            'current_stage': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'completed_at': None,
            'error_message': None
        }
        self.assets[project_id] = []
        self.generations[project_id] = []
        self.code_exports[project_id] = []
        self.brand_kits[project_id] = []
        self._save()
        return True
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID."""
        project = self.projects.get(project_id)
        if project:
            result = project.copy()
            result['brand_brief'] = project['brand_brief']
            return result
        return None
    
    def update_project_status(self, project_id: str, status: str, stage: int = None, error: str = None):
        """Update project status and stage."""
        if project_id in self.projects:
            self.projects[project_id]['status'] = status
            if stage is not None:
                self.projects[project_id]['current_stage'] = stage
            if error:
                self.projects[project_id]['error_message'] = error
            self.projects[project_id]['updated_at'] = datetime.now()
            self._save()
    
    def create_asset(self, asset_id: str, project_id: str, asset_type: str, stage: int, metadata: Dict = None):
        """Create a new asset record."""
        if project_id not in self.assets:
            self.assets[project_id] = []
        self.assets[project_id].append({
            'asset_id': asset_id,
            'project_id': project_id,
            'asset_type': asset_type,
            'stage': stage,
            'oss_url': None,
            'transparent_url': None,
            'metadata': metadata or {},
            'is_selected': False,
            'created_at': datetime.now().isoformat()
        })
        self._save()
    
    def update_asset_urls(self, asset_id: str, oss_url: str = None, transparent_url: str = None):
        """Update asset URLs after generation."""
        for project_assets in self.assets.values():
            for asset in project_assets:
                if asset['asset_id'] == asset_id:
                    if oss_url:
                        asset['oss_url'] = oss_url
                    if transparent_url:
                        asset['transparent_url'] = transparent_url
                    self._save()
                    return
    
    def select_asset(self, asset_id: str):
        """Mark asset as selected by user."""
        for project_assets in self.assets.values():
            for asset in project_assets:
                if asset['asset_id'] == asset_id:
                    asset['is_selected'] = True
                    self._save()
                    return
    
    def get_project_assets(self, project_id: str, asset_type: str = None) -> List[Dict]:
        """Get all assets for a project."""
        assets = self.assets.get(project_id, [])
        if asset_type:
            return [a for a in assets if a['asset_type'] == asset_type]
        return assets
    
    def create_generation(self, generation_id: str, project_id: str, stage: int, input_params: Dict):
        """Create a generation tracking record."""
        if project_id not in self.generations:
            self.generations[project_id] = []
        self.generations[project_id].append({
            'generation_id': generation_id,
            'project_id': project_id,
            'stage': stage,
            'status': 'processing',
            'retry_count': 0,
            'input_params': input_params,
            'output_result': None,
            'error_message': None,
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        })
        self._save()
    
    def complete_generation(self, generation_id: str, output_result: Dict = None, error: str = None):
        """Mark generation as completed or failed."""
        for project_generations in self.generations.values():
            for gen in project_generations:
                if gen['generation_id'] == generation_id:
                    if error:
                        gen['status'] = 'failed'
                        gen['error_message'] = error
                    else:
                        gen['status'] = 'completed'
                        gen['output_result'] = output_result
                    gen['completed_at'] = datetime.now().isoformat()
                    self._save()
                    return
    
    def save_code_export(self, export_id: str, project_id: str, component_data: Dict):
        """Save generated React component."""
        if project_id not in self.code_exports:
            self.code_exports[project_id] = []
        self.code_exports[project_id].append({
            'export_id': export_id,
            'project_id': project_id,
            'component_name': component_data.get('component_name'),
            'react_code': component_data.get('react_code'),
            'css_keyframes': component_data.get('css_keyframes'),
            'usage_snippet': component_data.get('usage_snippet'),
            'created_at': datetime.now().isoformat()
        })
        self._save()
    
    def get_code_exports(self, project_id: str) -> List[Dict]:
        """Get all code exports for a project."""
        return self.code_exports.get(project_id, [])
    
    def save_brand_kit(self, kit_id: str, project_id: str, zip_url: str, signed_url: str, expires_at: datetime):
        """Save brand kit assembly info."""
        if project_id not in self.brand_kits:
            self.brand_kits[project_id] = []
        self.brand_kits[project_id].append({
            'kit_id': kit_id,
            'project_id': project_id,
            'zip_url': zip_url,
            'signed_url': signed_url,
            'url_expires_at': expires_at.isoformat() if hasattr(expires_at, 'isoformat') else expires_at,
            'download_count': 0,
            'created_at': datetime.now().isoformat()
        })
        self._save()
    
    def get_brand_kit(self, project_id: str) -> Optional[Dict]:
        """Get brand kit for a project."""
        kits = self.brand_kits.get(project_id, [])
        return kits[-1] if kits else None


# Singleton instance
mock_db = MockDatabase()
