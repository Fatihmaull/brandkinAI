'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { Sparkles, Building2, Target, Palette, MessageSquare } from 'lucide-react';

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

    if (error) {
      alert(`Failed to create project: ${error}`);
    } else if (data?.project_id) {
      onProjectCreated(data.project_id);
    }

    setIsSubmitting(false);
  };

  return (
    <div className="glass rounded-2xl p-8 max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <Sparkles className="w-8 h-8 text-brand-500" />
        <h2 className="text-2xl font-bold">Brand DNA Wizard</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Brand Name */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2">
            <Building2 className="w-4 h-4" />
            Brand Name
          </label>
          <input
            type="text"
            value={formData.brand_name}
            onChange={(e) => setFormData({ ...formData, brand_name: e.target.value })}
            className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-brand-500 focus:outline-none"
            placeholder="Enter your brand name"
            required
          />
        </div>

        {/* Industry */}
        <div>
          <label className="text-sm font-medium mb-2 block">Industry</label>
          <input
            type="text"
            value={formData.industry}
            onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
            className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-brand-500 focus:outline-none"
            placeholder="e.g., Technology, Fashion, Food & Beverage"
            required
          />
        </div>

        {/* Target Audience */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2">
            <Target className="w-4 h-4" />
            Target Audience
          </label>
          <textarea
            value={formData.target_audience}
            onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
            className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-brand-500 focus:outline-none h-20"
            placeholder="Describe your ideal customers..."
            required
          />
        </div>

        {/* Brand Personality */}
        <div>
          <label className="text-sm font-medium mb-3 block">Brand Personality (Select up to 4)</label>
          <div className="flex flex-wrap gap-2">
            {PERSONALITY_OPTIONS.map((personality) => (
              <button
                key={personality}
                type="button"
                onClick={() => handlePersonalityToggle(personality)}
                className={`px-4 py-2 rounded-full text-sm transition-all ${
                  formData.brand_personality.includes(personality)
                    ? 'bg-brand-500 text-white'
                    : 'bg-white/5 hover:bg-white/10 border border-white/10'
                }`}
              >
                {personality}
              </button>
            ))}
          </div>
        </div>

        {/* Visual Style */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2">
            <Palette className="w-4 h-4" />
            Visual Style Preference
          </label>
          <select
            value={formData.visual_style}
            onChange={(e) => setFormData({ ...formData, visual_style: e.target.value })}
            className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-brand-500 focus:outline-none"
            required
          >
            <option value="">Select a style...</option>
            {VISUAL_STYLES.map((style) => (
              <option key={style} value={style}>{style}</option>
            ))}
          </select>
        </div>

        {/* Color Preferences */}
        <div>
          <label className="text-sm font-medium mb-2 block">Color Preferences (Optional)</label>
          <input
            type="text"
            value={formData.color_preferences}
            onChange={(e) => setFormData({ ...formData, color_preferences: e.target.value })}
            className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-brand-500 focus:outline-none"
            placeholder="e.g., Blue and orange, Earth tones, Bright and vibrant"
          />
        </div>

        {/* Brand Story */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium mb-2">
            <MessageSquare className="w-4 h-4" />
            Brand Story / Description
          </label>
          <textarea
            value={formData.brand_story}
            onChange={(e) => setFormData({ ...formData, brand_story: e.target.value })}
            className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-brand-500 focus:outline-none h-32"
            placeholder="Tell us about your brand's mission, values, and what makes it unique..."
            required
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-4 bg-gradient-to-r from-brand-500 to-alchemy-accent text-white font-bold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Creating Your Brand...
            </span>
          ) : (
            'Start Brand Alchemy'
          )}
        </button>
      </form>
    </div>
  );
}
