"""
BrandKin AI - Database Models and Connection
RDS MySQL Schema for projects, assets, and generations
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from contextlib import contextmanager

import pymysql
import threading

from .credentials import get_rds_config

logger = logging.getLogger(__name__)


class Database:
    """RDS MySQL connection manager for BrandKin AI.
    
    Uses threading.local() so each thread gets its own connection.
    This is critical for thread safety when background threads
    (stage processing) run concurrently with request threads.
    """
    
    def __init__(self):
        self.config = get_rds_config()
        self._local = threading.local()
    
    def _get_thread_connection(self) -> pymysql.connections.Connection:
        """Get or create a connection for the current thread."""
        conn = getattr(self._local, 'connection', None)
        if conn is None or not conn.open:
            conn = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30
            )
            self._local.connection = conn
        else:
            conn.ping(reconnect=True)
        return conn
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections.
        
        Each thread gets its own connection via threading.local().
        """
        conn = self._get_thread_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            if conn.open:
                conn.rollback()
            raise e
    
    def init_schema(self):
        """Initialize database schema. Run once during setup."""
        schema = """
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        CREATE TABLE IF NOT EXISTS assets (
            asset_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            asset_type ENUM('mascot', 'avatar', 'pose', 'banner', 'logo', 'icon') NOT NULL,
            stage INT NOT NULL,
            oss_url VARCHAR(512),
            transparent_url VARCHAR(512),
            metadata JSON,
            is_selected BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            INDEX idx_project (project_id),
            INDEX idx_type (asset_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        CREATE TABLE IF NOT EXISTS code_exports (
            export_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            component_name VARCHAR(128),
            react_code TEXT,
            css_keyframes TEXT,
            usage_snippet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        CREATE TABLE IF NOT EXISTS brand_kits (
            kit_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            zip_url VARCHAR(512),
            signed_url VARCHAR(512),
            url_expires_at TIMESTAMP NULL,
            download_count INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        CREATE TABLE IF NOT EXISTS brand_dna (
            dna_id VARCHAR(64) PRIMARY KEY,
            project_id VARCHAR(64) NOT NULL,
            brand_name VARCHAR(256),
            brand_personality JSON,
            target_audience JSON,
            visual_style JSON,
            mascot_concept JSON,
            avatar_concept JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
            INDEX idx_project (project_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                for statement in schema.split(';'):
                    stmt = statement.strip()
                    if stmt:
                        cursor.execute(stmt)
        logger.info("Database schema initialized")
    
    # Project operations
    def create_project(self, project_id: str, brand_brief: Dict) -> bool:
        """Create a new project."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO projects (project_id, brand_brief, status) VALUES (%s, %s, %s)",
                    (project_id, json.dumps(brand_brief), 'initialized')
                )
                return cursor.rowcount > 0
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM projects WHERE project_id = %s",
                    (project_id,)
                )
                result = cursor.fetchone()
                if result and result.get('brand_brief'):
                    if isinstance(result['brand_brief'], str):
                        result['brand_brief'] = json.loads(result['brand_brief'])
                return result
    
    def update_project_status(self, project_id: str, status: str, stage: Optional[int] = None, error: Optional[str] = None):
        """Update project status and stage."""
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
    def create_asset(self, asset_id: str, project_id: str, asset_type: str, stage: int, metadata: Optional[Dict] = None):
        """Create a new asset record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO assets (asset_id, project_id, asset_type, stage, metadata) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (asset_id, project_id, asset_type, stage, json.dumps(metadata) if metadata else None)
                )
    
    def update_asset_urls(self, asset_id: str, oss_url: Optional[str] = None, transparent_url: Optional[str] = None):
        """Update asset URLs after generation."""
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
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE assets SET is_selected = TRUE WHERE asset_id = %s",
                    (asset_id,)
                )
    
    def get_project_assets(self, project_id: str, asset_type: Optional[str] = None) -> List[Dict]:
        """Get all assets for a project."""
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
                    if r.get('metadata') and isinstance(r['metadata'], str):
                        r['metadata'] = json.loads(r['metadata'])
                return results
    
    # Generation tracking
    def create_generation(self, generation_id: str, project_id: str, stage: int, input_params: Dict):
        """Create a generation tracking record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO generations (generation_id, project_id, stage, status, input_params, started_at) 
                       VALUES (%s, %s, %s, %s, %s, NOW())""",
                    (generation_id, project_id, stage, 'processing', json.dumps(input_params))
                )
    
    def complete_generation(self, generation_id: str, output_result: Optional[Dict] = None, error: Optional[str] = None):
        """Mark generation as completed or failed."""
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
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM brand_kits WHERE project_id = %s ORDER BY created_at DESC LIMIT 1",
                    (project_id,)
                )
                return cursor.fetchone()


# Singleton instance
db = Database()
