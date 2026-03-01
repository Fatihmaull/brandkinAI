"""
BrandKin AI - Stage 4: Pose Pack Generation
Generate 5 pose variations using qwen-max for prompts and wanx-v1 for images.
Uses seed=42 for consistency with selected character.
"""

import json
import uuid
from typing import Dict, Any, List

from utils.database import db
from utils.dashscope_client import dashscope_client, DEFAULT_SEED
from utils.oss_handler import oss_handler
from prompts.stage_prompts import prompts


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 4 Handler: Generate pose pack for selected character.
    
    Args:
        event: Trigger event with project_id, selected_asset, brand_dna
        context: FC context
    
    Returns:
        Processing result with pose asset URLs
    """
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        project_id = body.get('project_id')
        selected_asset = body.get('selected_asset')
        brand_dna = body.get('brand_dna')
        
        if not all([project_id, selected_asset, brand_dna]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameters'})
            }
        
        result = process_stage4(project_id, selected_asset, brand_dna)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_stage4(project_id: str, selected_asset: Dict, brand_dna: Dict) -> Dict[str, Any]:
    """
    Process Stage 4: Generate 5 pose variations.
    
    Args:
        project_id: Project UUID
        selected_asset: Selected character asset
        brand_dna: Brand DNA for context
    
    Returns:
        Generation result with pose assets
    """
    generation_id = str(uuid.uuid4())
    
    # Update project status
    db.update_project_status(project_id, 'processing', stage=4)
    
    # Create generation tracking record
    db.create_generation(generation_id, project_id, 4, {
        'selected_asset_id': selected_asset.get('asset_id')
    })
    
    try:
        # Step 1: Generate pose prompts using qwen-max
        prompt_config = prompts.stage4_pose_generation()
        
        user_prompt = f"""Generate 5 pose variations for this character:

Character Description: {selected_asset.get('metadata', {}).get('prompt', 'Brand mascot character')}
Brand DNA: {json.dumps(brand_dna, indent=2)}

Create 5 distinct poses maintaining character consistency."""
        
        pose_data = dashscope_client.call_qwen_max(
            system_prompt=prompt_config['system_prompt'],
            user_prompt=user_prompt,
            temperature=0.8,
            max_tokens=2000
        )
        
        poses = pose_data.get('poses', [])
        consistency_addition = pose_data.get('consistency_prompt_addition', '')
        
        # Step 2: Generate each pose with wanx-v1 (seed=42)
        pose_assets = []
        
        for i, pose in enumerate(poses[:5]):  # Ensure max 5 poses
            pose_asset_id = str(uuid.uuid4())
            
            # Create asset record
            db.create_asset(
                pose_asset_id, project_id, 'pose', 4,
                metadata={
                    'pose_name': pose.get('pose_name', f'pose_{i+1}'),
                    'pose_description': pose.get('pose_description', ''),
                    'expression': pose.get('expression', ''),
                    'body_language': pose.get('body_language', '')
                }
            )
            
            # Build full prompt with consistency
            full_prompt = f"""{pose.get('pose_description', '')} 
{consistency_addition}
Same character, consistent style, matching the reference image.
Seed: {DEFAULT_SEED}"""
            
            # Generate pose image
            pose_url = dashscope_client.call_wanx_with_retry(
                prompt=full_prompt,
                seed=DEFAULT_SEED,  # CRITICAL: Consistency rule
                size="1024*1024"
            )
            
            # Upload to OSS
            pose_oss_key = f"projects/{project_id}/pose_{i+1}_{pose_asset_id}.png"
            pose_oss_url = oss_handler.upload_with_retry(pose_url, pose_oss_key)
            
            # Remove background
            pose_transparent_url = dashscope_client.remove_background(pose_url)
            pose_transparent_oss_key = f"projects/{project_id}/pose_{i+1}_{pose_asset_id}_transparent.png"
            pose_transparent_oss_url = oss_handler.upload_with_retry(
                pose_transparent_url, pose_transparent_oss_key
            )
            
            # Update asset
            db.update_asset_urls(
                pose_asset_id,
                oss_url=pose_oss_url,
                transparent_url=pose_transparent_oss_url
            )
            
            pose_assets.append({
                'asset_id': pose_asset_id,
                'pose_name': pose.get('pose_name', f'pose_{i+1}'),
                'oss_url': pose_oss_url,
                'transparent_url': pose_transparent_oss_url
            })
        
        # Complete generation tracking
        db.complete_generation(generation_id, {
            'pose_count': len(pose_assets),
            'pose_assets': [p['asset_id'] for p in pose_assets]
        })
        
        return {
            'success': True,
            'project_id': project_id,
            'stage': 4,
            'poses': pose_assets
        }
        
    except Exception as e:
        db.update_project_status(project_id, 'failed', stage=4, error=str(e))
        db.complete_generation(generation_id, error=str(e))
        raise
