"""
BrandKin AI - Stage 5: Code Export
Generate React components using qwen-coder-plus.
"""

import json
import uuid
from typing import Dict, Any

from utils.database import db
from utils.ai_client import ai_client
from prompts.stage_prompts import prompts


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 5 Handler: Generate React component for selected character.
    
    Args:
        event: Trigger event with project_id, selected_asset, brand_dna
        context: FC context
    
    Returns:
        Processing result with generated code
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
        
        result = process_stage5(project_id, selected_asset, brand_dna)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_stage5(project_id: str, selected_asset: Dict, brand_dna: Dict) -> Dict[str, Any]:
    """
    Process Stage 5: Generate React component using qwen-coder-plus.
    
    Args:
        project_id: Project UUID
        selected_asset: Selected character asset
        brand_dna: Brand DNA for context
    
    Returns:
        Generation result with React code
    """
    generation_id = str(uuid.uuid4())
    
    # Update project status
    db.update_project_status(project_id, 'processing', stage=5)
    
    # Create generation tracking record
    db.create_generation(generation_id, project_id, 5, {
        'selected_asset_id': selected_asset.get('asset_id')
    })
    
    try:
        # Get prompt configuration
        prompt_config = prompts.stage5_react_component_generation()
        
        # Extract brand colors
        colors = brand_dna.get('visual_style', {}).get('color_palette', {})
        primary_color = colors.get('primary', '#00FFFF')
        accent_color = colors.get('accent', '#FF6600')
        
        # Get brand story
        brand_story = brand_dna.get('brand_story', 'A unique brand with personality.')
        
        # Get mascot name from brand DNA
        mascot_name = brand_dna.get('mascot_concept', {}).get('character_type', 'Mascot')
        
        # Get image URL
        image_url = selected_asset.get('transparent_url') or selected_asset.get('oss_url', '')
        
        # Generate user prompt
        user_prompt = prompts.stage5_component_user_prompt(
            mascot_name=mascot_name,
            image_url=image_url,
            primary_color=primary_color,
            accent_color=accent_color,
            brand_story=brand_story
        )
        
        # Call qwen-coder-plus
        component_data = ai_client.call_qwen_coder_plus(
            system_prompt=prompt_config['system_prompt'],
            user_prompt=user_prompt,
            temperature=0.3,  # Lower temp for code
            max_tokens=4096
        )
        
        # Save code export to database
        export_id = str(uuid.uuid4())
        db.save_code_export(export_id, project_id, component_data)
        
        # Complete generation tracking
        db.complete_generation(generation_id, {
            'export_id': export_id,
            'component_name': component_data.get('component_name')
        })
        
        return {
            'success': True,
            'project_id': project_id,
            'stage': 5,
            'code_export': {
                'export_id': export_id,
                'component_name': component_data.get('component_name'),
                'react_code': component_data.get('react_code'),
                'css_keyframes': component_data.get('css_keyframes'),
                'usage_snippet': component_data.get('usage_snippet'),
                'dependencies': component_data.get('dependencies', [])
            }
        }
        
    except Exception as e:
        db.update_project_status(project_id, 'failed', stage=5, error=str(e))
        db.complete_generation(generation_id, error=str(e))
        raise
