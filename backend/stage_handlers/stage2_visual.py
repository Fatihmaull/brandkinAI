"""
BrandKin AI - Stage 2: Visual Generation
Uses qwen-max for prompt generation, then wanx-v1 for image generation.
CRITICAL: Uses seed=42 for mascot/avatar consistency.
"""

import json
import uuid
from typing import Dict, Any, List

from utils.database import db
from utils.ai_client import ai_client, DEFAULT_SEED
from utils.oss_handler import oss_handler
from prompts.stage_prompts import prompts


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 2 Handler: Generate mascot and avatar images.
    
    Args:
        event: Trigger event with project_id and brand_dna
        context: FC context
    
    Returns:
        Processing result with generated asset URLs
    """
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        project_id = body.get('project_id')
        brand_dna = body.get('brand_dna')
        
        if not project_id or not brand_dna:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing project_id or brand_dna'})
            }
        
        result = process_stage2(project_id, brand_dna)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_stage2(project_id: str, brand_dna: Dict) -> Dict[str, Any]:
    """
    Process Stage 2: Generate mascot and avatar images.
    
    Args:
        project_id: Project UUID
        brand_dna: Extracted brand DNA from Stage 1
    
    Returns:
        Generation result with asset URLs
    """
    generation_id = str(uuid.uuid4())
    
    # Update project status
    db.update_project_status(project_id, 'processing', stage=2)
    
    # Create generation tracking record
    db.create_generation(generation_id, project_id, 2, {
        'brand_dna': brand_dna
    })
    
    try:
        # Step 1: Generate optimized image prompts
        prompt_config = prompts.stage2_mascot_prompt_generation()
        
        user_prompt = f"""Generate optimized Wanx-v1 image prompts based on this brand DNA:

{json.dumps(brand_dna, indent=2)}

Create detailed prompts for mascot and avatar generation."""
        
        image_prompts = ai_client.call_qwen_max(
            system_prompt=prompt_config['system_prompt'],
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=1500
        )
        
        # Step 2: Generate mascot image with seed=42
        mascot_asset_id = str(uuid.uuid4())
        db.create_asset(
            mascot_asset_id, project_id, 'mascot', 2,
            metadata={'prompt': image_prompts.get('mascot_prompt', '')}
        )
        
        mascot_url = ai_client.call_wanx_with_retry(
            prompt=image_prompts.get('mascot_prompt', ''),
            seed=DEFAULT_SEED,  # CRITICAL: Consistency rule
            size="1024x1024"  # Use 'x' format for wan2.2-t2i-flash
        )
        
        # Use the generated image URL directly (already hosted on DashScope OSS)
        # For local development, we skip re-uploading to avoid access issues
        mascot_oss_url = mascot_url
        
        # Remove background from mascot (returns same URL for now)
        mascot_transparent_url = ai_client.remove_background(mascot_url)
        mascot_transparent_oss_url = mascot_transparent_url
        
        # Update mascot asset
        db.update_asset_urls(
            mascot_asset_id,
            oss_url=mascot_oss_url,
            transparent_url=mascot_transparent_oss_url
        )
        
        # Step 3: Generate avatar image with seed=42
        avatar_asset_id = str(uuid.uuid4())
        db.create_asset(
            avatar_asset_id, project_id, 'avatar', 2,
            metadata={'prompt': image_prompts.get('avatar_prompt', '')}
        )
        
        avatar_url = ai_client.call_wanx_with_retry(
            prompt=image_prompts.get('avatar_prompt', ''),
            seed=DEFAULT_SEED,  # CRITICAL: Consistency rule
            size="1024x1024"  # Use 'x' format for wan2.2-t2i-flash
        )
        
        # Use the generated image URL directly
        avatar_oss_url = avatar_url
        
        # Remove background from avatar (returns same URL for now)
        avatar_transparent_url = ai_client.remove_background(avatar_url)
        avatar_transparent_oss_url = avatar_transparent_url
        
        # Update avatar asset
        db.update_asset_urls(
            avatar_asset_id,
            oss_url=avatar_oss_url,
            transparent_url=avatar_transparent_oss_url
        )
        
        # Complete generation tracking
        db.complete_generation(generation_id, {
            'mascot_asset_id': mascot_asset_id,
            'avatar_asset_id': avatar_asset_id,
            'image_prompts': image_prompts
        })
        
        # Update project status - waiting for user selection
        db.update_project_status(project_id, 'awaiting_selection', stage=2)
        
        return {
            'success': True,
            'project_id': project_id,
            'stage': 2,
            'assets': {
                'mascot': {
                    'asset_id': mascot_asset_id,
                    'oss_url': mascot_oss_url,
                    'transparent_url': mascot_transparent_oss_url
                },
                'avatar': {
                    'asset_id': avatar_asset_id,
                    'oss_url': avatar_oss_url,
                    'transparent_url': avatar_transparent_oss_url
                }
            }
        }
        
    except Exception as e:
        db.update_project_status(project_id, 'failed', stage=2, error=str(e))
        db.complete_generation(generation_id, error=str(e))
        raise
