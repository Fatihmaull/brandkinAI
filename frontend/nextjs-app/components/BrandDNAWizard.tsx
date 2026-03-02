'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Sparkles, Building2, Target, Palette, MessageSquare, Loader2 } from 'lucide-react';

interface BrandDNAWizardProps {
  onProjectCreated: (projectId: string) => void;
}

interface FormData {
  brand_name: string;
  industry: string;
  target_audience: string;
  brand_personality: string[];
  visual_style: string;
  color_preferences: string;
  brand_story: string;
}

const PERSONALITY_OPTIONS = [
  'Professional', 'Playful', 'Innovative', 'Trustworthy',
  'Friendly', 'Bold', 'Sophisticated', 'Approachable',
  'Energetic', 'Calm', 'Luxurious', 'Minimalist'
];

const VISUAL_STYLES = [
  'Modern Minimalist', 'Playful 3D', 'Corporate Professional',
  'Artistic/Hand-drawn', 'Tech/Futuristic', 'Organic/Natural',
  'Retro/Vintage', 'Luxury/Elegant'
];

export default function BrandDNAWizard({ onProjectCreated }: BrandDNAWizardProps) {
  const [formData, setFormData] = useState<FormData>({
    brand_name: '',
    industry: '',
    target_audience: '',
    brand_personality: [],
    visual_style: '',
    color_preferences: '',
    brand_story: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePersonalityToggle = (personality: string) => {
    setFormData(prev => ({
      ...prev,
      brand_personality: prev.brand_personality.includes(personality)
        ? prev.brand_personality.filter(p => p !== personality)
        : [...prev.brand_personality, personality]
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const brandBrief = {
      brand_name: formData.brand_name,
      industry: formData.industry,
      target_audience: formData.target_audience,
      brand_personality: formData.brand_personality,
      visual_preferences: {
        style: formData.visual_style,
        colors: formData.color_preferences
      },
      brand_story: formData.brand_story
    };

    const { data, error } = await api.createProject(brandBrief);
    const projectData = data as any;

    if (error) {
      alert(`Failed to create project: ${error}`);
    } else if (projectData?.project_id) {
      onProjectCreated(projectData.project_id);
    }

    setIsSubmitting(false);
  };

  return (
    <div>
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-xl font-medium text-gray-300 mb-2">Describe your brand and let AI do the rest</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Brand Name */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2 text-gray-300">
            <Building2 className="w-4 h-4 text-gray-400" />
            Brand Name
          </label>
          <input
            type="text"
            value={formData.brand_name}
            onChange={(e) => setFormData({ ...formData, brand_name: e.target.value })}
            className="w-full px-4 py-3 studio-input"
            placeholder="Enter your brand name"
            required
          />
        </div>

        {/* Industry */}
        <div>
          <label className="text-sm font-medium mb-2 block text-gray-300">Industry</label>
          <input
            type="text"
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            className="w-full px-4 py-3 studio-input"
            placeholder="e.g., Technology, Fashion, Food & Beverage"
            required
          />
        </div>

        {/* Target Audience */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2 text-gray-300">
            <Target className="w-4 h-4 text-gray-400" />
            Target Audience
          </label>
          <textarea
            value={formData.target_audience}
            onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
            className="w-full px-4 py-3 studio-input h-20 resize-none"
            placeholder="Describe your ideal customers..."
            required
          />
        </div>

        {/* Brand Personality */}
        <div>
          <label className="text-sm font-medium mb-3 block text-gray-300">Brand Personality (Select up to 4)</label>
          <div className="flex flex-wrap gap-2">
            {PERSONALITY_OPTIONS.map((personality) => (
              <button
                key={personality}
                type="button"
                onClick={() => handlePersonalityToggle(personality)}
                className={`px-4 py-2 rounded-lg text-sm transition-all ${
                  formData.brand_personality.includes(personality)
                    ? 'bg-blue-600 text-white'
                    : 'bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300'
                }`}
              >
                {personality}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Style */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2 text-gray-300">
            <Palette className="w-4 h-4 text-gray-400" />
            Visual Style Preference
          </label>
          <select
            value={formData.visual_style}
            onChange={(e) => setFormData({ ...formData, visual_style: e.target.value })}
            className="w-full px-4 py-3 studio-input"
            required
          >
            <option value="">Select a style...</option>
            {VISUAL_STYLES.map((style) => (
              <option key={style} value={style} className="bg-gray-800">{style}</option>
            ))}
          </select>
        </div>

        {/* Color Preferences */}
        <div>
          <label className="text-sm font-medium mb-2 block text-gray-300">Color Preferences (Optional)</label>
          <input
            type="text"
            value={formData.color_preferences}
            onChange={(e) => setFormData({ ...formData, color_preferences: e.target.value })}
            className="w-full px-4 py-3 studio-input"
            placeholder="e.g., Blue and orange, Earth tones, Bright and vibrant"
          />
        </div>

        {/* Brand Story */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2 text-gray-300">
            <MessageSquare className="w-4 h-4 text-gray-400" />
            Brand Story / Description
          </label>
          <textarea
            value={formData.brand_story}
            onChange={(e) => setFormData({ ...formData, brand_story: e.target.value })}
            className="w-full px-4 py-3 studio-input h-32 resize-none"
            placeholder="Tell us about your brand's mission, values, and what makes it unique..."
            required
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-3 studio-btn flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating Your Brand...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Create Brand
            </>
          )}
        </button>
      </form>
    </div>
  );
}
