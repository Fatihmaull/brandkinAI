"""
BrandKin AI - Database Models and Connection
RDS MySQL Schema for projects, assets, and generations
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager

# Try to import MySQL, fall back to mock if not available
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    from .credentials import get_rds_config
except ImportError:
    get_rds_config = None

# Import mock database for local development
from .mock_database import mock_db


class Database:
    """RDS MySQL connection manager with fallback to mock database."""
    
    def __init__(self):
        self.use_mock = os.getenv('USE_MOCK_DB', 'true').lower() == 'true' or not MYSQL_AVAILABLE
        if not self.use_mock and get_rds_config:
            self.config = get_rds_config()
        else:
            self.config = None
    
    def _should_use_mock(self):
        """Check if we should use mock database."""
        return self.use_mock
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = pymysql.connect(
            host=self.config['host'],
            port=self.config['port'],
            database=self.config['database'],
            user=self.config['user'],
            password=self.config['password'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_schema(self):
        """Initialize database schema. Run once during setup."""
        schema = """
        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            project_id VARCHAR(64) PRIMARY KEY,
            brand_brief JSON NOT NULL,
            status VARCHAR(32) DEFAULT 'initialized',
            current_stage INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL,
            error_message TEXT,
            INDEX idx_status (status),
            INDEX idx_created (created_at)
        );
        
        -- Assets table (mascots, avatars, poses)
        CREATE TABLE IF NOT EXISTS assets (
            asset_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            asset_type ENUM('mascot', 'avatar', 'pose', 'banner') NOT NULL,
            stage INT NOT NULL,
            oss_url VARCHAR(512),
            transparent_url VARCHAR(512),
            metadata JSON,
            is_selected BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            INDEX idx_project (project_id),
            INDEX idx_type (asset_type)
        );
        
        -- Generations tracking table
        CREATE TABLE IF NOT EXISTS generations (
            generation_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            stage INT NOT NULL,
            status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
            retry_count INT DEFAULT 0,
            input_params JSON,
            output_result JSON,
            error_message TEXT,
            started_at TIMESTAMP NULL,
            completed_at TIMESTAMP NULL,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            INDEX idx_project_stage (project_id, stage)
        );
        
        -- Code exports table
        CREATE TABLE IF NOT EXISTS code_exports (
            export_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            component_name VARCHAR(128),
            react_code TEXT,
            css_keyframes TEXT,
            usage_snippet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
        );
        
        -- Brand kit assembly tracking
        CREATE TABLE IF NOT EXISTS brand_kits (
            kit_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            zip_url VARCHAR(512),
            signed_url VARCHAR(512),
            url_expires_at TIMESTAMP NULL,
            download_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
        );
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                for statement in schema.split(';'):
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
    
    # Project operations
    def create_project(self, project_id: str, brand_brief: Dict) -> bool:
        """Create a new project."""
        if self._should_use_mock():
            return mock_db.create_project(project_id, brand_brief)
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO projects (project_id, brand_brief, status) VALUES (%s, %s, %s)",
                    (project_id, json.dumps(brand_brief), 'initialized')
                )
                return cursor.rowcount > 0
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID."""
        if self._should_use_mock():
            return mock_db.get_project(project_id)
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM projects WHERE project_id = %s",
                    (project_id,)
                )
                result = cursor.fetchone()
                if result and result.get('brand_brief'):
                    result['brand_brief'] = json.loads(result['brand_brief'])
                return result
    
    def update_project_status(self, project_id: str, status: str, stage: int = None, error: str = None):
        """Update project status and stage."""
        if self._should_use_mock():
            mock_db.update_project_status(project_id, status, stage, error)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if stage is not None and error:
                    cursor.execute(
                        "UPDATE projects SET status = %s, current_stage = %s, error_message = %s WHERE project_id = %s",
                        (status, stage, error, project_id)
                    )
                elif stage is not None:
                    cursor.execute(
                        "UPDATE projects SET status = %s, current_stage = %s WHERE project_id = %s",
                        (status, stage, project_id)
                    )
                elif error:
                    cursor.execute(
                        "UPDATE projects SET status = %s, error_message = %s WHERE project_id = %s",
                        (status, error, project_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE projects SET status = %s WHERE project_id = %s",
                        (status, project_id)
                    )
    
    # Asset operations
    def create_asset(self, asset_id: str, project_id: str, asset_type: str, stage: int, metadata: Dict = None):
        """Create a new asset record."""
        if self._should_use_mock():
            mock_db.create_asset(asset_id, project_id, asset_type, stage, metadata)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO assets (asset_id, project_id, asset_type, stage, metadata) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (asset_id, project_id, asset_type, stage, json.dumps(metadata) if metadata else None)
                )
    
    def update_asset_urls(self, asset_id: str, oss_url: str = None, transparent_url: str = None):
        """Update asset URLs after generation."""
        if self._should_use_mock():
            mock_db.update_asset_urls(asset_id, oss_url, transparent_url)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if oss_url and transparent_url:
                    cursor.execute(
                        "UPDATE assets SET oss_url = %s, transparent_url = %s WHERE asset_id = %s",
                        (oss_url, transparent_url, asset_id)
                    )
                elif oss_url:
                    cursor.execute(
                        "UPDATE assets SET oss_url = %s WHERE asset_id = %s",
                        (oss_url, asset_id)
                    )
                elif transparent_url:
                    cursor.execute(
                        "UPDATE assets SET transparent_url = %s WHERE asset_id = %s",
                        (transparent_url, asset_id)
                    )
    
    def select_asset(self, asset_id: str):
        """Mark asset as selected by user."""
        if self._should_use_mock():
            mock_db.select_asset(asset_id)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE assets SET is_selected = TRUE WHERE asset_id = %s",
                    (asset_id,)
                )
    
    def get_project_assets(self, project_id: str, asset_type: str = None) -> List[Dict]:
        """Get all assets for a project."""
        if self._should_use_mock():
            return mock_db.get_project_assets(project_id, asset_type)
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if asset_type:
                    cursor.execute(
                        "SELECT * FROM assets WHERE project_id = %s AND asset_type = %s ORDER BY created_at",
                        (project_id, asset_type)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM assets WHERE project_id = %s ORDER BY created_at",
                        (project_id,)
                    )
                results = cursor.fetchall()
                for r in results:
                    if r.get('metadata'):
                        r['metadata'] = json.loads(r['metadata'])
                return results
    
    # Generation tracking
    def create_generation(self, generation_id: str, project_id: str, stage: int, input_params: Dict):
        """Create a generation tracking record."""
        if self._should_use_mock():
            mock_db.create_generation(generation_id, project_id, stage, input_params)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO generations (generation_id, project_id, stage, status, input_params, started_at) 
                       VALUES (%s, %s, %s, %s, %s, NOW())""",
                    (generation_id, project_id, stage, 'processing', json.dumps(input_params))
                )
    
    def complete_generation(self, generation_id: str, output_result: Dict = None, error: str = None):
        """Mark generation as completed or failed."""
        if self._should_use_mock():
            mock_db.complete_generation(generation_id, output_result, error)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if error:
                    cursor.execute(
                        """UPDATE generations 
                           SET status = 'failed', error_message = %s, completed_at = NOW() 
                           WHERE generation_id = %s""",
                        (error, generation_id)
                    )
                else:
                    cursor.execute(
                        """UPDATE generations 
                           SET status = 'completed', output_result = %s, completed_at = NOW() 
                           WHERE generation_id = %s""",
                        (json.dumps(output_result) if output_result else None, generation_id)
                    )
    
    # Code export operations
    def save_code_export(self, export_id: str, project_id: str, component_data: Dict):
        """Save generated React component."""
        if self._should_use_mock():
            mock_db.save_code_export(export_id, project_id, component_data)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO code_exports 
                       (export_id, project_id, component_name, react_code, css_keyframes, usage_snippet) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        export_id, project_id,
                        component_data.get('component_name'),
                        component_data.get('react_code'),
                        component_data.get('css_keyframes'),
                        component_data.get('usage_snippet')
                    )
                )
    
    def get_code_exports(self, project_id: str) -> List[Dict]:
        """Get all code exports for a project."""
        if self._should_use_mock():
            return mock_db.get_code_exports(project_id)
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM code_exports WHERE project_id = %s ORDER BY created_at",
                    (project_id,)
                )
                return cursor.fetchall()
    
    # Brand kit operations
    def save_brand_kit(self, kit_id: str, project_id: str, zip_url: str, signed_url: str, expires_at: datetime):
        """Save brand kit assembly info."""
        if self._should_use_mock():
            mock_db.save_brand_kit(kit_id, project_id, zip_url, signed_url, expires_at)
            return
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO brand_kits 
                       (kit_id, project_id, zip_url, signed_url, url_expires_at) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (kit_id, project_id, zip_url, signed_url, expires_at)
                )
    
    def get_brand_kit(self, project_id: str) -> Optional[Dict]:
        """Get brand kit for a project."""
        if self._should_use_mock():
            return mock_db.get_brand_kit(project_id)
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM brand_kits WHERE project_id = %s ORDER BY created_at DESC LIMIT 1",
                    (project_id,)
                )
                return cursor.fetchone()


# Singleton instance
db = Database()
