"""
BrandKin AI - Stage 0: Project Initialization
Accepts brand_brief JSON, initializes project in RDS, triggers Stage 1.
"""

import json
import uuid
import logging
import threading
from typing import Dict, Any

from utils.database import db
from utils.credentials import get_mns_config

logger = logging.getLogger(__name__)


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
        # Defensive parsing: FC 3.0 may pass event as bytes, string, or dict
        if isinstance(event, (bytes, bytearray)):
            event = json.loads(event.decode('utf-8'))
        elif isinstance(event, str):
            event = json.loads(event)
        
        # Parse request body
        body_raw = event.get('body', '{}')
        if isinstance(body_raw, str):
            body = json.loads(body_raw) if body_raw else {}
        elif isinstance(body_raw, (bytes, bytearray)):
            body = json.loads(body_raw.decode('utf-8')) if body_raw else {}
        elif isinstance(body_raw, dict):
            body = body_raw
        else:
            body = {}

        
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
        logger.info(f"Project {project_id} created in database")
        
        # Trigger Stage 1 asynchronously (non-blocking)
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
        logger.error(f"Stage 0 failed: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }


def trigger_stage1(project_id: str, brand_brief: Dict):
    """
    Trigger Stage 1 processing in a background thread.
    
    In production, this would send a message to MNS queue.
    For local dev, we run it in a thread so the API returns immediately.
    """
    def _run_stage1():
        try:
            from .stage1_dna import process_stage1
            process_stage1(project_id, brand_brief)
        except Exception as e:
            logger.error(f"Stage 1 background processing failed for {project_id}: {e}", exc_info=True)
            try:
                db.update_project_status(project_id, 'failed', stage=1, error=str(e))
            except Exception:
                pass
    
    thread = threading.Thread(target=_run_stage1, daemon=True)
    thread.start()
    logger.info(f"Stage 1 triggered in background for project {project_id}")

