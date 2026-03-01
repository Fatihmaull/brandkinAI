"""
BrandKin AI - Model Studio Client (Alibaba Cloud International)
Alternative to DashScope for international users
Uses modelstudio.console.alibabacloud.com API
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class ModelStudioClient:
    """Client for Alibaba Cloud Model Studio API (International).
    
    Uses OpenAI-compatible endpoints:
    - Singapore: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    - Virginia: https://dashscope-us.aliyuncs.com/compatible-mode/v1
    """
    
    def __init__(self):
        self.api_key = os.getenv('MODELSTUDIO_API_KEY', '')
        # Use OpenAI-compatible endpoint for Singapore region
        self.base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        
        # Model mappings for Model Studio (OpenAI-compatible names)
        # Try different model names based on availability
        self.models = {
            'qwen-max': 'qwen3-max',  # Latest version
            'qwen-coder-plus': 'qwen3-coder-plus',
            'wanx-v1': 'wanx-v1',
            'qwen-vl-plus': 'qwen3-vl-plus'
        }
    
    def _make_request(self, endpoint: str, payload: Dict) -> Dict:
        """Make API request to Model Studio using OpenAI-compatible format."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e.response, 'text'):
                error_msg += f" - Response: {e.response.text}"
            raise Exception(f"Model Studio API error: {error_msg}")
    
    def call_qwen_max(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        result_format: str = "message"
    ) -> Dict[str, Any]:
        """Call qwen-max for text generation using OpenAI-compatible endpoint."""
        # Try different model names in order of preference
        model_names = ['qwen3-max', 'qwen-max', 'qwen-plus', 'qwen-turbo']
        
        for model_name in model_names:
            try:
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
                    
            except Exception as e:
                if 'AccessDenied' in str(e) or 'Unpurchased' in str(e):
                    continue  # Try next model
                raise  # Re-raise other errors
        
        raise Exception(f"No available qwen model found. Please check your Model Studio subscription.")
    
    def call_qwen_coder_plus(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Call qwen-coder-plus for code generation using OpenAI-compatible endpoint."""
        # Try different coder model names
        model_names = ['qwen3-coder-plus', 'qwen-coder-plus', 'qwen3-max', 'qwen-max']
        
        for model_name in model_names:
            try:
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
                    
            except Exception as e:
                if 'AccessDenied' in str(e) or 'Unpurchased' in str(e):
                    continue
                raise
        
        raise Exception(f"No available coder model found. Please check your Model Studio subscription.")
    
    def call_wanx_v1(
        self,
        prompt: str,
        seed: int = 42,
        size: str = "1024*1024",
        n: int = 1
    ) -> str:
        """Call wanx-v1 for image generation.
        
        Note: Wanx may not be available through OpenAI-compatible endpoint.
        Falls back to placeholder images for now.
        """
        # For now, return placeholder image since wanx might not be available
        # through the OpenAI-compatible endpoint
        prompt_hash = hash(prompt + str(seed)) % 10000
        return f'https://placehold.co/600x600/png?text=AI+Generated+Mascot+{prompt_hash}'
    
    def _poll_wanx_task(self, task_id: str, max_attempts: int = 30) -> str:
        """Poll for Wanx image generation task completion."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        for attempt in range(max_attempts):
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('output', {}).get('task_status') == 'SUCCEEDED':
                results = result['output'].get('results', [])
                if results:
                    return results[0].get('url')
            
            import time
            time.sleep(2)
        
        raise Exception(f"Wanx task {task_id} timed out")
    
    def call_image_segmentation(self, image_url: str) -> str:
        """Call image segmentation for background removal."""
        payload = {
            'model': 'image-segmentation',
            'input': {
                'image': image_url
            }
        }
        
        response = self._make_request('services/aigc/image-segmentation/generation', payload)
        
        if 'output' in response and 'results' in response['output']:
            return response['output']['results'][0].get('url', image_url)
        
        return image_url
    
    def _safe_parse_json(self, content: str) -> Any:
        """Safely parse JSON content, return raw string if parsing fails."""
        try:
            # Try to extract JSON from markdown code blocks
            if '```json' in content:
                json_match = content.split('```json')[1].split('```')[0].strip()
                return json.loads(json_match)
            elif '```' in content:
                json_match = content.split('```')[1].split('```')[0].strip()
                return json.loads(json_match)
            else:
                return json.loads(content)
        except (json.JSONDecodeError, IndexError):
            return content


# Singleton instance
modelstudio_client = ModelStudioClient()
