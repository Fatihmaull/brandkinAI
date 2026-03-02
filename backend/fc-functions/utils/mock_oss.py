"""
BrandKin AI - Mock OSS Handler for Local Development
Simulates OSS operations without requiring real Alibaba Cloud resources
"""

import os
import uuid
import requests
from typing import Optional
from datetime import datetime, timedelta


class MockOSSHandler:
    """Mock handler that simulates OSS operations for local testing."""
    
    URL_EXPIRATION_HOURS = 24
    
    def __init__(self):
        self.storage_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'local_storage')
        os.makedirs(self.storage_dir, exist_ok=True)
        self.mock_urls = {}
    
    def upload_image(self, image_url: str, oss_key: str) -> str:
        """Simulate uploading an image - just returns the original URL or a local path."""
        # For placeholder images, just return as-is
        if 'placehold.co' in image_url:
            return image_url
        
        # For real images, we could download and save locally
        # But for now, just return the original URL
        try:
            # Try to download and save locally
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                local_path = os.path.join(self.storage_dir, oss_key.replace('/', '_'))
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return f"file://{local_path}"
        except Exception:
            pass
        
        return image_url
    
    def upload_with_retry(self, image_url: str, oss_key: str, max_retries: int = 3) -> str:
        """Upload with retry logic (mock version just calls upload_image)."""
        return self.upload_image(image_url, oss_key)
    
    def upload_bytes(self, data: bytes, oss_key: str) -> str:
        """Simulate uploading bytes."""
        local_path = os.path.join(self.storage_dir, oss_key.replace('/', '_'))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(data)
        return f"file://{local_path}"
    
    def get_signed_url(self, oss_key: str, expiration_hours: int = None) -> str:
        """Generate a mock signed URL."""
        if expiration_hours is None:
            expiration_hours = self.URL_EXPIRATION_HOURS
        
        # For local files, return file:// URL
        if oss_key.startswith('file://'):
            return oss_key
        
        # For external URLs, return as-is
        if oss_key.startswith('http'):
            return oss_key
        
        # For brand kit zip files, create a data URL or return placeholder
        if oss_key.endswith('.zip'):
            # Return a placeholder message since we can't generate real ZIP in mock mode
            return f"data:text/plain;charset=utf-8,This%20is%20a%20mock%20brand%20kit%20download.%20In%20production,%20this%20would%20be%20a%20real%20ZIP%20file%20containing%20all%20brand%20assets.%20Expires%20in%20{expiration_hours}h"
        
        # Generate mock signed URL
        return f"https://mock-oss.local/{oss_key}?expires={expiration_hours}h"
    
    def download_to_bytes(self, oss_key: str) -> bytes:
        """Simulate downloading from OSS."""
        local_path = os.path.join(self.storage_dir, oss_key.replace('/', '_'))
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                return f.read()
        return b''
    
    def delete_object(self, oss_key: str) -> bool:
        """Simulate deleting an object."""
        local_path = os.path.join(self.storage_dir, oss_key.replace('/', '_'))
        if os.path.exists(local_path):
            os.remove(local_path)
            return True
        return False


# Singleton instance
mock_oss_handler = MockOSSHandler()
