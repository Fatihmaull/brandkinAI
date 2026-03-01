"""
BrandKin AI - Prompt Engineering Library
Stages 1-7: Reusable prompt templates with strict JSON output requirements
"""

from typing import Dict, Any


class StagePrompts:
    """Centralized prompt templates for all pipeline stages."""
    
    # ==================== STAGE 1: Brand DNA Analysis ====================
    
    @staticmethod
    def stage1_brand_dna_analysis() -> Dict[str, str]:
        """
        Stage 1: Analyze brand brief and extract structured DNA.
        
        Returns:
            Dict with system_prompt and output_schema
        """
        system_prompt = """You are a Brand Strategist AI with expertise in brand identity analysis.
Your task is to analyze a brand brief and extract structured brand DNA elements.

Output MUST be valid JSON only, no markdown, no explanations.

Required output format:
{
    "brand_name": "string",
    "brand_personality": ["trait1", "trait2", "trait3"],
    "target_audience": {
        "demographics": "string",
        "psychographics": "string"
    },
    "visual_style": {
        "art_direction": "string (e.g., 'modern minimalist', 'playful 3D', 'corporate professional')",
        "color_palette": {
            "primary": "hex color",
            "secondary": "hex color",
            "accent": "hex color"
        },
        "mood_keywords": ["keyword1", "keyword2", "keyword3"]
    },
    "mascot_concept": {
        "character_type": "string (animal, abstract, humanoid, robot, etc.)",
        "personality_traits": ["trait1", "trait2"],
        "visual_description": "detailed visual description for image generation"
    },
    "avatar_concept": {
        "style": "string (professional, casual, artistic, etc.)",
        "visual_description": "detailed visual description for image generation"
    }
}"""
        
        output_schema = {
            "type": "object",
            "required": ["brand_name", "brand_personality", "visual_style", "mascot_concept", "avatar_concept"],
            "properties": {
                "brand_name": {"type": "string"},
                "brand_personality": {"type": "array", "items": {"type": "string"}},
                "target_audience": {
                    "type": "object",
                    "properties": {
                        "demographics": {"type": "string"},
                        "psychographics": {"type": "string"}
                    }
                },
                "visual_style": {
                    "type": "object",
                    "required": ["art_direction", "color_palette", "mood_keywords"],
                    "properties": {
                        "art_direction": {"type": "string"},
                        "color_palette": {
                            "type": "object",
                            "properties": {
                                "primary": {"type": "string"},
                                "secondary": {"type": "string"},
                                "accent": {"type": "string"}
                            }
                        },
                        "mood_keywords": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "mascot_concept": {
                    "type": "object",
                    "required": ["character_type", "visual_description"],
                    "properties": {
                        "character_type": {"type": "string"},
                        "personality_traits": {"type": "array", "items": {"type": "string"}},
                        "visual_description": {"type": "string"}
                    }
                },
                "avatar_concept": {
                    "type": "object",
                    "required": ["style", "visual_description"],
                    "properties": {
                        "style": {"type": "string"},
                        "visual_description": {"type": "string"}
                    }
                }
            }
        }
        
        return {
            "system_prompt": system_prompt,
            "output_schema": output_schema
        }
    
    # ==================== STAGE 2: Image Prompt Generation ====================
    
    @staticmethod
    def stage2_mascot_prompt_generation() -> Dict[str, str]:
        """Stage 2: Generate optimized image prompt for mascot."""
        
        system_prompt = """You are an expert Prompt Engineer specializing in AI image generation for Wanx-v1.
Convert brand DNA into optimized image generation prompts.

CRITICAL RULES:
1. Output ONLY valid JSON, no markdown
2. Prompts must be detailed, descriptive, and Wanx-v1 optimized
3. Include art style, lighting, composition, and mood
4. Use English for image prompts (Wanx-v1 performs best with English)

Output format:
{
    "mascot_prompt": "detailed English prompt for mascot generation",
    "mascot_negative_prompt": "things to avoid",
    "avatar_prompt": "detailed English prompt for avatar generation", 
    "avatar_negative_prompt": "things to avoid",
    "style_consistency_notes": "notes for maintaining visual consistency"
}"""
        
        return {"system_prompt": system_prompt}
    
    # ==================== STAGE 4: Pose Pack Generation ====================
    
    @staticmethod
    def stage4_pose_generation() -> Dict[str, str]:
        """Stage 4: Generate pose variations for selected character."""
        
        system_prompt = """You are a Character Designer AI. Generate 5 pose variations for a brand mascot.

Given:
- Character description
- Selected mascot image reference
- Brand personality

Generate 5 distinct poses that maintain character consistency:
1. Hero/Confident pose
2. Friendly/Welcoming pose  
3. Working/Action pose
4. Celebratory/Joyful pose
5. Thoughtful/Professional pose

Output MUST be valid JSON:
{
    "poses": [
        {
            "pose_name": "string",
            "pose_description": "detailed description for image generation",
            "expression": "facial expression description",
            "body_language": "body posture description"
        }
    ],
    "consistency_prompt_addition": "additional prompt text to maintain character consistency across all poses"
}"""
        
        return {"system_prompt": system_prompt}
    
    # ==================== STAGE 5: Code Export ====================
    
    @staticmethod
    def stage5_react_component_generation() -> Dict[str, str]:
        """Stage 5: Generate React component using qwen-coder-plus."""
        
        system_prompt = """You are a Senior React Developer specializing in animated UI components.
Generate production-ready React components for brand mascots.

REQUIREMENTS:
- React 18+ functional components with hooks
- TypeScript preferred but JavaScript acceptable
- CSS-in-JS or CSS modules (no external CSS files)
- Animations using CSS keyframes or Framer Motion (if imported)
- Responsive design
- No external image dependencies (use provided URL)
- Accessible (ARIA labels where appropriate)

Output MUST be valid JSON only, no markdown backticks:
{
    "component_name": "PascalCase component name",
    "react_code": "complete component code as string",
    "css_keyframes": "CSS @keyframes definitions if needed",
    "usage_snippet": "example usage code",
    "props_interface": "TypeScript interface or JSDoc for props",
    "dependencies": ["list", "of", "npm", "packages", "if", "any"]
}"""
        
        return {"system_prompt": system_prompt}
    
    @staticmethod
    def stage5_component_user_prompt(
        mascot_name: str,
        image_url: str,
        primary_color: str,
        accent_color: str,
        brand_story: str
    ) -> str:
        """Generate user prompt for React component."""
        
        return f"""Generate a React mascot widget component with the following specifications:

Mascot Details:
- Name: {mascot_name}
- Image URL: {image_url}
- Primary Color: {primary_color}
- Accent Color: {accent_color}
- Brand Story: {brand_story}

Component Features Required:
1. Floating animation (gentle up/down movement)
2. Glow pulse effect on hover
3. Click to show brand story tooltip/modal
4. Responsive sizing
5. No external dependencies beyond React
6. Clean, modern design matching brand colors

The component should be self-contained and ready to drop into any React application."""
    
    # ==================== STAGE 6: Revision Handler ====================
    
    @staticmethod
    def stage6_revision_prompt() -> Dict[str, str]:
        """Stage 6: Handle user revision requests."""
        
        system_prompt = """You are a Revision Specialist AI. Modify image generation prompts based on user feedback.

Given:
- Original prompt
- User revision request
- Current generation results

Generate an improved prompt that addresses the user's feedback while maintaining brand consistency.

Output MUST be valid JSON:
{
    "revised_prompt": "new optimized prompt",
    "changes_made": ["list of specific changes"],
    "conservation_notes": "what was preserved from original"
}"""
        
        return {"system_prompt": system_prompt}
    
    # ==================== STAGE 7: Brand Kit Assembly ====================
    
    @staticmethod
    def stage7_brand_copy_generation() -> Dict[str, str]:
        """Stage 7: Generate brand copy and marketing text."""
        
        system_prompt = """You are a Brand Copywriter AI. Generate complete brand copy package.

Given brand DNA and visual assets, create:

Output MUST be valid JSON:
{
    "tagline": "memorable brand tagline (5-8 words)",
    "elevator_pitch": "one-sentence brand description",
    "brand_story": "2-3 paragraph brand narrative",
    "social_media": {
        "instagram_bio": "short bio",
        "linkedin_headline": "professional headline",
        "twitter_bio": "concise bio"
    },
    "messaging_guidelines": {
        "tone_of_voice": "description",
        "key_messages": ["message1", "message2", "message3"],
        "words_to_use": ["word1", "word2"],
        "words_to_avoid": ["word1", "word2"]
    }
}"""
        
        return {"system_prompt": system_prompt}
    
    @staticmethod
    def stage7_linkedin_banner_prompt(brand_dna: Dict) -> str:
        """Generate prompt for LinkedIn banner background."""
        
        colors = brand_dna.get('visual_style', {}).get('color_palette', {})
        mood = brand_dna.get('visual_style', {}).get('mood_keywords', [])
        
        return f"""Professional LinkedIn banner background, 1584x396 pixels,
abstract gradient design using colors {colors.get('primary', '#000000')} and {colors.get('secondary', '#FFFFFF')},
{mood[0] if mood else 'modern'} style, subtle geometric patterns,
corporate professional, clean composition, high resolution,
suitable for text overlay, minimalist elegant design"""


# Convenience instance
prompts = StagePrompts()
