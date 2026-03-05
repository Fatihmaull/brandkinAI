"""
BrandKin AI - STS Credential Handler
Stage 0-7: Security & Auth (Alibaba Cloud RAM + STS)

FC automatically retrieves STS temporary tokens via instance metadata
without hardcoded environment variables. This implements credential-free runtime.
"""

import os
from typing import Dict, Optional


def get_sts_credentials() -> Dict[str, str]:
    """
    Retrieve STS credentials from FC environment variables.
    FC 3.0 automatically injects these at runtime via RAM role assumption.
    
    Returns:
        Dict containing access_key_id, access_key_secret, security_token
    
    Raises:
        KeyError: If required environment variables are missing
    """
    required_vars = [
        'ALIBABA_CLOUD_ACCESS_KEY_ID',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET',
        'ALIBABA_CLOUD_SECURITY_TOKEN'
    ]
    
    # Validate all required variables are present
    for var in required_vars:
        if var not in os.environ:
            raise KeyError(f"Missing required environment variable: {var}")
    
    return {
        'access_key_id': os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
        'access_key_secret': os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'],
        'security_token': os.environ['ALIBABA_CLOUD_SECURITY_TOKEN']
    }


def get_dashscope_api_key() -> str:
    """
    Retrieve DashScope API key from environment.
    In production, this should be fetched from RAM Secret Manager or KMS.
    
    Returns:
        DashScope API key string
    """
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        raise KeyError("Missing DASHSCOPE_API_KEY environment variable")
    return api_key


def get_oss_config() -> Dict[str, str]:
    """
    Get OSS configuration from environment variables.
    
    Returns:
        Dict containing bucket_name, endpoint, region
    """
    return {
        'bucket_name': os.environ.get('OSS_BUCKET', 'brandkin-ai-assets'),
        'endpoint': os.environ.get('OSS_ENDPOINT', 'oss-cn-hangzhou.aliyuncs.com'),
        'region': os.environ.get('OSS_REGION', 'cn-hangzhou'),
        'cdn_domain': os.environ.get('OSS_CDN_DOMAIN', 'assets.brandkin.ai')
    }


def get_rds_config() -> Dict[str, str]:
    """
    Get RDS MySQL configuration from environment variables.
    
    Returns:
        Dict containing host, port, database, user, password
    """
    return {
        'host': os.environ.get('RDS_HOST', 'brandkin-ai.mysql.rds.aliyuncs.com'),
        'port': int(os.environ.get('RDS_PORT', '3306')),
        'database': os.environ.get('RDS_DATABASE', 'brandkin_ai'),
        'user': os.environ.get('RDS_USER', 'brandkin_admin'),
        'password': os.environ.get('RDS_PASSWORD', '')
    }


def get_mns_config() -> Dict[str, str]:
    """
    Get MNS (Message Service) configuration.
    
    Returns:
        Dict containing endpoint, queue_name
    """
    return {
        'endpoint': os.environ.get('MNS_ENDPOINT', 'https://123456789.mns.cn-hangzhou.aliyuncs.com'),
        'queue_name': os.environ.get('MNS_QUEUE_NAME', 'brandkin-generation-tasks'),
        'region': os.environ.get('MNS_REGION', 'cn-hangzhou')
    }
