"""
BrandKin AI - OSS Handler
Object Storage Service for asset storage with signed URLs.

Automatically falls back to local file storage when OSS credentials
are not available (local development).
"""

import os
import logging
import requests
import time
import base64
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


def _is_oss_available() -> bool:
    """Check if OSS credentials are available in the environment."""
    # Check for direct AccessKey auth (local dev with real credentials)
    if os.environ.get('OSS_ACCESS_KEY_ID') and os.environ.get('OSS_ACCESS_KEY_SECRET'):
        return True
    # Check for STS auth (FC production - auto-injected)
    if os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'):
        return True
    return False


class LocalStorageHandler:
    """Local file storage fallback for development without OSS.
    
    Stores files in a local directory and serves them via the Flask dev server.
    """
    
    URL_EXPIRATION_HOURS = 24  # No-op for local, but keeps API consistent
    
    def __init__(self):
        # Store files relative to the fc-functions directory
        self.storage_dir = Path(__file__).parent.parent / 'local_storage'
        self.storage_dir.mkdir(exist_ok=True)
        self.base_url = os.environ.get('LOCAL_STORAGE_URL', 'http://localhost:5000/local-assets')
        logger.info(f"Using LOCAL file storage at: {self.storage_dir}")
    
    def _ensure_dir(self, oss_key: str) -> Path:
        """Create directory structure for the key and return file path."""
        file_path = self.storage_dir / oss_key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path
    
    def _download_from_url(self, url: str) -> bytes:
        """Download content from a URL, handling data: URIs."""
        if url.startswith('data:'):
            # Handle data: URIs (e.g., data:image/svg+xml;base64,...)
            _, data_part = url.split(',', 1)
            return base64.b64decode(data_part)
        else:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            return response.content
    
    def upload_image(self, image_url: str, oss_key: str) -> str:
        """Download image from URL and save locally."""
        content = self._download_from_url(image_url)
        file_path = self._ensure_dir(oss_key)
        file_path.write_bytes(content)
        logger.info(f"Saved locally: {oss_key}")
        return f"{self.base_url}/{oss_key}"
    
    def upload_data(self, data: bytes, oss_key: str) -> str:
        """Save raw data locally."""
        file_path = self._ensure_dir(oss_key)
        file_path.write_bytes(data)
        logger.info(f"Saved locally: {oss_key}")
        return f"{self.base_url}/{oss_key}"
    
    def upload_file(self, file_path_src: str, oss_key: str) -> str:
        """Copy local file to storage directory."""
        dest_path = self._ensure_dir(oss_key)
        shutil.copy2(file_path_src, dest_path)
        logger.info(f"Saved locally: {oss_key}")
        return f"{self.base_url}/{oss_key}"
    
    def get_signed_url(self, oss_key: str, expiration_hours: Optional[int] = None) -> str:
        """Return local URL (no signing needed for local dev)."""
        return f"{self.base_url}/{oss_key}"
    
    def download_to_memory(self, oss_key: str) -> bytes:
        """Read file from local storage."""
        file_path = self.storage_dir / oss_key
        if not file_path.exists():
            raise FileNotFoundError(f"Local file not found: {oss_key}")
        return file_path.read_bytes()
    
    def delete_object(self, oss_key: str):
        """Delete file from local storage."""
        file_path = self.storage_dir / oss_key
        if file_path.exists():
            file_path.unlink()
    
    def object_exists(self, oss_key: str) -> bool:
        """Check if file exists in local storage."""
        return (self.storage_dir / oss_key).exists()
    
    def list_objects(self, prefix: str = '') -> list:
        """List files with optional prefix."""
        search_dir = self.storage_dir / prefix
        if not search_dir.exists():
            return []
        return [
            str(p.relative_to(self.storage_dir))
            for p in search_dir.rglob('*')
            if p.is_file()
        ]
    
    def upload_with_retry(self, image_url: str, oss_key: str, max_retries: int = 3) -> str:
        """Upload with retry (simplified for local - just one attempt)."""
        return self.upload_image(image_url, oss_key)


