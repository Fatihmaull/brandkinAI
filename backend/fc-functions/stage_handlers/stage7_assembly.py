"""
BrandKin AI - Stage 7: Brand Kit Assembly
Generate brand copy, LinkedIn banner, ZIP all assets, create signed download URL.
"""

import json
import uuid
import zipfile
import io
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List

from utils.database import db
from utils.ai_client import ai_client, DEFAULT_SEED
from utils.oss_handler import oss_handler
from prompts.stage_prompts import prompts


def download_image_from_url(url: str) -> bytes:
    """Download image data from a URL."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to download image from {url}: {response.status_code}")
            return b''
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return b''


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Stage 7 Handler: Assemble final brand kit.
    
    Triggered when user confirms they're satisfied with assets.
    
    Args:
        event: Trigger event with project_id
        context: FC context
    
    Returns:
        Processing result with download URL
    """
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        project_id = body.get('project_id')
        
        if not project_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing project_id'})
            }
        
        result = process_assembly(project_id)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def process_assembly(project_id: str) -> Dict[str, Any]:
    """
    Process Stage 7: Assemble complete brand kit.
    
    Args:
        project_id: Project UUID
    
    Returns:
        Assembly result with download URL
    """
    generation_id = str(uuid.uuid4())
    
    # Update project status
    db.update_project_status(project_id, 'processing', stage=7)
    
    # Get project data
    project = db.get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    
    brand_dna = project.get('brand_brief', {})
    
    # Create generation tracking
    db.create_generation(generation_id, project_id, 7, {})
    
    try:
        # Step 1: Generate brand copy
        brand_copy = generate_brand_copy(brand_dna)
        
        # Step 2: Generate LinkedIn banner
        banner_url = generate_linkedin_banner(project_id, brand_dna)
        
        # Step 3: Get all project assets
        assets = db.get_project_assets(project_id)
        code_exports = db.get_code_exports(project_id)
        
        # Step 4: Create ZIP archive
        zip_data = create_brand_kit_zip(
            project_id, assets, code_exports, brand_copy, banner_url
        )
        
        # Step 5: Upload ZIP to OSS (or save locally in mock mode)
        zip_oss_key = f"projects/{project_id}/brandkit_{project_id}.zip"
        zip_oss_url = oss_handler.upload_data(zip_data, zip_oss_key)
        
        # Step 6: Generate signed URL (24h TTL)
        # In mock mode, create a local file and return API download URL
        if hasattr(oss_handler, 'use_mock') and oss_handler.use_mock:
            import os
            local_storage = os.path.join(os.path.dirname(__file__), '..', '..', 'local_storage')
            os.makedirs(local_storage, exist_ok=True)
            local_zip_path = os.path.join(local_storage, f"brandkit_{project_id}.zip")
            with open(local_zip_path, 'wb') as f:
                f.write(zip_data)
            # Return API download URL
            signed_url = f"http://localhost:5000/api/v1/download/{project_id}"
        else:
            signed_url = oss_handler.get_signed_url(zip_oss_key, expiration_hours=24)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Step 7: Save brand kit record
        kit_id = str(uuid.uuid4())
        db.save_brand_kit(kit_id, project_id, zip_oss_url, signed_url, expires_at)
        
        # Complete generation
        db.complete_generation(generation_id, {
            'kit_id': kit_id,
            'asset_count': len(assets),
            'code_export_count': len(code_exports)
        })
        
        # Mark project as completed
        db.update_project_status(project_id, 'completed', stage=7)
        
        import base64
        return {
            'success': True,
            'project_id': project_id,
            'stage': 7,
            'brand_kit': {
                'kit_id': kit_id,
                'download_url': signed_url,
                'expires_at': expires_at.isoformat(),
                'contents': {
                    'assets': len(assets),
                    'code_exports': len(code_exports),
                    'brand_copy': True,
                    'banner': True
                }
            },
            'zip_data': base64.b64encode(zip_data).decode('utf-8')
        }
        
    except Exception as e:
        db.update_project_status(project_id, 'failed', stage=7, error=str(e))
        db.complete_generation(generation_id, error=str(e))
        raise


def generate_brand_copy(brand_dna: Dict) -> Dict[str, Any]:
    """
    Generate brand copy using qwen-max.
    
    Args:
        brand_dna: Brand DNA data
    
    Returns:
        Brand copy package
    """
    prompt_config = prompts.stage7_brand_copy_generation()
    
    user_prompt = f"""Generate complete brand copy package for this brand:

{json.dumps(brand_dna, indent=2)}

Create compelling brand copy following the required JSON format."""
    
    return ai_client.call_qwen_max(
        system_prompt=prompt_config['system_prompt'],
        user_prompt=user_prompt,
        temperature=0.8,
        max_tokens=2000
    )


