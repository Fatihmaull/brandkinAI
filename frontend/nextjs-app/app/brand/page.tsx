'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Building2, Target, Palette, MessageSquare, ArrowLeft, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

function LoadingState() {
  return (
    <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  );
}

interface BrandDNA {
  brand_name?: string;
  name?: string;
  brand_personality: string[];
  target_audience: {
    demographics: string;
    psychographics: string;
  };
  visual_style: {
    art_direction: string;
    color_palette: {
      primary: string;
      secondary: string;
      accent: string;
    };
    mood_keywords: string[];
  };
  mascot_concept: {
    character_type: string;
    personality_traits: string[];
    visual_description: string;
  };
  avatar_concept: {
    style: string;
    visual_description: string;
  };
}

interface Project {
  project_id: string;
  brand_brief: BrandDNA;
  brand_dna?: BrandDNA;
  status: string;
  current_stage: number;
  created_at: string;
}

function BrandContent() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get('id');

  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      loadProject(projectId);
    } else {
      setIsLoading(false);
    }
  }, [projectId]);

  const loadProject = async (id: string) => {
    const { data, error } = await api.getProject(id);
    if (error) {
      console.error('Failed to load project:', error);
    } else {
      setProject(data as Project);
    }
    setIsLoading(false);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-4">No project selected</p>
          <Link href="/" className="studio-btn inline-block">
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  // Use brand_dna (AI-generated from Stage 1) as primary, brand_brief (user form) as fallback
  const dna = project.brand_dna || project.brand_brief || {};

  if (!dna || (!dna.brand_name && !dna.name)) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-4">Brand data not yet available. The AI is still processing.</p>
          <Link href="/" className="studio-btn inline-block">
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d0d0d]">
      {/* Header */}
      <header className="border-b border-[#3c3c43]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-gray-400 hover:text-white transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <h1 className="text-xl font-semibold">Brand Details</h1>
            </div>
            <div className="flex gap-3">
              <Link
                href={`/assets?id=${projectId}`}
                className="studio-btn-secondary text-sm"
              >
                View Assets
              </Link>
              <Link
                href={`/components-page?id=${projectId}`}
                className="studio-btn-secondary text-sm"
              >
                View Components
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Brand Header */}
        <div className="studio-card p-8 mb-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-3xl font-bold gradient-text mb-2">{dna.brand_name || dna.name}</h2>
              <p className="text-gray-400">Project ID: {project.project_id}</p>
              <div className="flex gap-2 mt-3">
                {dna.brand_personality?.map((trait, idx) => (
                  <span key={idx} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                    {trait}
                  </span>
                ))}
              </div>
            </div>
            <div className="text-right">
              <span className={`px-3 py-1 rounded-full text-sm ${project.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                project.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-blue-500/20 text-blue-400'
                }`}>
                {project.status}
              </span>
              <p className="text-sm text-gray-500 mt-2">
                Stage {project.current_stage} of 7
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Target Audience */}
          <div className="studio-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <Target className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-lg font-medium">Target Audience</h3>
            </div>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Demographics</h4>
                <p className="text-white">{dna.target_audience?.demographics || 'Not specified'}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Psychographics</h4>
                <p className="text-white">{dna.target_audience?.psychographics || 'Not specified'}</p>
              </div>
            </div>
          </div>

          {/* Visual Style */}
          <div className="studio-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Palette className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-lg font-medium">Visual Style</h3>
            </div>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Art Direction</h4>
                <p className="text-white">{dna.visual_style?.art_direction || 'Not specified'}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Color Palette</h4>
                <div className="flex gap-3">
                  {dna.visual_style?.color_palette?.primary && (
                    <div className="text-center">
                      <div
                        className="w-12 h-12 rounded-lg border border-[#3c3c43]"
                        style={{ backgroundColor: dna.visual_style.color_palette.primary }}
                      />
                      <span className="text-xs text-gray-500 mt-1">Primary</span>
                    </div>
                  )}
                  {dna.visual_style?.color_palette?.secondary && (
                    <div className="text-center">
                      <div
                        className="w-12 h-12 rounded-lg border border-[#3c3c43]"
                        style={{ backgroundColor: dna.visual_style.color_palette.secondary }}
                      />
                      <span className="text-xs text-gray-500 mt-1">Secondary</span>
                    </div>
                  )}
                  {dna.visual_style?.color_palette?.accent && (
                    <div className="text-center">
                      <div
                        className="w-12 h-12 rounded-lg border border-[#3c3c43]"
                        style={{ backgroundColor: dna.visual_style.color_palette.accent }}
                      />
                      <span className="text-xs text-gray-500 mt-1">Accent</span>
                    </div>
                  )}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Mood Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {dna.visual_style?.mood_keywords?.map((keyword, idx) => (
                    <span key={idx} className="px-2 py-1 bg-[#1c1c1e] rounded text-sm text-gray-300">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Mascot Concept */}
          <div className="studio-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <Building2 className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="text-lg font-medium">Mascot Concept</h3>
            </div>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Character Type</h4>
                <p className="text-white">{dna.mascot_concept?.character_type || 'Not specified'}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2">Personality Traits</h4>
                <div className="flex flex-wrap gap-2">
                  {dna.mascot_concept?.personality_traits?.map((trait, idx) => (
                    <span key={idx} className="px-2 py-1 bg-green-500/20 text-green-400 rounded text-sm">
                      {trait}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Visual Description</h4>
                <p className="text-white text-sm">{dna.mascot_concept?.visual_description || 'Not specified'}</p>
              </div>
            </div>
          </div>

          {/* Avatar Concept */}
          <div className="studio-card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-orange-400" />
              </div>
              <h3 className="text-lg font-medium">Avatar Concept</h3>
            </div>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Style</h4>
                <p className="text-white">{dna.avatar_concept?.style || 'Not specified'}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-1">Visual Description</h4>
                <p className="text-white text-sm">{dna.avatar_concept?.visual_description || 'Not specified'}</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function BrandPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <BrandContent />
    </Suspense>
  );
}
