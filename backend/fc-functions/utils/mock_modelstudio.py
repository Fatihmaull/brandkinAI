"""
BrandKin AI - Mock Model Studio Client for Local Development
Simulates AI responses without requiring real API keys
"""

import json
import uuid
import random
from typing import Dict, List, Optional
from datetime import datetime


class MockModelStudioClient:
    """Mock client that simulates Model Studio API responses."""
    
    def __init__(self):
        self.call_count = 0
    
    def call_qwen_max(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> Dict:
        """Mock Qwen-Max text generation."""
        self.call_count += 1
        
        # Extract the prompt content
        prompt = messages[-1].get('content', '') if messages else ''
        
        # Generate mock responses based on prompt type
        if 'brand DNA' in prompt.lower() or 'brand_dna' in prompt.lower():
            content = self._generate_mock_brand_dna()
        elif 'mascot' in prompt.lower():
            content = self._generate_mock_mascot_prompt()
        elif 'avatar' in prompt.lower():
            content = self._generate_mock_avatar_prompt()
        elif 'pose' in prompt.lower() or 'action' in prompt.lower():
            content = self._generate_mock_pose_prompt()
        elif 'react' in prompt.lower() or 'component' in prompt.lower():
            content = self._generate_mock_react_component()
        elif 'revision' in prompt.lower() or 'refine' in prompt.lower():
            content = self._generate_mock_revision()
        elif 'brand copy' in prompt.lower() or 'copywriting' in prompt.lower():
            content = self._generate_mock_brand_copy()
        else:
            content = self._generate_generic_response(prompt)
        
        return {
            'output': {
                'choices': [{
                    'message': {
                        'content': content
                    }
                }]
            },
            'usage': {
                'input_tokens': len(prompt) // 4,
                'output_tokens': len(content) // 4
            }
        }
    
    def call_qwen_coder_plus(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Mock Qwen-Coder-Plus code generation."""
        self.call_count += 1
        
        return {
            'output': {
                'choices': [{
                    'message': {
                        'content': self._generate_mock_react_component()
                    }
                }]
            },
            'usage': {
                'input_tokens': len(prompt) // 4,
                'output_tokens': 500
            }
        }
    
    def call_wanx_v1(self, prompt: str, seed: int = 42, size: str = '1024*1024') -> Dict:
        """Mock Wanx image generation - returns placeholder image URLs."""
        self.call_count += 1
        
        # Generate deterministic "image URLs" based on prompt hash
        prompt_hash = hash(prompt + str(seed)) % 10000
        
        # Return SVG data URL as placeholder
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
            <rect width="600" height="600" fill="#4F46E5"/>
            <text x="300" y="280" font-family="Arial" font-size="32" fill="white" text-anchor="middle">AI Generated</text>
            <text x="300" y="330" font-family="Arial" font-size="48" fill="white" text-anchor="middle">Mascot {prompt_hash}</text>
            <text x="300" y="380" font-family="Arial" font-size="20" fill="#E0E0E0" text-anchor="middle">(Mock Mode)</text>
        </svg>'''
        import base64
        svg_base64 = base64.b64encode(svg_content.encode()).decode()
        data_url = f"data:image/svg+xml;base64,{svg_base64}"
        
        return {
            'output': {
                'results': [{
                    'url': data_url,
                    'seed': seed
                }]
            }
        }
    
    def call_image_segmentation(self, image_url: str) -> str:
        """Mock image segmentation for background removal."""
        self.call_count += 1
        # Return original URL in mock mode
        return image_url
    
    def _generate_mock_brand_dna(self) -> str:
        """Generate mock brand DNA JSON."""
        return json.dumps({
            'brand_name': 'TechVision',
            'industry': 'Technology',
            'core_values': ['Innovation', 'Trust', 'Simplicity'],
            'personality_traits': ['Professional', 'Friendly', 'Forward-thinking'],
            'visual_style': 'Modern minimalist with blue accents',
            'color_palette': {
                'primary': '#2563EB',
                'secondary': '#10B981',
                'accent': '#F59E0B'
            },
            'mascot_concept': 'A friendly robot character with glowing eyes',
            'target_audience': 'Tech-savvy professionals aged 25-45'
        }, indent=2)
    
    def _generate_mock_mascot_prompt(self) -> str:
        """Generate mock mascot generation prompt."""
        return json.dumps({
            'prompt': 'A friendly robot mascot character, full body shot, standing pose, blue and white color scheme, modern minimalist design, clean background, professional 3D render style, soft lighting',
            'negative_prompt': 'blurry, low quality, distorted, multiple characters, text, watermark'
        })
    
    def _generate_mock_avatar_prompt(self) -> str:
        """Generate mock avatar generation prompt."""
        return json.dumps({
            'prompt': 'Portrait headshot of a friendly robot character, blue glowing eyes, modern minimalist design, professional lighting, clean background, facing camera directly',
            'negative_prompt': 'blurry, low quality, distorted, multiple faces, text, watermark, profile view'
        })
    
    def _generate_mock_pose_prompt(self) -> str:
        """Generate mock pose variation prompt."""
        return json.dumps({
            'poses': [
                {'name': 'waving', 'prompt': 'Robot mascot waving hello, friendly expression'},
                {'name': 'thinking', 'prompt': 'Robot mascot in thinking pose, hand on chin'},
                {'name': 'celebrating', 'prompt': 'Robot mascot celebrating with arms raised'},
                {'name': 'pointing', 'prompt': 'Robot mascot pointing to the side'}
            ]
        })
    
    def _generate_mock_react_component(self) -> str:
        """Generate mock React component code."""
        return '''{
  "component_name": "BrandMascot",
  "react_code": "import React from 'react';\\n\\nexport const BrandMascot = ({ pose = 'default', size = 200 }) => {\\n  return (\\n    <img\\n      src={`/assets/mascot-${pose}.png`}\\n      alt=\\"Brand Mascot\\"\\n      style={{ width: size, height: size }}\\n    />\\n  );\\n};",
  "css_keyframes": "@keyframes mascotWave {\\n  0%, 100% { transform: rotate(0deg); }\\n  50% { transform: rotate(20deg); }\\n}",
  "usage_snippet": "<BrandMascot pose=\\"waving\\" size={150} />"
}'''
    
    def _generate_mock_revision(self) -> str:
        """Generate mock revision response."""
        return json.dumps({
            'revised_prompt': 'Updated mascot with brighter colors and more friendly expression',
            'changes_made': ['Increased color saturation', 'Adjusted eye size for warmth', 'Added subtle smile'],
            'reasoning': 'Made character more approachable while maintaining professional appearance'
        })
    
    def _generate_mock_brand_copy(self) -> str:
        """Generate mock brand copy."""
        return json.dumps({
            'tagline': 'Innovation Made Simple',
            'mission_statement': 'To empower businesses with cutting-edge technology solutions that drive growth and efficiency.',
            'value_proposition': 'We combine expertise with innovation to deliver solutions that matter.',
            'key_messages': [
                'Transform your business with smart technology',
                'Reliable solutions for modern challenges',
                'Your success is our mission'
            ],
            'tone_of_voice': 'Professional yet approachable, confident but not arrogant'
        }, indent=2)
    
    def _generate_generic_response(self, prompt: str) -> str:
        """Generate generic mock response."""
        return json.dumps({
            'response': f'Mock response for: {prompt[:50]}...',
            'timestamp': datetime.now().isoformat(),
            'mock': True
        })


# Global mock client instance
mock_modelstudio_client = MockModelStudioClient()
