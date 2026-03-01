"""
BrandKin AI - Mock DashScope Client for Local Development
Simulates AI responses without requiring real API keys
"""

import json
import uuid
import random
from typing import Dict, List, Optional
from datetime import datetime


class MockDashScopeClient:
    """Mock client that simulates DashScope API responses."""
    
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
    
    def call_wanx_v1(self, prompt: str, seed: int = 42, size: str = '1024*1024') -> Dict:
        """Mock Wanx image generation - returns placeholder image URLs."""
        self.call_count += 1
        
        # Generate deterministic "image URLs" based on prompt hash
        prompt_hash = hash(prompt + str(seed)) % 10000
        
        return {
            'output': {
                'results': [{
                    'url': f'https://placehold.co/600x600/png?text=Mascot+{prompt_hash}',
                    'seed': seed
                }]
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
            }
        }
    
    def call_image_segmentation(self, image_url: str) -> Dict:
        """Mock image segmentation for background removal."""
        self.call_count += 1
        
        return {
            'output': {
                'results': [{
                    'url': image_url.replace('placehold.co', 'placehold.co') + '&bg=transparent'
                }]
            }
        }
    
    def _generate_mock_brand_dna(self) -> str:
        """Generate mock brand DNA JSON."""
        return json.dumps({
            "brand_name": "TechFlow",
            "archetype": "Innovator",
            "personality_traits": ["Innovative", "Reliable", "Friendly"],
            "voice_tone": "Professional yet approachable",
            "color_palette": {
                "primary": "#0066FF",
                "secondary": "#00CC99",
                "accent": "#FF6B35"
            },
            "visual_style": "Modern, clean, tech-forward with rounded corners",
            "mascot_concept": "A friendly robot character with blue accents",
            "font_recommendation": "Inter for body, Poppins for headers"
        }, indent=2)
    
    def _generate_mock_mascot_prompt(self) -> str:
        """Generate mock mascot generation prompt."""
        return """A friendly robot mascot character, 3D rendered style, 
        blue and teal color scheme, standing pose, white background, 
        Pixar-style animation, cute and approachable, high quality render"""
    
    def _generate_mock_avatar_prompt(self) -> str:
        """Generate mock avatar generation prompt."""
        return """Professional avatar portrait, friendly robot character, 
        blue color accents, clean background, corporate headshot style, 
        high quality, 3D rendered"""
    
    def _generate_mock_pose_prompt(self) -> str:
        """Generate mock pose generation prompt."""
        poses = [
            "waving hello", "thumbs up", "thinking pose", 
            "celebrating", "presenting", "running"
        ]
        pose = random.choice(poses)
        return f"Robot mascot character in {pose} pose, same style as reference, consistent character design"
    
    def _generate_mock_react_component(self) -> str:
        """Generate mock React component code."""
        return '''import React from 'react';

export const BrandMascot = ({ pose = 'default', size = 200 }) => {
  const poses = {
    default: '🤖',
    wave: '👋',
    thumbsup: '👍',
    thinking: '🤔',
    celebrate: '🎉'
  };
  
  return (
    <div style={{ 
      fontSize: size, 
      textAlign: 'center',
      animation: 'bounce 2s infinite'
    }}>
      {poses[pose] || poses.default}
    </div>
  );
};

export default BrandMascot;'''
    
    def _generate_mock_revision(self) -> str:
        """Generate mock revision response."""
        return json.dumps({
            "revised_prompt": "Updated mascot with brighter colors and more dynamic pose",
            "changes_made": ["Increased color saturation", "Added dynamic lighting", "Improved pose"],
            "seed": 43
        })
    
    def _generate_mock_brand_copy(self) -> str:
        """Generate mock brand copy."""
        return json.dumps({
            "tagline": "Innovate with Confidence",
            "mission_statement": "Empowering businesses through cutting-edge technology solutions.",
            "value_propositions": [
                "Reliable and scalable solutions",
                "Expert support team",
                "Future-proof technology"
            ],
            "social_media_templates": {
                "announcement": "🚀 Exciting news from {brand_name}! {message}",
                "feature_highlight": "✨ Discover how {feature} can transform your workflow"
            }
        })
    
    def _generate_generic_response(self, prompt: str) -> str:
        """Generate generic response for unknown prompts."""
        return f"Mock response for: {prompt[:50]}..."


# Singleton instance
mock_dashscope_client = MockDashScopeClient()
