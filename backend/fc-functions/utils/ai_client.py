"""
BrandKin AI - Unified AI Client
Stages 1-7: Unified client for Model Studio (Alibaba Cloud International)

Implements retry logic, error handling, and seed consistency (Seed 42).
Uses Model Studio API with OpenAI-compatible endpoints.
"""

import json
import re
import time
import os
import requests
import base64
from typing import Dict, List, Optional, Any, Callable

# Import mock client for local development fallback
from .mock_modelstudio import mock_modelstudio_client

# CRITICAL: Consistency Rule - Seed 42 for ALL visual generation
DEFAULT_SEED = 42
MAX_RETRIES = 3


class AIClient:
    """Unified client for all AI models using Model Studio API.
    
    Supports:
    - Model Studio (Alibaba Cloud International) - Primary
    - Mock mode (local development fallback)
    """
    
    def __init__(self):
        # API Configuration
        self.api_key = os.getenv('MODELSTUDIO_API_KEY', 'sk-6a088b68d8ef46c180cbc84fd987aba9')
        self.base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        
        # Model mappings for Model Studio
        self.models = {
            'qwen-max': 'qwen3.5-122b-a10b',
            'qwen-coder': 'qwen3.5-122b-a10b',
            'wanx-v1': 'wan2.2-t2i-flash',
            'image-gen': 'wan2.2-t2i-flash',
        }
        
        # Check if we should use mock mode
        self.use_mock = os.getenv('AI_PROVIDER', 'modelstudio').lower() == 'mock'
        
        if self.use_mock:
            print("AI Client: Using mock mode for local development")
        else:
            print(f"AI Client: Using Model Studio with API key: {self.api_key[:10]}...")
    
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
        """Call qwen-max for brand DNA analysis and logic tasks."""
        if self.use_mock:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = mock_modelstudio_client.call_qwen_max(messages, temperature, max_tokens)
            content = response['output']['choices'][0]['message']['content']
            return self._safe_parse_json(content)
        
        model_name = self.models.get('qwen-max', 'qwen3.5-122b-a10b')
        
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
        """Call qwen-coder-plus for code generation."""
        if self.use_mock:
            response = mock_modelstudio_client.call_qwen_coder_plus(user_prompt, temperature)
            content = response['output']['choices'][0]['message']['content']
            return self._safe_parse_json(content)
        
        # Use the same model as qwen-max for code (qwen3.5 handles code well)
        model_name = self.models.get('qwen-coder', 'qwen3.5-122b-a10b')
        
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
        size: str = "1024x1024",  # Use 'x' format for wan2.2-t2i-flash
        n: int = 1
    ) -> str:
        """Call wanx-v1 for image generation using Model Studio API."""
        # Enforce consistency rule
        if seed != DEFAULT_SEED:
            print(f"Warning: Seed changed from {DEFAULT_SEED} to {seed}")
        
        if self.use_mock:
            response = mock_modelstudio_client.call_wanx_v1(prompt, seed, size)
            return response['output']['results'][0]['url']
        
        try:
            # Based on error messages, wan2.2-t2i-flash exists but requires async calls
            # Other models are not available in the subscription
            model_name = 'wan2.2-t2i-flash'
            
            print(f"Starting async image generation with model: {model_name}")
            
            # Use async API call (required for this model)
            # Validate and convert size format
            if '*' in size:
                size = size.replace('*', 'x')
            
            # Ensure size is valid (wan2.2-t2i-flash supports specific sizes)
            valid_sizes = ['512x512', '768x768', '1024x1024', '1440x1440', 
                          '512x1024', '768x1024', '1024x768', '1024x512']
            if size not in valid_sizes:
                print(f"Warning: Size {size} may not be valid, using 1024x1024")
                size = '1024x1024'
            
            # Build payload - wan2.2-t2i-flash may not support size parameter
            # Try without size first, only include seed
            payload = {
                'model': model_name,
                'input': {
                    'prompt': prompt
                },
                'parameters': {
                    'seed': seed,
                    'n': n
                }
            }
            
            print(f"DEBUG: Sending payload: {payload}")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-DashScope-Async': 'enable'  # Enable async mode
            }
            
            # Submit async task
            response = requests.post(
                'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
                headers=headers,
                json=payload,
                timeout=120
            )
            
            print(f"Submit response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Submit response: {result}")
                
                if 'output' in result and 'task_id' in result['output']:
                    task_id = result['output']['task_id']
                    print(f"Task submitted, ID: {task_id}")
                    return self._poll_image_task(task_id)
                elif 'output' in result and 'results' in result['output']:
                    # Sync response (unlikely for this model)
                    return result['output']['results'][0]['url']
            else:
                print(f"Failed to submit task: {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"Image generation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback to SVG placeholder
        return self._generate_placeholder(prompt, seed)
    
    def _poll_image_task(self, task_id: str, max_attempts: int = 60) -> str:
        """Poll for async image generation task result."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        
        print(f"Polling task {task_id}...")
        
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
                    
                    print(f"Task status: {status} (attempt {attempt + 1})")
                    
                    if status == 'SUCCEEDED':
                        results = result['output'].get('results', [])
                        if results:
                            url = results[0].get('url')
                            print(f"Task completed! Image URL: {url[:50]}...")
                            return url
                        else:
                            raise Exception("Task succeeded but no results")
                    elif status == 'FAILED':
                        error_msg = result.get('output', {}).get('message', 'Unknown error')
                        raise Exception(f"Task failed: {error_msg}")
                    
                    # Still processing, wait and retry
                    time.sleep(3)
                else:
                    print(f"Poll failed: {response.status_code} - {response.text}")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"Poll attempt {attempt + 1} error: {e}")
                time.sleep(3)
        
        raise Exception("Task polling timed out")
    
    def call_wanx_with_retry(
        self,
        prompt: str,
        seed: int = DEFAULT_SEED,
        size: str = "1024x1024",  # Use 'x' format for wan2.2-t2i-flash
        max_retries: int = MAX_RETRIES
    ) -> str:
        """Call wanx-v1 with retry logic."""
        for attempt in range(max_retries):
            try:
                return self.call_wanx_v1(prompt, seed, size)
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    print("All retries failed, using placeholder")
                    return self._generate_placeholder(prompt, seed)
    
    def remove_background(self, image_url: str) -> str:
        """Remove background from image using image-segmentation."""
        if self.use_mock:
            return mock_modelstudio_client.call_image_segmentation(image_url)
        
        # For now, return original image (background removal requires special handling)
        # TODO: Implement using qwen-image-edit-plus when available
        return image_url
    
    def _generate_placeholder(self, prompt: str, seed: int) -> str:
        """Generate SVG placeholder image."""
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
                    except:
                        pass
            
            return json.loads(content)
        except json.JSONDecodeError:
            return content


# Global client instance
ai_client = AIClient()
