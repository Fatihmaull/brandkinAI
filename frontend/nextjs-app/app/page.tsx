'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Sparkles, Wand2, Image, Code, Download, ChevronRight, Loader2 } from 'lucide-react';
import BrandDNAWizard from '@/components/BrandDNAWizard';
import StageTracker from '@/components/StageTracker';
import AssetGallery from '@/components/AssetGallery';
import CodePreview from '@/components/CodePreview';
import CharacterSelection from '@/components/CharacterSelection';
import GenerationProgress from '@/components/GenerationProgress';
import { api } from '@/lib/api';

export default function Home() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState(0);
  const [projectStatus, setProjectStatus] = useState<string>('idle');
  const [assets, setAssets] = useState<any[]>([]);
  const [codeExports, setCodeExports] = useState<any[]>([]);
  const [brandKit, setBrandKit] = useState<any>(null);
  const [generatedAssets, setGeneratedAssets] = useState<{ mascot?: any, avatar?: any } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');

  const handleProjectCreated = (id: string) => {
    setProjectId(id);
    setCurrentStage(1);
    setProjectStatus('processing');
    startStatusPolling(id);
  };

  const startStatusPolling = async (id: string) => {
    setIsLoading(true);
    setLoadingMessage('Initializing your brand...');

    const poll = async () => {
      const { data, error } = await api.getProject(id);

      if (error) {
        console.error('Failed to fetch project status:', error);
        setIsLoading(false);
        return;
      }

      if (data) {
        const projectData = data as any;
        setCurrentStage(projectData.current_stage || 0);
        setProjectStatus(projectData.status);

        if (projectData.status === 'processing') {
          setLoadingMessage(`Creating ${getStageName(projectData.current_stage)}...`);
        } else if (projectData.status === 'awaiting_selection' || projectData.status === 'awaiting_finalization') {
          setIsLoading(false);
          setLoadingMessage('');
        }

        if (projectData.current_stage === 2 && projectData.last_stage_result?.assets) {
          setGeneratedAssets(projectData.last_stage_result.assets);
        }

        if (projectData.assets && projectData.assets.total > 0) {
          const { data: assetsData } = await api.getAssets(id);
          if (assetsData) {
            setAssets((assetsData as any).assets || []);
          }
        }

        if (projectData.code_exports > 0) {
          const { data: codeData } = await api.getCodeExports(id);
          if (codeData) {
            setCodeExports((codeData as any).code_exports || []);
          }
        }

        if (projectData.brand_kit?.available) {
          setBrandKit(projectData.brand_kit);
        }

        if (projectData.status !== 'completed' && projectData.status !== 'failed') {
          setTimeout(poll, 3000);
        } else {
          setIsLoading(false);
        }
      }
    };

    const getStageName = (stage: number): string => {
      const stages = ['', 'Brand DNA', 'Visual Identity', 'Character Selection', 'Pose Collection', 'Code Components', 'Refinements', 'Brand Kit'];
      return stages[stage] || 'Processing';
    };

    poll();
  };

  const handleCharacterSelect = async (assetId: string, type: string) => {
    if (!projectId) return;

    // Optimistically show processing state
    setProjectStatus('processing');

    const { data, error } = await api.selectCharacter(projectId, assetId, type);

    if (error) {
      alert(`Failed to select character: ${error}`);
      setProjectStatus('awaiting_selection'); // Revert on error
      return;
    }

    const { data: assetsData } = await api.getAssets(projectId);
    if (assetsData) {
      setAssets((assetsData as any).assets || []);
    }

    // Fetch code exports too since Stage 5 generates them synchronously
    const { data: codeData } = await api.getCodeExports(projectId);
    if (codeData) {
      setCodeExports((codeData as any).code_exports || []);
    }

    // Explicitly update status to turn off progress bar
    setProjectStatus('awaiting_finalization');
  };

  const handleRevision = async (assetId: string, feedback: string, type: string) => {
    if (!projectId) return;

    const { data, error } = await api.requestRevision(projectId, assetId, feedback, type);

    if (error) {
      alert(`Failed to request revision: ${error}`);
      return;
    }

    setTimeout(async () => {
      const { data: assetsData } = await api.getAssets(projectId);
      if (assetsData) {
        setAssets((assetsData as any).assets || []);
      }
    }, 5000);
  };

  const handleFinalize = async () => {
    if (!projectId) return;

    const { data, error } = await api.finalizeProject(projectId);

    if (error) {
      alert(`Failed to finalize: ${error}`);
      return;
    }

    if (data && (data as any).brand_kit) {
      setBrandKit((data as any).brand_kit);
    }
  };

  // Feature cards for the landing page
  const features = [
    {
      icon: <Wand2 className="w-5 h-5 text-blue-400" />,
      title: "AI Brand DNA",
      description: "Describe your brand and let AI create your unique identity"
    },
    {
      icon: <Image className="w-5 h-5 text-purple-400" />,
      title: "Visual Identity",
      description: "Generate mascots, avatars, and brand assets automatically"
    },
    {
      icon: <Code className="w-5 h-5 text-green-400" />,
      title: "Code Export",
      description: "Get React components and CSS ready for your website"
    }
  ];

  return (
    <div className="min-h-screen bg-studio">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 border-r border-studio bg-studio hidden lg:block">
        <div className="p-4">
          <div className="flex items-center gap-3 px-2 py-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg">BrandKin AI</span>
          </div>

          <nav className="mt-8 space-y-1">
            <Link href="/" className="sidebar-item active">
              <Wand2 className="w-4 h-4" />
              <span>Create Brand</span>
            </Link>
            <Link href={projectId ? `/assets?id=${projectId}` : '/assets'} className="sidebar-item">
              <Image className="w-4 h-4" />
              <span>My Assets</span>
            </Link>
            <Link href={projectId ? `/components-page?id=${projectId}` : '/components-page'} className="sidebar-item">
              <Code className="w-4 h-4" />
              <span>Components</span>
            </Link>
          </nav>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-studio">
          <div className="text-xs text-gray-500">
            Powered by Alibaba Cloud Model Studio
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="lg:ml-64 min-h-screen">
        {/* Mobile Header */}
        <div className="lg:hidden flex items-center gap-3 p-4 border-b border-studio">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-lg">BrandKin AI</span>
        </div>

        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {!projectId ? (
            /* Landing Page */
            <div className="space-y-12">
              {/* Hero */}
              <div className="text-center pt-8 pb-12">
                <h1 className="text-4xl sm:text-5xl font-semibold mb-4">
                  <span className="gradient-text">Build your brand with AI</span>
                </h1>
                <p className="text-lg text-gray-400 max-w-2xl mx-auto">
                  Describe your vision and let AI create your complete brand identity —
                  from mascots to code components.
                </p>
              </div>

              {/* Feature Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {features.map((feature, idx) => (
                  <div key={idx} className="studio-card p-5">
                    <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center mb-4">
                      {feature.icon}
                    </div>
                    <h3 className="font-medium text-white mb-2">{feature.title}</h3>
                    <p className="text-sm text-gray-400">{feature.description}</p>
                  </div>
                ))}
              </div>

              {/* Create Brand Form */}
              <div className="studio-card p-6 sm:p-8">
                <BrandDNAWizard onProjectCreated={handleProjectCreated} />
              </div>
            </div>
          ) : (
            /* Project Workspace */
            <div className="space-y-6">
              {/* Header with Stage */}
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-2xl font-semibold">Brand Creation</h1>
                  <p className="text-sm text-gray-400 mt-1">
                    Project ID: {projectId.slice(0, 8)}...
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex gap-2">
                    <Link
                      href={`/brand?id=${projectId}`}
                      className="studio-btn-secondary text-sm"
                    >
                      Brand
                    </Link>
                    <Link
                      href={`/assets?id=${projectId}`}
                      className="studio-btn-secondary text-sm"
                    >
                      Assets
                    </Link>
                    <Link
                      href={`/components-page?id=${projectId}`}
                      className="studio-btn-secondary text-sm"
                    >
                      Components
                    </Link>
                  </div>
                  <StageTracker currentStage={currentStage} status={projectStatus} />
                </div>
              </div>

              {/* Loading State & Progress (shown above contents) */}
              {(isLoading || projectStatus === 'processing') && (
                <GenerationProgress currentStage={currentStage} status={projectStatus} />
              )}

              {/* Character Selection - Stage 2 */}
              {currentStage === 2 && generatedAssets?.mascot && generatedAssets?.avatar && !isLoading && (
                <CharacterSelection
                  mascot={generatedAssets.mascot}
                  avatar={generatedAssets.avatar}
                  onSelect={(assetId: string, type: string) => { handleCharacterSelect(assetId, type); }}
                  onRegenerate={() => window.location.reload()}
                />
              )}

              {/* Assets Gallery */}
              {assets.length > 0 && (
                <div className="studio-card p-6">
                  <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
                    <Image className="w-5 h-5 text-gray-400" />
                    Brand Assets
                  </h2>
                  <AssetGallery
                    assets={assets}
                    onSelect={handleCharacterSelect}
                    onRevise={handleRevision}
                  />
                </div>
              )}

              {/* Code Exports */}
              {codeExports.length > 0 && (
                <div className="studio-card p-6">
                  <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
                    <Code className="w-5 h-5 text-gray-400" />
                    Code Components
                  </h2>
                  <CodePreview exports={codeExports} />
                </div>
              )}

              {/* Finalize Button */}
              {currentStage >= 5 && !brandKit && !isLoading && (
                <div className="studio-card p-6 text-center">
                  <h3 className="text-lg font-medium mb-2">Ready to finalize?</h3>
                  <p className="text-sm text-gray-400 mb-4">
                    Generate your complete brand kit with all assets and code
                  </p>
                  <button
                    onClick={handleFinalize}
                    className="studio-btn px-6 py-3 inline-flex items-center gap-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    Generate Brand Kit
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* Brand Kit Download */}
              {brandKit && (
                <div className="studio-card p-8 text-center">
                  <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                    <Download className="w-8 h-8 text-green-500" />
                  </div>
                  <h2 className="text-xl font-semibold mb-2">Your Brand Kit is Ready!</h2>
                  <p className="text-sm text-gray-400 mb-6">
                    Download all your brand assets, code components, and guidelines
                  </p>
                  <a
                    href={brandKit.download_url}
                    download
                    className="studio-btn px-8 py-3 inline-flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download (.zip)
                  </a>
                  <p className="mt-4 text-xs text-gray-500">
                    Link expires: {new Date(brandKit.expires_at).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
