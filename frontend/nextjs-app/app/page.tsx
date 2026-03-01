'use client';

import { useState, useEffect } from 'react';
import BrandDNAWizard from '@/components/BrandDNAWizard';
import StageTracker from '@/components/StageTracker';
import AssetGallery from '@/components/AssetGallery';
import CodePreview from '@/components/CodePreview';
import CharacterSelection from '@/components/CharacterSelection';
import { api } from '@/lib/api';

export default function Home() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState(0);
  const [projectStatus, setProjectStatus] = useState<string>('idle');
  const [assets, setAssets] = useState<any[]>([]);
  const [codeExports, setCodeExports] = useState<any[]>([]);
  const [brandKit, setBrandKit] = useState<any>(null);
  const [generatedAssets, setGeneratedAssets] = useState<{mascot?: any, avatar?: any} | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');

  const handleProjectCreated = (id: string) => {
    setProjectId(id);
    setCurrentStage(1);
    setProjectStatus('processing');
    
    // Start polling for status updates
    startStatusPolling(id);
  };

  const startStatusPolling = async (id: string) => {
    setIsLoading(true);
    setLoadingMessage('Initializing project...');
    
    const poll = async () => {
      const { data, error } = await api.getProject(id);
      
      if (error) {
        console.error('Failed to fetch project status:', error);
        setIsLoading(false);
        return;
      }
      
      if (data) {
        setCurrentStage(data.current_stage || 0);
        setProjectStatus(data.status);
        
        // Update loading message based on stage
        if (data.status === 'processing') {
          setLoadingMessage(`Processing Stage ${data.current_stage}: ${getStageName(data.current_stage)}...`);
        } else if (data.status === 'awaiting_selection') {
          setIsLoading(false);
          setLoadingMessage('');
        }
        
        // Handle generated assets from Stage 2
        if (data.current_stage === 2 && data.last_stage_result?.assets) {
          setGeneratedAssets(data.last_stage_result.assets);
        }
        
        // Fetch assets when available
        if (data.assets && data.assets.total > 0) {
          const { data: assetsData } = await api.getAssets(id);
          if (assetsData) {
            setAssets(assetsData.assets || []);
          }
        }
        
        // Fetch code exports when available
        if (data.code_exports > 0) {
          const { data: codeData } = await api.getCodeExports(id);
          if (codeData) {
            setCodeExports(codeData.code_exports || []);
          }
        }
        
        // Set brand kit when available
        if (data.brand_kit?.available) {
          setBrandKit(data.brand_kit);
        }
        
        // Continue polling if not completed or failed
        if (data.status !== 'completed' && data.status !== 'failed') {
          setTimeout(poll, 3000);
        } else {
          setIsLoading(false);
        }
      }
    };
    
    const getStageName = (stage: number): string => {
      const stages = ['Initialize', 'Brand DNA', 'Visual Gen', 'Selection', 'Pose Pack', 'Code Export', 'Revision', 'Assembly'];
      return stages[stage] || 'Processing';
    };
    
    poll();
  };

  const handleCharacterSelect = async (assetId: string, type: string) => {
    if (!projectId) return;
    
    const { data, error } = await api.selectCharacter(projectId, assetId, type);
    
    if (error) {
      alert(`Failed to select character: ${error}`);
      return;
    }
    
    // Refresh assets
    const { data: assetsData } = await api.getAssets(projectId);
    if (assetsData) {
      setAssets(assetsData.assets || []);
    }
  };

  const handleRevision = async (assetId: string, feedback: string, type: string) => {
    if (!projectId) return;
    
    const { data, error } = await api.requestRevision(projectId, assetId, feedback, type);
    
    if (error) {
      alert(`Failed to request revision: ${error}`);
      return;
    }
    
    // Refresh assets after revision
    setTimeout(async () => {
      const { data: assetsData } = await api.getAssets(projectId);
      if (assetsData) {
        setAssets(assetsData.assets || []);
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
    
    if (data?.brand_kit) {
      setBrandKit(data.brand_kit);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold gradient-text mb-4">
            BrandKin AI
          </h1>
          <p className="text-xl text-gray-300">
            AI-Powered Brand Identity Creation
          </p>
        </header>

        {/* Stage Tracker */}
        {projectId && (
          <StageTracker 
            currentStage={currentStage} 
            status={projectStatus}
          />
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-white mb-4"></div>
            <p className="text-xl text-gray-300">{loadingMessage}</p>
            <p className="text-sm text-gray-500 mt-2">This may take a few moments...</p>
          </div>
        )}

        {/* Main Content */}
        <div className="mt-8">
          {!projectId ? (
            <BrandDNAWizard onProjectCreated={handleProjectCreated} />
          ) : (
            <div className="space-y-8">
              {/* Character Selection - Stage 2 */}
              {currentStage === 2 && generatedAssets?.mascot && generatedAssets?.avatar && (
                <CharacterSelection
                  mascot={generatedAssets.mascot}
                  avatar={generatedAssets.avatar}
                  onSelect={(assetId) => handleCharacterSelect(assetId, 'mascot')}
                  onRegenerate={() => window.location.reload()}
                />
              )}

              {/* Asset Gallery */}
              {assets.length > 0 && (
                <AssetGallery
                  assets={assets}
                  onSelect={handleCharacterSelect}
                  onRevise={handleRevision}
                />
              )}

              {/* Code Preview */}
              {codeExports.length > 0 && (
                <CodePreview exports={codeExports} />
              )}

              {/* Finalize Button */}
              {currentStage >= 5 && !brandKit && (
                <div className="text-center">
                  <button
                    onClick={handleFinalize}
                    className="px-8 py-4 bg-gradient-to-r from-brand-500 to-alchemy-accent text-white font-bold rounded-lg hover:opacity-90 transition-opacity"
                  >
                    Finalize Brand Kit
                  </button>
                </div>
              )}

              {/* Brand Kit Download */}
              {brandKit && (
                <div className="glass rounded-xl p-8 text-center">
                  <h2 className="text-2xl font-bold mb-4">Your Brand Kit is Ready!</h2>
                  <a
                    href={brandKit.download_url}
                    download
                    className="inline-block px-8 py-4 bg-green-600 text-white font-bold rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Download Brand Kit (.zip)
                  </a>
                  <p className="mt-4 text-sm text-gray-400">
                    Link expires: {new Date(brandKit.expires_at).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
