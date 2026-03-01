"""
BrandKin AI - Main API Handler
FC 3.0 HTTP handler for API Gateway routes
"""

import json
from typing import Dict, Any

# Import stage handlers
import sys
sys.path.append('/code')  # FC 3.0 working directory

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


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main API entry point for all routes.
    
    Routes:
    - POST /api/v1/projects -> Stage 0: Initialize
    - GET  /api/v1/projects/{id} -> Get project status
    - POST /api/v1/projects/{id}/select -> Stage 3: Character selection
    - POST /api/v1/projects/{id}/revise -> Stage 6: Revision
    - POST /api/v1/projects/{id}/finalize -> Stage 7: Assembly
    """
    
    # Parse request
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '')
    path_params = event.get('pathParameters', {}) or {}
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle OPTIONS for CORS
    if http_method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Route: Create project (Stage 0)
        if http_method == 'POST' and path == '/api/v1/projects':
            return stage0_init.handler(event, context)
        
        # Route: Get project status
        if http_method == 'GET' and '/api/v1/projects/' in path:
            project_id = path_params.get('id')
            if project_id:
                return get_project_status(project_id, headers)
        
        # Route: Character selection (Stage 3)
        if http_method == 'POST' and '/select' in path:
            return stage3_selection.handler(event, context)
        
        # Route: Revision request (Stage 6)
        if http_method == 'POST' and '/revise' in path:
            return stage6_revision.handler(event, context)
        
        # Route: Finalize/Assembly (Stage 7)
        if http_method == 'POST' and '/finalize' in path:
            return stage7_assembly.handler(event, context)
        
        # Route: Get project assets
        if http_method == 'GET' and '/assets' in path:
            project_id = path_params.get('id')
            if project_id:
                return get_project_assets(project_id, headers)
        
        # Route: Get code exports
        if http_method == 'GET' and '/code' in path:
            project_id = path_params.get('id')
            if project_id:
                return get_code_exports(project_id, headers)
        
        # 404 for unmatched routes
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Route not found', 'path': path})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }


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
    
    # Get code exports
    code_exports = db.get_code_exports(project_id)
    
    # Get brand kit if available
    brand_kit = db.get_brand_kit(project_id)
    
    # Build response
    response = {
        'project_id': project_id,
        'status': project.get('status'),
        'current_stage': project.get('current_stage'),
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
    
    # Format assets for response
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
    
    # Format exports for response
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
