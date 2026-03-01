"""
BrandKin AI - Stage 6: Revision Handler
Handle user revision requests and regenerate assets.
"""

import json
import uuid
from typing import Dict, Any

from utils.database import db
from utils.dashscope_client import dashscope_client, DEFAULT_SEED
from utils.oss_handler import oss_handler
from prompts.stage_prompts import prompts


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 6 Handler: Process revision request.
    
    API Endpoint: POST /api/v1/projects/{id}/revise
    
    Args:
        event: HTTP request with revision feedback
        context: FC context
    
    Returns:
        Processing result with regenerated asset
    """
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        path_params = event.get('pathParameters', {})
        project_id = path_params.get('id') or body.get('project_id')
        
        asset_id = body.get('asset_id')
        revision_feedback = body.get('feedback')
        asset_type = body.get('type', 'mascot')  # mascot, avatar, or pose
        
        if not all([project_id, asset_id, revision_feedback]):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Missing project_id, asset_id, or feedback'})
            }
        
        result = process_revision(project_id, asset_id, revision_feedback, asset_type)
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


def process_revision(
    project_id: str,
    asset_id: str,
    revision_feedback: str,
    asset_type: str
) -> Dict[str, Any]:
    """
    Process revision request and regenerate asset.
    
    Args:
        project_id: Project UUID
        asset_id: Asset to revise
        revision_feedback: User's revision request
        asset_type: Type of asset being revised
    
    Returns:
        Revision result with new asset
    """
    generation_id = str(uuid.uuid4())
    
    # Update project status
    db.update_project_status(project_id, 'processing', stage=6)
    
    # Get project data
    project = db.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    
    # Get original asset
    assets = db.get_project_assets(project_id, asset_type)
    original_asset = next((a for a in assets if a['asset_id'] == asset_id), None)
    
    if not original_asset:
        raise ValueError(f"Asset {asset_id} not found")
    
    # Create generation tracking
    db.create_generation(generation_id, project_id, 6, {
        'original_asset_id': asset_id,
        'revision_feedback': revision_feedback
    })
    
    try:
        # Get revision prompt config
        prompt_config = prompts.stage6_revision_prompt()
        
        # Prepare revision prompt
        user_prompt = f"""Revise this image generation prompt based on user feedback:

Original Prompt: {original_asset.get('metadata', {}).get('prompt', '')}
Asset Type: {asset_type}
User Feedback: {revision_feedback}

Generate an improved prompt addressing the feedback while maintaining brand consistency."""
        
        # Get revised prompt from qwen-max
        revision_data = dashscope_client.call_qwen_max(
            system_prompt=prompt_config['system_prompt'],
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        revised_prompt = revision_data.get('revised_prompt', '')
        
        # Generate new asset with revised prompt
        # Use seed=42 + 1 to maintain consistency but allow variation
        new_asset_id = str(uuid.uuid4())
        
        db.create_asset(
            new_asset_id, project_id, asset_type, 6,
            metadata={
                'prompt': revised_prompt,
                'revision_of': asset_id,
                'feedback': revision_feedback,
                'changes': revision_data.get('changes_made', [])
            }
        )
        
        # Generate with wanx-v1 (seed=42 for consistency)
        new_image_url = dashscope_client.call_wanx_with_retry(
            prompt=revised_prompt,
            seed=DEFAULT_SEED,
            size="1024*1024"
        )
        
        # Upload to OSS
        new_oss_key = f"projects/{project_id}/{asset_type}_revised_{new_asset_id}.png"
        new_oss_url = oss_handler.upload_with_retry(new_image_url, new_oss_key)
        
        # Remove background
        new_transparent_url = dashscope_client.remove_background(new_image_url)
        new_transparent_oss_key = f"projects/{project_id}/{asset_type}_revised_{new_asset_id}_transparent.png"
        new_transparent_oss_url = oss_handler.upload_with_retry(
            new_transparent_url, new_transparent_oss_key
        )
        
        # Update asset
        db.update_asset_urls(
            new_asset_id,
            oss_url=new_oss_url,
            transparent_url=new_transparent_oss_url
        )
        
        # Complete generation
        db.complete_generation(generation_id, {
            'new_asset_id': new_asset_id,
            'changes_made': revision_data.get('changes_made', [])
        })
        
        # Update project status back to awaiting_selection
        db.update_project_status(project_id, 'awaiting_selection', stage=6)
        
        return {
            'success': True,
            'project_id': project_id,
            'stage': 6,
            'revision': {
                'original_asset_id': asset_id,
                'new_asset_id': new_asset_id,
                'changes_made': revision_data.get('changes_made', []),
                'conservation_notes': revision_data.get('conservation_notes', ''),
                'oss_url': new_oss_url,
                'transparent_url': new_transparent_oss_url
            }
        }
        
    except Exception as e:
        db.update_project_status(project_id, 'failed', stage=6, error=str(e))
        db.complete_generation(generation_id, error=str(e))
        raise
