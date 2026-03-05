"""
BrandKin AI - Unified AI Client
Stages 1-7: Client for Model Studio (Alibaba Cloud International)

Implements retry logic, error handling, and seed consistency (Seed 42).
Uses Model Studio API with OpenAI-compatible endpoints.
"""

import json
import re
import time
import os
import logging
import requests
import base64
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# CRITICAL: Consistency Rule - Seed 42 for ALL visual generation
DEFAULT_SEED = 42
MAX_RETRIES = 3


class AIClient:
    """Unified client for all AI models using Model Studio API.
    
    Requires MODELSTUDIO_API_KEY environment variable.
    Uses DashScope International (OpenAI-compatible) endpoints.
    """
    
    def __init__(self):
        self.api_key = os.environ.get('MODELSTUDIO_API_KEY', '')
        if not self.api_key:
            logger.warning("MODELSTUDIO_API_KEY not set — AI calls will fail")
        
        self.base_url = os.environ.get(
            'MODELSTUDIO_BASE_URL',
            'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'
        )
        
        # Model mappings
        self.models = {
            'qwen-max': os.environ.get('MODEL_TEXT', 'qwen-max'),
            'qwen-coder': os.environ.get('MODEL_CODE', 'qwen-max'),
            'image-gen': os.environ.get('MODEL_IMAGE', 'wan2.5-t2i-preview'),
        }
        
        logger.info("AI Client initialized (Model Studio)")
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """Make API request to Model Studio using OpenAI-compatible format."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - Response: {e.response.text[:500]}"
            raise Exception(f"Model Studio API error: {error_msg}")
    
    def call_qwen_max(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        result_format: str = "message"
    ) -> Dict[str, Any]:
        """Call qwen-max for brand DNA analysis and logic tasks."""
        model_name = self.models.get('qwen-max', 'qwen-max')
        
        payload = {
            'model': model_name,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        response = self._make_request('chat/completions', payload)
        
        if 'choices' in response:
            content = response['choices'][0]['message']['content']
            return self._safe_parse_json(content)
        
        raise Exception("Invalid response from Model Studio API")
    
    def call_qwen_coder_plus(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Call qwen-coder for code generation."""
        model_name = self.models.get('qwen-coder', 'qwen-max')
        
        payload = {
            'model': model_name,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        response = self._make_request('chat/completions', payload)
        
        if 'choices' in response:
            content = response['choices'][0]['message']['content']
            return self._safe_parse_json(content)
        
        raise Exception("Invalid response from Model Studio API")
    
    def call_wanx_v1(
        self,
        prompt: str,
        seed: int = DEFAULT_SEED,
        size: str = "1024x1024",
        n: int = 1
    ) -> str:
        """Call image generation model using Model Studio async API.
        
        CRITICAL: Uses seed=42 for mascot/avatar consistency.
        """
        if seed != DEFAULT_SEED:
            logger.warning(f"Seed changed from {DEFAULT_SEED} to {seed}")
        
        model_name = self.models.get('image-gen', 'wan2.5-t2i-preview')
        
        # Normalize size format (API uses * separator)
        if 'x' in size:
            size = size.replace('x', '*')
        
        # Valid sizes for wan2.5 image generation
        valid_sizes = [
            '512*512', '768*768', '1024*1024', '1280*1280',
            '512*1024', '768*1024', '1024*768', '1024*512'
        ]
        if size not in valid_sizes:
            logger.warning(f"Size {size} may not be valid, using 1024*1024")
            size = '1024*1024'
        
        # Use async image synthesis API
        payload = {
            'model': model_name,
            'input': {
                'prompt': prompt
            },
            'parameters': {
                'seed': seed,
                'n': n,
                'size': size
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-DashScope-Async': 'enable'
        }
        
        try:
            response = requests.post(
                'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'output' in result and 'task_id' in result['output']:
                    task_id = result['output']['task_id']
                    logger.info(f"Image task submitted: {task_id}")
                    return self._poll_image_task(task_id)
                elif 'output' in result and 'results' in result['output']:
                    return result['output']['results'][0]['url']
            else:
                logger.error(f"Image generation failed: {response.status_code} - {response.text[:300]}")
                
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
        
        # Fallback to SVG placeholder
        return self._generate_placeholder(prompt, seed)
    
    def _poll_image_task(self, task_id: str, max_attempts: int = 60) -> str:
        """Poll for async image generation task result."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f'https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}',
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get('output', {}).get('task_status', '')
                    
                    if status == 'SUCCEEDED':
                        results = result['output'].get('results', [])
                        if results:
                            url = results[0].get('url')
                            logger.info(f"Image task {task_id} completed")
                            return url
                        raise Exception("Task succeeded but no results")
                    elif status == 'FAILED':
                        error_msg = result.get('output', {}).get('message', 'Unknown error')
                        raise Exception(f"Image task failed: {error_msg}")
                    
                    # Still processing
                    time.sleep(3)
                else:
                    time.sleep(3)
                    
            except Exception as e:
                if 'failed' in str(e).lower() or 'succeeded' in str(e).lower():
                    raise
                logger.warning(f"Poll attempt {attempt + 1} error: {e}")
                time.sleep(3)
        
        raise Exception("Image task polling timed out")
    
    def call_wanx_with_retry(
        self,
        prompt: str,
        seed: int = DEFAULT_SEED,
        size: str = "1024x1024",
        max_retries: int = MAX_RETRIES
    ) -> str:
        """Call image generation with retry logic."""
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                return self.call_wanx_v1(prompt, seed, size)
            except Exception as e:
                last_error = e
                logger.warning(f"Image gen attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        logger.error("All retries failed, using placeholder")
        return self._generate_placeholder(prompt, seed)
    
    def remove_background(self, image_url: str) -> str:
        """Remove background from image.
        
        TODO: Implement using image segmentation model when available.
        Currently returns the original URL.
        """
        return image_url
    
    def _generate_placeholder(self, prompt: str, seed: int) -> str:
        """Generate SVG placeholder image when API is unavailable."""
        prompt_hash = hash(prompt + str(seed)) % 10000
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
            <rect width="600" height="600" fill="#4F46E5"/>
            <text x="300" y="280" font-family="Arial" font-size="32" fill="white" text-anchor="middle">AI Generated</text>
            <text x="300" y="330" font-family="Arial" font-size="48" fill="white" text-anchor="middle">Mascot {prompt_hash}</text>
            <text x="300" y="380" font-family="Arial" font-size="20" fill="#E0E0E0" text-anchor="middle">(Model API unavailable)</text>
        </svg>'''
        svg_base64 = base64.b64encode(svg_content.encode()).decode()
        return f"data:image/svg+xml;base64,{svg_base64}"
    
    def _safe_parse_json(self, content: str) -> Any:
        """Safely parse JSON content, return raw string if parsing fails."""
        try:
            if '```json' in content:
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
            
            if '```' in content:
                code_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
                if code_match:
                    try:
                        return json.loads(code_match.group(1))
                    except json.JSONDecodeError:
                        pass
            
            return json.loads(content)
        except json.JSONDecodeError:
            return content


# Global client instance
ai_client = AIClient()
