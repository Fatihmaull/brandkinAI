"""
BrandKin AI - DashScope Client Wrapper
Stages 1-7: Unified client for qwen-max, qwen-coder-plus, and wanx-v1

Implements retry logic, error handling, and seed consistency (Seed 42).
"""

import json
import re
import time
import os
from typing import Dict, List, Optional, Any, Callable

# Try to import dashscope, fall back to mock if not available
try:
    import dashscope
    from dashscope import Generation, ImageSynthesis
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

try:
    from .credentials import get_dashscope_api_key
except ImportError:
    get_dashscope_api_key = None

# Import mock client for local development
from .mock_dashscope import mock_dashscope_client

# Import Model Studio client for international users
try:
    from .modelstudio_client import modelstudio_client
    MODELSTUDIO_AVAILABLE = True
except ImportError:
    MODELSTUDIO_AVAILABLE = False


# CRITICAL: Consistency Rule - Seed 42 for ALL visual generation
DEFAULT_SEED = 42
MAX_RETRIES = 3


class DashScopeClient:
    """Unified client for all DashScope AI models with mock fallback and Model Studio support."""
    
    def __init__(self):
        # Check which provider to use
        self.provider = os.getenv('AI_PROVIDER', 'mock').lower()  # 'dashscope', 'modelstudio', or 'mock'
        
        if self.provider == 'modelstudio' and MODELSTUDIO_AVAILABLE:
            self.use_mock = False
            self.use_modelstudio = True
            self.modelstudio = modelstudio_client
        elif self.provider == 'dashscope' and DASHSCOPE_AVAILABLE and get_dashscope_api_key:
            try:
                self.api_key = get_dashscope_api_key()
                dashscope.api_key = self.api_key
                self.use_mock = False
                self.use_modelstudio = False
            except Exception:
                self.use_mock = True
                self.use_modelstudio = False
        else:
            # Default to mock
            self.use_mock = True
            self.use_modelstudio = False
    
    def call_qwen_max(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        result_format: str = "message"
    ) -> Dict[str, Any]:
        """
        Call qwen-max for brand DNA analysis and logic tasks.
        
        Args:
            system_prompt: System role instructions
            user_prompt: User query/content
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
            result_format: Output format (message/text)
        
        Returns:
            Parsed JSON response or raw text
        """
        if self.use_modelstudio:
            return self.modelstudio.call_qwen_max(system_prompt, user_prompt, temperature, max_tokens, result_format)
        
        if self.use_mock:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = mock_dashscope_client.call_qwen_max(messages, temperature, max_tokens)
            content = response['output']['choices'][0]['message']['content']
            return self._safe_parse_json(content)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = Generation.call(
            model="qwen-max",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format=result_format
        )
        
        if response.status_code != 200:
            raise Exception(f"qwen-max API error: {response.message}")
        
        content = response.output.choices[0].message.content
        return self._safe_parse_json(content)
    
    def call_qwen_coder_plus(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Call qwen-coder-plus for React component generation.
        Lower temperature for more deterministic code output.
        
        Args:
            system_prompt: System role instructions for code generation
            user_prompt: Code generation requirements
            temperature: Lower for code (0.0-1.0)
            max_tokens: Maximum code length
        
        Returns:
            Parsed JSON containing component_name, react_code, css_keyframes, usage_snippet
        """
        if self.use_modelstudio:
            return self.modelstudio.call_qwen_coder_plus(system_prompt, user_prompt, temperature, max_tokens)
        
        if self.use_mock:
            response = mock_dashscope_client.call_qwen_coder_plus(user_prompt, temperature)
            content = response['output']['choices'][0]['message']['content']
            return self._safe_parse_json(content)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = Generation.call(
            model="qwen-coder-plus",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format="message"
        )
        
        if response.status_code != 200:
            raise Exception(f"qwen-coder-plus API error: {response.message}")
        
        content = response.output.choices[0].message.content
        return self._safe_parse_json(content)
    
    def call_wanx_v1(
        self,
        prompt: str,
        seed: int = DEFAULT_SEED,
        size: str = "1024*1024",
        n: int = 1
    ) -> str:
        """
        Call wanx-v1 for image generation.
        CRITICAL: Uses seed=42 for mascot/avatar consistency.
        
        Args:
            prompt: Image generation prompt
            seed: Random seed (MUST be 42 for consistency)
            size: Image dimensions (1024*1024, 1024*768, etc.)
            n: Number of images to generate
        
        Returns:
            URL of generated image
        """
        # Enforce consistency rule
        if seed != DEFAULT_SEED:
            print(f"Warning: Seed changed from {DEFAULT_SEED} to {seed}")
        
        if self.use_modelstudio:
            return self.modelstudio.call_wanx_v1(prompt, seed, size, n)
        
        if self.use_mock:
            response = mock_dashscope_client.call_wanx_v1(prompt, seed, size)
            return response['output']['results'][0]['url']
        
        response = ImageSynthesis.call(
            model="wanx-v1",
            prompt=prompt,
            seed=seed,
            size=size,
            n=n
        )
        
        if response.status_code != 200:
            raise WanxGenerationError(f"wanx-v1 API error: {response.message}")
        
        # Poll for task completion
        task_id = response.output.task_id
        return self._poll_wanx_task(task_id)
    
    def call_wanx_with_retry(
        self,
        prompt: str,
        seed: int = DEFAULT_SEED,
        size: str = "1024*1024",
        max_retries: int = MAX_RETRIES
    ) -> str:
        """
        Call wanx-v1 with retry logic for failure handling.
        On failure, increment seed slightly and retry.
        
        Args:
            prompt: Image generation prompt
            seed: Initial seed (default 42)
            size: Image dimensions (1024*1024, 1024*768, etc.)
            max_retries: Maximum retry attempts
        
        Returns:
            URL of generated image
        """
        for attempt in range(max_retries):
            try:
                current_seed = seed + attempt
                return self.call_wanx_v1(prompt, seed=current_seed, size=size)
            except WanxGenerationError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise
        
        raise WanxGenerationError(f"Failed after {max_retries} attempts")
    
    def remove_background(self, image_url: str) -> str:
        """
        Remove background from image using image-segmentation model.
        
        Args:
            image_url: URL of image to process
        
        Returns:
            URL of transparent PNG
        """
        # In mock mode, just return the original URL (no background removal)
        if self.use_mock or self.use_modelstudio:
            return image_url
        
        response = ImageSynthesis.call(
            model="image-segmentation",
            image=image_url
        )
        
        if response.status_code != 200:
            raise Exception(f"Segmentation API error: {response.message}")
        
        return response.output.image_url
    
    def _poll_wanx_task(self, task_id: str, timeout: int = 300) -> str:
        """
        Poll wanx-v1 task until completion.
        
        Args:
            task_id: Task ID from initial call
            timeout: Maximum wait time in seconds
        
        Returns:
            URL of generated image
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = ImageSynthesis.fetch(task_id)
            
            if response.status_code != 200:
                raise WanxGenerationError(f"Task fetch error: {response.message}")
            
            status = response.output.task_status
            
            if status == "SUCCEEDED":
                return response.output.results[0].url
            elif status == "FAILED":
                raise WanxGenerationError(f"Task failed: {response.output.message}")
            
            time.sleep(2)  # Poll every 2 seconds
        
        raise WanxGenerationError(f"Task timeout after {timeout}s")
    
    def _safe_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Safely parse JSON from model output, handling markdown backticks.
        
        Args:
            raw_text: Raw text output from model
        
        Returns:
            Parsed JSON dict
        """
        # Remove markdown code blocks
        clean = re.sub(r"```json|```", "", raw_text).strip()
        
        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            # Try to extract JSON from text
            json_match = re.search(r'\{.*\}', clean, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            raise JSONParseError(f"Failed to parse JSON: {e}\nRaw text: {raw_text[:200]}")


class WanxGenerationError(Exception):
    """Custom exception for Wanx generation failures."""
    pass


class JSONParseError(Exception):
    """Custom exception for JSON parsing failures."""
    pass


# Singleton instance
dashscope_client = DashScopeClient()
