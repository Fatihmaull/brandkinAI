"""
BrandKin AI - Stage 1: Brand DNA Analysis
Uses qwen-max to analyze brand brief and extract structured DNA.
"""

import json
import uuid
from typing import Dict, Any

from utils.database import db
from utils.dashscope_client import dashscope_client
from prompts.stage_prompts import prompts


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 1 Handler: Process brand DNA analysis from MNS trigger.
    
    Args:
        event: MNS message with project_id and brand_brief
        context: FC context
    
    Returns:
        Processing result
    """
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        project_id = body.get('project_id')
        brand_brief = body.get('brand_brief')
        
        if not project_id or not brand_brief:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing project_id or brand_brief'})
            }
        
        result = process_stage1(project_id, brand_brief)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_stage1(project_id: str, brand_brief: Dict) -> Dict[str, Any]:
    """
    Process Stage 1: Brand DNA Analysis using qwen-max.
    
    Args:
        project_id: Project UUID
        brand_brief: Original brand brief data
    
    Returns:
        Analysis result with brand DNA
    """
    generation_id = str(uuid.uuid4())
    
    # Update project status
    db.update_project_status(project_id, 'processing', stage=1)
    
    # Create generation tracking record
    db.create_generation(generation_id, project_id, 1, {
        'brand_brief': brand_brief
    })
    
    try:
        # Get prompt configuration
        prompt_config = prompts.stage1_brand_dna_analysis()
        
        # Prepare user prompt from brand brief
        user_prompt = f"""Analyze the following brand brief and extract structured brand DNA:

Brand Brief:
{json.dumps(brand_brief, indent=2)}

Provide a comprehensive brand DNA analysis following the required JSON format."""
        
        # Call qwen-max
        brand_dna = dashscope_client.call_qwen_max(
            system_prompt=prompt_config['system_prompt'],
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=2048
        )
        
        # Store brand DNA in project metadata
        db.update_project_status(project_id, 'dna_analyzed', stage=1)
        
        # Complete generation tracking
        db.complete_generation(generation_id, {
            'brand_dna': brand_dna
        })
        
        # Trigger Stage 2
        trigger_stage2(project_id, brand_dna)
        
        return {
            'success': True,
            'project_id': project_id,
            'stage': 1,
            'brand_dna': brand_dna
        }
        
    except Exception as e:
        db.update_project_status(project_id, 'failed', stage=1, error=str(e))
        db.complete_generation(generation_id, error=str(e))
        raise


def trigger_stage2(project_id: str, brand_dna: Dict):
    """
    Trigger Stage 2: Image Prompt Generation.
    
    Args:
        project_id: Project UUID
        brand_dna: Extracted brand DNA
    """
    from .stage2_visual import process_stage2
    process_stage2(project_id, brand_dna)
