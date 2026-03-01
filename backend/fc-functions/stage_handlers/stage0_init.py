"""
BrandKin AI - Stage 0: Project Initialization
Accepts brand_brief JSON, initializes project in RDS, triggers Stage 1.
"""

import json
import uuid
from typing import Dict, Any

from utils.database import db
from utils.credentials import get_mns_config


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 0 Handler: Initialize new brand project.
    
    Args:
        event: HTTP request with brand_brief
        context: FC context
    
    Returns:
        Response with project_id and initial status
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        brand_brief = body.get('brand_brief')
        
        if not brand_brief:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing brand_brief in request'})
            }
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Create project in database
        db.create_project(project_id, brand_brief)
        
        # Trigger Stage 1 via MNS (async)
        trigger_stage1(project_id, brand_brief)
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'project_id': project_id,
                'status': 'initialized',
                'current_stage': 0,
                'message': 'Project created successfully. Stage 1 (Brand DNA Analysis) started.'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def trigger_stage1(project_id: str, brand_brief: Dict):
    """
    Send message to MNS queue to trigger Stage 1 processing.
    
    Args:
        project_id: Project UUID
        brand_brief: Original brand brief data
    """
    # In production, this would send to MNS queue
    # For now, we'll import and call directly
    from .stage1_dna import process_stage1
    
    # Async processing would be:
    # mns_client.send_message({
    #     'project_id': project_id,
    #     'stage': 1,
    #     'brand_brief': brand_brief
    # })
    
    # Direct call for synchronous flow
    process_stage1(project_id, brand_brief)