class OSSHandler:
    """Handler for OSS operations with AccessKey or STS credentials."""
    
    URL_EXPIRATION_HOURS = 24
    
    def __init__(self):
        from .credentials import get_oss_config
        self.config = get_oss_config()
        self._bucket = None
    
    def _get_bucket(self):
        """Get or create OSS bucket connection.
        
        Supports two auth modes:
        1. AccessKey auth (local dev): OSS_ACCESS_KEY_ID + OSS_ACCESS_KEY_SECRET
        2. STS auth (FC production): ALIBABA_CLOUD_ACCESS_KEY_ID + SECRET + TOKEN
        """
        if self._bucket is None:
            try:
                import oss2
                
                ak_id = os.environ.get('OSS_ACCESS_KEY_ID')
                ak_secret = os.environ.get('OSS_ACCESS_KEY_SECRET')
                
                if ak_id and ak_secret:
                    # AccessKey auth (local dev with real credentials)
                    auth = oss2.Auth(ak_id, ak_secret)
                    logger.info("OSS: Using AccessKey auth")
                else:
                    # STS auth (FC production)
                    from .credentials import get_sts_credentials
                    creds = get_sts_credentials()
                    auth = oss2.StsAuth(
                        creds['access_key_id'],
                        creds['access_key_secret'],
                        creds['security_token']
                    )
                    logger.info("OSS: Using STS auth")
                
                endpoint = self.config['endpoint']
                # Ensure endpoint has https:// prefix
                if not endpoint.startswith('http'):
                    endpoint = f'https://{endpoint}'
                
                self._bucket = oss2.Bucket(
                    auth,
                    endpoint,
                    self.config['bucket_name']
                )
            except Exception as e:
                logger.error(f"Failed to initialize OSS bucket: {e}")
                raise
        return self._bucket
    
    def upload_image(self, image_url: str, oss_key: str) -> str:
        """Download image from URL and upload to OSS."""
        if image_url.startswith('data:'):
            # Handle data: URIs
            _, data_part = image_url.split(',', 1)
            import base64
            content = base64.b64decode(data_part)
        else:
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()
            content = response.content
        
        bucket = self._get_bucket()
        bucket.put_object(oss_key, content)
        return f"https://{self.config['bucket_name']}.{self.config['endpoint']}/{oss_key}"
    
    def upload_data(self, data: bytes, oss_key: str) -> str:
        """Upload raw data to OSS."""
        bucket = self._get_bucket()
        bucket.put_object(oss_key, data)
        return f"https://{self.config['bucket_name']}.{self.config['endpoint']}/{oss_key}"
    
    def upload_file(self, file_path: str, oss_key: str) -> str:
        """Upload local file to OSS."""
        bucket = self._get_bucket()
        bucket.put_object_from_file(oss_key, file_path)
        return f"https://{self.config['bucket_name']}.{self.config['endpoint']}/{oss_key}"
    
    def get_signed_url(self, oss_key: str, expiration_hours: Optional[int] = None) -> str:
        """Generate a signed URL for private bucket access."""
        if expiration_hours is None:
            expiration_hours = self.URL_EXPIRATION_HOURS
        bucket = self._get_bucket()
        return bucket.sign_url('GET', oss_key, expiration_hours * 3600)
    
    def download_to_memory(self, oss_key: str) -> bytes:
        """Download object from OSS to memory."""
        bucket = self._get_bucket()
        return bucket.get_object(oss_key).read()
    
    def delete_object(self, oss_key: str):
        """Delete object from OSS."""
        bucket = self._get_bucket()
        bucket.delete_object(oss_key)
    
    def object_exists(self, oss_key: str) -> bool:
        """Check if object exists in OSS."""
        bucket = self._get_bucket()
        return bucket.object_exists(oss_key)
    
    def list_objects(self, prefix: str = '') -> list:
        """List objects in bucket with optional prefix."""
        import oss2
        bucket = self._get_bucket()
        return [obj.key for obj in oss2.ObjectIterator(bucket, prefix=prefix)]
    
    def upload_with_retry(self, image_url: str, oss_key: str, max_retries: int = 3) -> str:
        """Upload image with exponential backoff retry logic."""
        for attempt in range(max_retries):
            try:
                return self.upload_image(image_url, oss_key)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Upload attempt {attempt + 1} failed: {e}")
                time.sleep(2 ** attempt)
        raise Exception(f"Failed to upload after {max_retries} attempts")


# Auto-select handler based on environment
if _is_oss_available():
    logger.info("OSS credentials detected — using Alibaba Cloud OSS")
    oss_handler = OSSHandler()
else:
    logger.info("No OSS credentials — using local file storage")
    oss_handler = LocalStorageHandler()
