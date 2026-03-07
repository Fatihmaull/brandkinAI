"""
BrandKin AI - Stage 3: Character Selection
Store user selection and trigger parallel Stage 4 (Pose Pack) and Stage 5 (Code Export).
"""

import json
import uuid
from typing import Dict, Any

from utils.database import db


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 3 Handler: Process user character selection.
    
    API Endpoint: POST /api/v1/projects/{id}/select
    
    Args:
        event: HTTP request with selected asset_id
        context: FC context
    
    Returns:
        Confirmation and trigger status for Stages 4 & 5
    """
    try:
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Get project_id from path parameters
        path_params = event.get('pathParameters', {})
        project_id = path_params.get('id') or body.get('project_id')
        
        selected_asset_id = body.get('asset_id')
        selection_type = body.get('type', 'mascot')  # 'mascot' or 'avatar'
        
        if not project_id or not selected_asset_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing project_id or asset_id'})
            }
        
        result = process_selection(project_id, selected_asset_id, selection_type)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def process_selection(project_id: str, asset_id: str, selection_type: str) -> Dict[str, Any]:
    """
    Process user selection and trigger parallel stages.
    
    Args:
        project_id: Project UUID
        asset_id: Selected asset UUID
        selection_type: 'mascot' or 'avatar'
    
    Returns:
        Processing result
    """
    # Verify project exists
    project = db.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    
    # Mark asset as selected
    db.select_asset(asset_id)
    
    # Update project status
    db.update_project_status(project_id, 'selection_made', stage=3)
    
    # Get selected asset details
    assets = db.get_project_assets(project_id, selection_type)
    selected_asset = next((a for a in assets if a['asset_id'] == asset_id), None)
    
    if not selected_asset:
        raise ValueError(f"Asset {asset_id} not found in project {project_id}")
    
    # Trigger parallel Stage 4 and Stage 5
    # In production, these would be async MNS messages
    
    # Get brand DNA for context
    brand_dna = project.get('brand_brief', {})
    
    # Trigger Stage 4: Pose Pack Generation
    trigger_stage4(project_id, selected_asset, brand_dna)
    
    # Trigger Stage 5: Code Export
    trigger_stage5(project_id, selected_asset, brand_dna)
    
    return {
        'success': True,
        'project_id': project_id,
        'stage': 3,
        'selected_asset': {
            'asset_id': asset_id,
            'type': selection_type,
            'url': selected_asset.get('transparent_url') or selected_asset.get('oss_url')
        },
        'message': 'Selection recorded. Stage 4 (Pose Pack) and Stage 5 (Code Export) started in parallel.'
    }


import threading
import logging

logger = logging.getLogger(__name__)

def trigger_stage4(project_id: str, selected_asset: Dict, brand_dna: Dict):
    """
    Trigger Stage 4: Pose Pack Generation in a background thread.
    """
    def _run_stage4():
        try:
            from .stage4_poses import process_stage4
            process_stage4(project_id, selected_asset, brand_dna)
        except Exception as e:
            logger.error(f"Stage 4 background processing failed for {project_id}: {e}", exc_info=True)
            try:
                db.update_project_status(project_id, 'failed', stage=4, error=str(e))
            except Exception:
                pass
    
    thread = threading.Thread(target=_run_stage4, daemon=True)
    thread.start()


def trigger_stage5(project_id: str, selected_asset: Dict, brand_dna: Dict):
    """
    Trigger Stage 5: Code Export in a background thread.
    """
    def _run_stage5():
        try:
            from .stage5_code import process_stage5
            process_stage5(project_id, selected_asset, brand_dna)
        except Exception as e:
            logger.error(f"Stage 5 background processing failed for {project_id}: {e}", exc_info=True)
            try:
                db.update_project_status(project_id, 'failed', stage=5, error=str(e))
            except Exception:
                pass
    
    thread = threading.Thread(target=_run_stage5, daemon=True)
    thread.start()
