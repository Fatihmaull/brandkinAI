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

def handler(environ_or_event, context_or_start_response):
    """
    DIAGNOSTIC HANDLER - Temporarily dumps all FC 3.0 runtime info
    to discover where HTTP method, path, and headers are stored.
    """
    import os
    
    # Collect diagnostic data
    diag = {
        'arg1_type': str(type(environ_or_event)),
        'arg2_type': str(type(context_or_start_response)),
        'arg2_callable': callable(context_or_start_response),
    }
    
    # Inspect arg1
    if isinstance(environ_or_event, (bytes, bytearray)):
        diag['arg1_preview'] = environ_or_event[:500].decode('utf-8', errors='replace')
    elif isinstance(environ_or_event, dict):
        diag['arg1_keys'] = list(environ_or_event.keys())[:30]
        # Check for WSGI keys
        for key in ['REQUEST_METHOD', 'PATH_INFO', 'QUERY_STRING', 'CONTENT_TYPE', 
                     'CONTENT_LENGTH', 'SERVER_NAME', 'SERVER_PORT', 'wsgi.input',
                     'fc.context', 'fc.request_uri', 'HTTP_HOST']:
            if key in environ_or_event:
                val = environ_or_event[key]
                diag[f'arg1.{key}'] = str(val)[:200]
    elif isinstance(environ_or_event, str):
        diag['arg1_preview'] = environ_or_event[:500]
    else:
        diag['arg1_repr'] = repr(environ_or_event)[:500]
    
    # Inspect arg2 (context or start_response)
    try:
        diag['arg2_dir'] = [x for x in dir(context_or_start_response) if not x.startswith('__')]
    except:
        diag['arg2_dir'] = 'failed'
    
    try:
        if hasattr(context_or_start_response, 'request_id'):
            diag['arg2.request_id'] = str(context_or_start_response.request_id)
        if hasattr(context_or_start_response, 'function'):
            diag['arg2.function'] = str(context_or_start_response.function)
        if hasattr(context_or_start_response, 'http_params'):
            diag['arg2.http_params'] = str(context_or_start_response.http_params)
        if hasattr(context_or_start_response, 'service'):
            diag['arg2.service'] = str(context_or_start_response.service)
        if hasattr(context_or_start_response, 'credentials'):
            diag['arg2.credentials'] = 'present (hidden)'
    except Exception as e:
        diag['arg2_inspect_error'] = str(e)
    
    # Inspect environment variables (FC-related)
    fc_env = {}
    for k, v in os.environ.items():
        if any(prefix in k.upper() for prefix in ['FC_', 'HTTP_', 'REQUEST', 'PATH', 'METHOD', 'SERVER', 'CONTENT']):
            fc_env[k] = v[:200]
    diag['fc_env_vars'] = fc_env
    
    # Build response
    response_body = json.dumps(diag, indent=2, default=str)
    
    # If arg2 is callable, it's WSGI mode — respond via WSGI
    if callable(context_or_start_response):
        start_response = context_or_start_response
        start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
        return [response_body.encode('utf-8')]
    else:
        # Event mode — return dict
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': response_body
        }
