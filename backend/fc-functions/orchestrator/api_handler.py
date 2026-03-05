"""
BrandKin AI - Main API Handler
FC 3.0 HTTP handler for API Gateway routes
"""

import json
import logging
import re
from typing import Dict, Any, Optional

import sys
sys.path.append('/code')  # FC 3.0 working directory

# CRITICAL 502 FIX: Alibaba Cloud SDK requires 'Crypto' (capital C), 
# but Linux pip often installs it as 'crypto'. This prevents the 502 Boot Crash.
try:
    import crypto
    import sys
    sys.modules['Crypto'] = crypto
    sys.modules['Crypto.Hash'] = crypto.Hash
    sys.modules['Crypto.Cipher'] = crypto.Cipher
    sys.modules['Crypto.Util'] = crypto.Util
except ImportError:
    pass

from stage_handlers import (
    stage0_init,
    stage1_dna,
    stage2_visual,
    stage3_selection,
    stage4_poses,
    stage5_code,
    stage6_revision,
    stage7_assembly
)
from utils.database import db

logger = logging.getLogger(__name__)

# Allowed CORS origins (configure via env var for production)
import os
CORS_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '*')


def _original_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main API entry point for all routes.
    
    Routes:
    - POST /api/v1/projects -> Stage 0: Initialize
    - GET  /api/v1/projects/{id} -> Get project status
    - GET  /api/v1/projects/{id}/assets -> Get project assets
    - GET  /api/v1/projects/{id}/code -> Get code exports
    - POST /api/v1/projects/{id}/select -> Stage 3: Character selection
    - POST /api/v1/projects/{id}/revise -> Stage 6: Revision
    - POST /api/v1/projects/{id}/finalize -> Stage 7: Assembly
    - GET  /health -> Health check
    """
    
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '')
    path_params = event.get('pathParameters', {}) or {}
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': CORS_ORIGINS,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-App-Key, X-Timestamp, X-Nonce, X-Signature'
    }
    
    # Handle OPTIONS for CORS
    if http_method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Parse route
        route = _match_route(http_method, path, path_params)
        
        if route == 'health':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'status': 'ok', 'service': 'BrandKin AI'})
            }
        
        # Helper to ensure CORS headers are on sub-handler responses
        def _with_cors(response):
            if isinstance(response, dict):
                response_headers = response.get('headers', {})
                response_headers.update(headers)
                response['headers'] = response_headers
            return response
        
        if route == 'create_project':
            return _with_cors(stage0_init.handler(event, context))
        
        if route == 'get_project':
            project_id = path_params.get('id') or _extract_project_id(path)
            if project_id:
                return get_project_status(project_id, headers)
        
        if route == 'get_assets':
            project_id = path_params.get('id') or _extract_project_id(path)
            if project_id:
                return get_project_assets(project_id, headers)
        
        if route == 'get_code':
            project_id = path_params.get('id') or _extract_project_id(path)
            if project_id:
                return get_code_exports(project_id, headers)
        
        if route == 'select_character':
            return _with_cors(stage3_selection.handler(event, context))
        
        if route == 'revise':
            return _with_cors(stage6_revision.handler(event, context))
        
        if route == 'finalize':
            return _with_cors(stage7_assembly.handler(event, context))
        
        # 404 for unmatched routes
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Route not found'})
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"API handler error on {http_method} {path}: {error_details}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e),
                'traceback': error_details
            })
        }


def _match_route(method: str, path: str, path_params: dict) -> str:
    """Match HTTP method + path to a named route.
    
    Uses explicit path matching to avoid ambiguous substring matches.
    """
    # Normalize path
    path = path.rstrip('/')
    
    if method == 'GET' and path == '/health':
        return 'health'
    
    if method == 'POST' and path == '/api/v1/projects':
        return 'create_project'
    
    # Match: /api/v1/projects/{id}/select
    if method == 'POST' and re.match(r'^/api/v1/projects/[^/]+/select$', path):
        return 'select_character'
    
    # Match: /api/v1/projects/{id}/revise
    if method == 'POST' and re.match(r'^/api/v1/projects/[^/]+/revise$', path):
        return 'revise'
    
    # Match: /api/v1/projects/{id}/finalize
    if method == 'POST' and re.match(r'^/api/v1/projects/[^/]+/finalize$', path):
        return 'finalize'
    
    # Match: /api/v1/projects/{id}/assets
    if method == 'GET' and re.match(r'^/api/v1/projects/[^/]+/assets$', path):
        return 'get_assets'
    
    # Match: /api/v1/projects/{id}/code
    if method == 'GET' and re.match(r'^/api/v1/projects/[^/]+/code$', path):
        return 'get_code'
    
    # Match: /api/v1/projects/{id} (must be last to avoid catching sub-routes)
    if method == 'GET' and re.match(r'^/api/v1/projects/[^/]+$', path):
        return 'get_project'
    
    return 'not_found'


def _extract_project_id(path: str) -> Optional[str]:
    """Extract project ID from path like /api/v1/projects/{id}/..."""
    match = re.match(r'^/api/v1/projects/([^/]+)', path)
    return match.group(1) if match else None


def get_project_status(project_id: str, headers: Dict) -> Dict[str, Any]:
    """Get project status and current stage info."""
    project = db.get_project(project_id)
    
    if not project:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Project not found'})
        }
    
    # Get assets summary
    assets = db.get_project_assets(project_id)
    asset_summary = {
        'mascot': len([a for a in assets if a['asset_type'] == 'mascot']),
        'avatar': len([a for a in assets if a['asset_type'] == 'avatar']),
        'pose': len([a for a in assets if a['asset_type'] == 'pose']),
        'total': len(assets)
    }
    
    code_exports = db.get_code_exports(project_id)
    brand_kit = db.get_brand_kit(project_id)
    
    response = {
        'project_id': project_id,
        'status': project.get('status'),
        'current_stage': project.get('current_stage'),
        'brand_brief': project.get('brand_brief'),
        'brand_dna': json.loads(project['brand_dna']) if project.get('brand_dna') and isinstance(project['brand_dna'], str) else project.get('brand_dna'),
        'created_at': project.get('created_at').isoformat() if project.get('created_at') else None,
        'updated_at': project.get('updated_at').isoformat() if project.get('updated_at') else None,
        'assets': asset_summary,
        'code_exports': len(code_exports),
        'brand_kit': {
            'available': brand_kit is not None,
            'download_url': brand_kit.get('signed_url') if brand_kit else None,
            'expires_at': brand_kit.get('url_expires_at').isoformat() if brand_kit and brand_kit.get('url_expires_at') else None
        } if brand_kit else None
    }
    
    # Include full asset details for Stage 2 (awaiting selection)
    if project.get('current_stage') == 2 and project.get('status') == 'awaiting_selection':
        mascot_assets = [a for a in assets if a['asset_type'] == 'mascot']
        avatar_assets = [a for a in assets if a['asset_type'] == 'avatar']
        
        if mascot_assets and avatar_assets:
            response['last_stage_result'] = {
                'assets': {
                    'mascot': {
                        'asset_id': mascot_assets[0]['asset_id'],
                        'oss_url': mascot_assets[0].get('oss_url'),
                        'transparent_url': mascot_assets[0].get('transparent_url')
                    },
                    'avatar': {
                        'asset_id': avatar_assets[0]['asset_id'],
                        'oss_url': avatar_assets[0].get('oss_url'),
                        'transparent_url': avatar_assets[0].get('transparent_url')
                    }
                }
            }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(response)
    }


def get_project_assets(project_id: str, headers: Dict) -> Dict[str, Any]:
    """Get all assets for a project."""
    project = db.get_project(project_id)
    
    if not project:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Project not found'})
        }
    
    assets = db.get_project_assets(project_id)
    
    formatted_assets = []
    for asset in assets:
        formatted_assets.append({
            'asset_id': asset['asset_id'],
            'type': asset['asset_type'],
            'stage': asset['stage'],
            'oss_url': asset.get('oss_url'),
            'transparent_url': asset.get('transparent_url'),
            'is_selected': asset.get('is_selected', False),
            'metadata': asset.get('metadata'),
            'created_at': asset.get('created_at').isoformat() if asset.get('created_at') else None
        })
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'project_id': project_id,
            'assets': formatted_assets
        })
    }


def get_code_exports(project_id: str, headers: Dict) -> Dict[str, Any]:
    """Get all code exports for a project."""
    project = db.get_project(project_id)
    
    if not project:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Project not found'})
        }
    
    exports = db.get_code_exports(project_id)
    
    formatted_exports = []
    for export in exports:
        formatted_exports.append({
            'export_id': export['export_id'],
            'component_name': export.get('component_name'),
            'react_code': export.get('react_code'),
            'css_keyframes': export.get('css_keyframes'),
            'usage_snippet': export.get('usage_snippet'),
            'created_at': export.get('created_at').isoformat() if export.get('created_at') else None
        })
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'project_id': project_id,
            'code_exports': formatted_exports
        })
    }

def handler(environ_or_event, context_or_start_response):
    """
    Diagnostic handler to discover EXACTLY what FC 3.0 is passing.
    """
    try:
        if isinstance(environ_or_event, dict) and 'httpMethod' in environ_or_event:
            # It's an API Gateway dict
            return _original_handler(environ_or_event, context_or_start_response)
        
        # If we reach here, the infrastructure is passing something unexpected (like bytes)
        # Let's inspect it and return a 200 OK so the 502 vanishes and we can read the payload!
        event_type = str(type(environ_or_event))
        event_str = str(environ_or_event)
        
        # Attempt to parse as JSON if it's bytes
        import json
        if isinstance(environ_or_event, bytes):
            try:
                parsed = json.loads(environ_or_event.decode('utf-8'))
                if isinstance(parsed, dict) and 'httpMethod' in parsed:
                    return _original_handler(parsed, context_or_start_response)
                event_str = "JSON parsed: " + str(parsed)
            except Exception as e:
                event_str = "Bytes (failed to parse JSON): " + str(e) + " | " + repr(environ_or_event[:200])
                
        # If it's a WSGI environ, start_response will be callable
        if callable(context_or_start_response):
            context_or_start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({
                'debug': 'WSGI detected',
                'environ_keys': list(environ_or_event.keys()) if isinstance(environ_or_event, dict) else event_type
            }).encode('utf-8')]
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Unhandled FC 3.0 Trigger Format',
                'event_type': event_type,
                'event_content': event_str,
                'context_type': str(type(context_or_start_response))
            })
        }
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e), 'trace': traceback.format_exc()})
        }
