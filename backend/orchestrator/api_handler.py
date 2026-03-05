"""
BrandKin AI - Main API Handler
FC 3.0 HTTP handler for API Gateway routes
"""

import json
import logging
import re
import os
import sys
import importlib
from typing import Dict, Any, Optional

# Initialize logger
logger = logging.getLogger(__name__)

def _match_route(method: str, path: str, path_params: dict) -> str:
    """Match HTTP method + path to a named route."""
    path = path.rstrip('/')
    if method == 'GET' and path == '/health': return 'health'
    if method == 'POST' and path == '/api/v1/projects': return 'create_project'
    if method == 'POST' and re.match(r'^/api/v1/projects/[^/]+/select$', path): return 'select_character'
    if method == 'POST' and re.match(r'^/api/v1/projects/[^/]+/revise$', path): return 'revise'
    if method == 'POST' and re.match(r'^/api/v1/projects/[^/]+/finalize$', path): return 'finalize'
    if method == 'GET' and re.match(r'^/api/v1/projects/[^/]+/assets$', path): return 'get_assets'
    if method == 'GET' and re.match(r'^/api/v1/projects/[^/]+/code$', path): return 'get_code'
    if method == 'GET' and re.match(r'^/api/v1/projects/[^/]+$', path): return 'get_project'
    return 'not_found'

def _extract_project_id(path: str) -> Optional[str]:
    match = re.match(r'^/api/v1/projects/([^/]+)', path)
    return match.group(1) if match else None

def get_project_status(project_id: str, headers: Dict, db: Any) -> Dict[str, Any]:
    project = db.get_project(project_id)
    if not project:
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Project not found'})}
    
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
    
    if project.get('current_stage') == 2 and project.get('status') == 'awaiting_selection':
        mascot_assets = [a for a in assets if a['asset_type'] == 'mascot']
        avatar_assets = [a for a in assets if a['asset_type'] == 'avatar']
        if mascot_assets and avatar_assets:
            response['last_stage_result'] = {
                'assets': {
                    'mascot': { 'asset_id': mascot_assets[0]['asset_id'], 'oss_url': mascot_assets[0].get('oss_url'), 'transparent_url': mascot_assets[0].get('transparent_url') },
                    'avatar': { 'asset_id': avatar_assets[0]['asset_id'], 'oss_url': avatar_assets[0].get('oss_url'), 'transparent_url': avatar_assets[0].get('transparent_url') }
                }
            }
    
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps(response)}

def get_project_assets(project_id: str, headers: Dict, db: Any) -> Dict[str, Any]:
    project = db.get_project(project_id)
    if not project:
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Project not found'})}
    assets = db.get_project_assets(project_id)
    formatted = [{
        'asset_id': a['asset_id'], 'type': a['asset_type'], 'stage': a['stage'],
        'oss_url': a.get('oss_url'), 'transparent_url': a.get('transparent_url'),
        'is_selected': a.get('is_selected', False), 'metadata': a.get('metadata'),
        'created_at': a.get('created_at').isoformat() if a.get('created_at') else None
    } for a in assets]
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'project_id': project_id, 'assets': formatted})}

def get_code_exports(project_id: str, headers: Dict, db: Any) -> Dict[str, Any]:
    project = db.get_project(project_id)
    if not project:
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Project not found'})}
    exports = db.get_code_exports(project_id)
    formatted = [{
        'export_id': e['export_id'], 'component_name': e.get('component_name'),
        'react_code': e.get('react_code'), 'css_keyframes': e.get('css_keyframes'),
        'usage_snippet': e.get('usage_snippet'),
        'created_at': e.get('created_at').isoformat() if e.get('created_at') else None
    } for e in exports]
    return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'project_id': project_id, 'code_exports': formatted})}

