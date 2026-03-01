"""
BrandKin AI - OSS Handler
Object Storage Service for asset storage with signed URLs
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, BinaryIO
from io import BytesIO

# Try to import OSS, fall back to mock if not available
try:
    import oss2
    OSS_AVAILABLE = True
except ImportError:
    OSS_AVAILABLE = False

try:
    from .credentials import get_sts_credentials, get_oss_config
except ImportError:
    get_sts_credentials = None
    get_oss_config = None

# Import mock handler for local development
from .mock_oss import mock_oss_handler


class OSSHandler:
    """Handler for OSS operations with STS credentials and mock fallback."""
    
    # URL expiration time (24 hours as per security requirements)
    URL_EXPIRATION_HOURS = 24
    
    def __init__(self):
        self.use_mock = os.getenv('USE_MOCK_OSS', 'true').lower() == 'true' or not OSS_AVAILABLE
        
        if not self.use_mock and get_oss_config and get_sts_credentials:
            try:
                self.config = get_oss_config()
                creds = get_sts_credentials()
                
                # Initialize OSS auth with STS credentials
                auth = oss2.StsAuth(
                    creds['access_key_id'],
                    creds['access_key_secret'],
                    creds['security_token']
                )
                
                # Initialize bucket
                self.bucket = oss2.Bucket(
                    auth,
                    self.config['endpoint'],
                    self.config['bucket_name']
                )
            except Exception:
                self.use_mock = True
        else:
            self.use_mock = True
    
    def upload_image(self, image_url: str, oss_key: str) -> str:
        """
        Download image from URL and upload to OSS.
        
        Args:
            image_url: Source image URL
            oss_key: Target path in OSS (e.g., "projects/{id}/mascot.png")
        
        Returns:
            OSS URL of uploaded file
        """
        if self.use_mock:
            return mock_oss_handler.upload_image(image_url, oss_key)
        # Download image
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        # Upload to OSS
        self.bucket.put_object(oss_key, response.content)
        
        return f"https://{self.config['bucket_name']}.{self.config['endpoint']}/{oss_key}"
    
    def upload_data(self, data: bytes, oss_key: str) -> str:
        """
        Upload raw data to OSS.
        
        Args:
            data: Binary data to upload
            oss_key: Target path in OSS
        
        Returns:
            OSS URL of uploaded file
        """
        if self.use_mock:
            return mock_oss_handler.upload_bytes(data, oss_key)
        self.bucket.put_object(oss_key, data)
        return f"https://{self.config['bucket_name']}.{self.config['endpoint']}/{oss_key}"
    
    def upload_file(self, file_path: str, oss_key: str) -> str:
        """
        Upload local file to OSS.
        
        Args:
            file_path: Local file path
            oss_key: Target path in OSS
        
        Returns:
            OSS URL of uploaded file
        """
        if self.use_mock:
            with open(file_path, 'rb') as f:
                return mock_oss_handler.upload_bytes(f.read(), oss_key)
        self.bucket.put_object_from_file(oss_key, file_path)
        return f"https://{self.config['bucket_name']}.{self.config['endpoint']}/{oss_key}"
    
    def get_signed_url(self, oss_key: str, expiration_hours: int = None) -> str:
        """
        Generate a signed URL for private bucket access.
        
        Args:
            oss_key: Object key in OSS
            expiration_hours: URL validity period (default: 24 hours)
        
        Returns:
            Signed URL string
        """
        if self.use_mock:
            return mock_oss_handler.get_signed_url(oss_key, expiration_hours)
        
        if expiration_hours is None:
            expiration_hours = self.URL_EXPIRATION_HOURS
        
        # Calculate expiration time in seconds
        expires = int(time.time()) + (expiration_hours * 3600)
        
        # Generate signed URL
        signed_url = self.bucket.sign_url('GET', oss_key, expiration_hours * 3600)
        
        return signed_url
    
    def download_to_memory(self, oss_key: str) -> bytes:
        """
        Download object from OSS to memory.
        
        Args:
            oss_key: Object key in OSS
        
        Returns:
            Object content as bytes
        """
        if self.use_mock:
            return mock_oss_handler.download_to_bytes(oss_key)
        return self.bucket.get_object(oss_key).read()
    
    def delete_object(self, oss_key: str):
        """
        Delete object from OSS.
        
        Args:
            oss_key: Object key to delete
        """
        if self.use_mock:
            return mock_oss_handler.delete_object(oss_key)
        self.bucket.delete_object(oss_key)
    
    def object_exists(self, oss_key: str) -> bool:
        """
        Check if object exists in OSS.
        
        Args:
            oss_key: Object key to check
        
        Returns:
            True if exists, False otherwise
        """
        if self.use_mock:
            return False  # Simplified for mock
        return self.bucket.object_exists(oss_key)
    
    def list_objects(self, prefix: str = '') -> list:
        """
        List objects in bucket with optional prefix.
        
        Args:
            prefix: Path prefix filter
        
        Returns:
            List of object keys
        """
        objects = []
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
            objects.append(obj.key)
        return objects
    
    def upload_with_retry(self, image_url: str, oss_key: str, max_retries: int = 3) -> str:
        """
        Upload image with exponential backoff retry logic.
        
        Args:
            image_url: Source image URL
            oss_key: Target path in OSS
            max_retries: Maximum retry attempts
        
        Returns:
            OSS URL of uploaded file
        """
        for attempt in range(max_retries):
            try:
                return self.upload_image(image_url, oss_key)
            except oss2.exceptions.OssError as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
        
        raise Exception(f"Failed to upload after {max_retries} attempts")


# Singleton instance
oss_handler = OSSHandler()