def generate_linkedin_banner(project_id: str, brand_dna: Dict) -> str:
    """
    Generate LinkedIn banner background.
    
    Args:
        project_id: Project UUID
        brand_dna: Brand DNA for styling
    
    Returns:
        Banner OSS URL
    """
    # Generate banner prompt
    banner_prompt = prompts.stage7_linkedin_banner_prompt(brand_dna)
    
    # Generate with wanx-v1
    banner_url = ai_client.call_wanx_with_retry(
        prompt=banner_prompt,
        seed=DEFAULT_SEED,
        size="1024x1024"  # Use square format for wan2.2-t2i-flash compatibility
    )
    
    # Upload to OSS
    banner_oss_key = f"projects/{project_id}/linkedin_banner.png"
    return oss_handler.upload_with_retry(banner_url, banner_oss_key)


def create_brand_kit_zip(
    project_id: str,
    assets: List[Dict],
    code_exports: List[Dict],
    brand_copy: Dict,
    banner_url: str
) -> bytes:
    """
    Create ZIP archive with all brand kit contents.
    
    Args:
        project_id: Project UUID
        assets: List of asset records
        code_exports: List of code export records
        brand_copy: Brand copy data
        banner_url: LinkedIn banner URL
    
    Returns:
        ZIP file as bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add assets
        for asset in assets:
            asset_type = asset.get('asset_type', 'asset')
            asset_id = asset.get('asset_id', 'unknown')
            
            # Download and add original image from URL
            if asset.get('oss_url'):
                try:
                    image_data = download_image_from_url(asset['oss_url'])
                    if image_data:
                        zip_file.writestr(f"assets/{asset_type}_{asset_id}.png", image_data)
                        print(f"Added asset {asset_id} to ZIP")
                    else:
                        print(f"Skipping asset {asset_id}: no image data")
                except Exception as e:
                    print(f"Failed to add asset {asset_id}: {e}")
            
            # Download and add transparent image from URL
            if asset.get('transparent_url'):
                try:
                    image_data = download_image_from_url(asset['transparent_url'])
                    if image_data:
                        zip_file.writestr(f"assets/{asset_type}_{asset_id}_transparent.png", image_data)
                        print(f"Added transparent asset {asset_id} to ZIP")
                    else:
                        print(f"Skipping transparent asset {asset_id}: no image data")
                except Exception as e:
                    print(f"Failed to add transparent asset {asset_id}: {e}")
        
        # Add code exports
        for export in code_exports:
            component_name = export.get('component_name', 'Component')
            
            if export.get('react_code'):
                zip_file.writestr(
                    f"code/{component_name}.jsx",
                    export['react_code'].encode('utf-8')
                )
            
            if export.get('css_keyframes'):
                zip_file.writestr(
                    f"code/{component_name}.css",
                    export['css_keyframes'].encode('utf-8')
                )
            
            if export.get('usage_snippet'):
                zip_file.writestr(
                    f"code/{component_name}_usage.md",
                    export['usage_snippet'].encode('utf-8')
                )
        
        # Add brand copy
        zip_file.writestr(
            "brand_copy.json",
            json.dumps(brand_copy, indent=2).encode('utf-8')
        )
        
        # Add LinkedIn banner
        if banner_url:
            try:
                banner_data = download_image_from_url(banner_url)
                if banner_data:
                    zip_file.writestr("assets/linkedin_banner.png", banner_data)
                    print(f"Added banner to ZIP")
                else:
                    print(f"Skipping banner: no image data")
            except Exception as e:
                print(f"Failed to add banner: {e}")
        
        # Add README
        readme = f"""# BrandKit - {project_id}

This brand kit contains all assets generated for your brand.

## Contents
- `/assets/` - All visual assets (mascot, avatar, poses, banner)
- `/code/` - React components and CSS
- `brand_copy.json` - Brand messaging and copy

## Usage
Import the React components from `/code/` into your project.
Use assets from `/assets/` for marketing materials.

Generated by BrandKin AI
"""
        zip_file.writestr("README.md", readme.encode('utf-8'))
    
    zip_buffer.seek(0)
    return zip_buffer.read()