def _original_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main API entry point with LAZY LOADING to prevent 502 Boot Crashes."""
    
    # 1. Critical Aliases and Paths
    if '/code' not in sys.path:
        sys.path.append('/code')
        
    try:
        import crypto
        sys.modules['Crypto'] = crypto
        sys.modules['Crypto.Hash'] = crypto.Hash
        sys.modules['Crypto.Cipher'] = crypto.Cipher
        sys.modules['Crypto.Util'] = crypto.Util
    except ImportError:
        pass

    # 2. Lazy imports (The core fix for the silent 502)
    try:
        from utils.database import db
        handlers = {
            'stage0_init': importlib.import_module('stage_handlers.stage0_init'),
            'stage3_selection': importlib.import_module('stage_handlers.stage3_selection'),
            'stage6_revision': importlib.import_module('stage_handlers.stage6_revision'),
            'stage7_assembly': importlib.import_module('stage_handlers.stage7_assembly')
        }
    except Exception as e:
        import traceback
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'error': 'Module Import Failure (Lazy Loading)',
                'details': str(e),
                'traceback': traceback.format_exc()
            })
        }

    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '')
    path_params = event.get('pathParameters', {}) or {}
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': os.environ.get('CORS_ALLOWED_ORIGINS', '*'),
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-App-Key, X-Timestamp, X-Nonce, X-Signature'
    }
    
    if http_method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    def _with_cors(response):
        if isinstance(response, dict):
            resp_headers = response.get('headers', {})
            resp_headers.update(headers)
            response['headers'] = resp_headers
        return response

    route = _match_route(http_method, path, path_params)
    
    if route == 'health':
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'status': 'ok', 'env': 'FC 3.0'})}

    if route == 'create_project':
        return _with_cors(handlers['stage0_init'].handler(event, context))
    
    if route == 'get_project':
        project_id = path_params.get('id') or _extract_project_id(path)
        return get_project_status(project_id, headers, db) if project_id else {'statusCode': 400, 'body': 'id required'}
        
    if route == 'get_assets':
        project_id = path_params.get('id') or _extract_project_id(path)
        return get_project_assets(project_id, headers, db) if project_id else {'statusCode': 400, 'body': 'id required'}
        
    if route == 'get_code':
        project_id = path_params.get('id') or _extract_project_id(path)
        return get_code_exports(project_id, headers, db) if project_id else {'statusCode': 400, 'body': 'id required'}

    if route == 'select_character':
        return _with_cors(handlers['stage3_selection'].handler(event, context))
    
    if route == 'revise':
        return _with_cors(handlers['stage6_revision'].handler(event, context))
        
    if route == 'finalize':
        return _with_cors(handlers['stage7_assembly'].handler(event, context))

    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'Route not found: ' + (path or '/')})
    }


def handler(event_bytes, fc_context):
    """
    Production FC 3.0 Handler.
    
    CONFIRMED FORMAT (from live diagnostic dump):
    - arg1: bytes containing JSON: {"version":"v1", "rawPath":"/...", "headers":{...}, "body":"...", "requestContext":{...}}
    - arg2: fc_rapis_context.FCContext (NOT callable, NOT WSGI)
    
    This handler converts the FC 3.0 JSON-bytes format into the internal event dict format.
    """
    
    try:
        # 1. Parse the FC 3.0 request bytes into a dict
        if isinstance(event_bytes, (bytes, bytearray)):
            fc_request = json.loads(event_bytes.decode('utf-8'))
        elif isinstance(event_bytes, dict):
            fc_request = event_bytes
        elif isinstance(event_bytes, str):
            fc_request = json.loads(event_bytes)
        else:
            fc_request = {}
        
        # 2. Extract HTTP metadata from the FC 3.0 request format
        # FC 3.0 uses: rawPath, requestContext.http.method, headers, body, queryStringParameters
        raw_path = fc_request.get('rawPath', '/')
        
        # HTTP method: check requestContext.http.method first, then fall back to headers
        request_context = fc_request.get('requestContext', {})
        http_info = request_context.get('http', {})
        http_method = http_info.get('method', 'GET')
        
        # If method is still GET but we have no requestContext, try other common locations
        if http_method == 'GET' and not http_info:
            http_method = fc_request.get('httpMethod', 'GET')
        
        # Query string
        query_params = fc_request.get('queryStringParameters', {}) or {}
        
        # Headers from FC 3.0 format
        fc_headers = fc_request.get('headers', {}) or {}
        
        # Body
        body = fc_request.get('body', '{}') or '{}'
        if isinstance(body, dict):
            body = json.dumps(body)
        
        # 3. Build the normalized event dict for _original_handler
        event = {
            'httpMethod': http_method,
            'path': raw_path,
            'pathParameters': fc_request.get('pathParameters', {}) or {},
            'queryStringParameters': query_params,
            'headers': fc_headers,
            'body': body
        }
        
        # 4. Call the main handler
        result = _original_handler(event, fc_context)
        
        # 5. FC 3.0 expects a specific response format
        return result
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.critical(f"Handler crash: {e}\n{error_trace}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'error': 'Handler Crash',
                'details': str(e),
                'traceback': error_trace
            })
        }
