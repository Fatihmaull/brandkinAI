'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { ImageIcon, User, Move, ArrowLeft, Download, Check } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

interface Asset {
  asset_id: string;
  type: string;
  oss_url: string;
  transparent_url: string;
  is_selected: boolean;
  metadata?: {
    pose_name?: string;
    prompt?: string;
  };
}

interface Project {
  project_id: string;
  brand_brief: {
    brand_name: string;
  };
  status: string;
}

function LoadingState() {
  return (
    <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-400 text-sm">Loading assets...</p>
      </div>
    </div>
  );
}

function AssetsContent() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get('id');

  const [project, setProject] = useState<Project | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (projectId) {
      loadData(projectId);
    } else {
      setIsLoading(false);
    }
  }, [projectId]);

  const loadData = async (id: string) => {
    try {
      const [projectRes, assetsRes] = await Promise.all([
        api.getProject(id),
        api.getAssets(id)
      ]);

      if (projectRes.data) {
        setProject(projectRes.data as Project);
      }
      if (assetsRes.data) {
        const assetsData = (assetsRes.data as any).assets;
        setAssets(Array.isArray(assetsData) ? assetsData : []);
      } else {
        setAssets([]);
      }
    } catch (error) {
      console.error('Error loading assets:', error);
      setAssets([]);
    } finally {
      setIsLoading(false);
    }
  };

  const mascots = assets.filter(a => a.type === 'mascot');
  const avatars = assets.filter(a => a.type === 'avatar');
  const poses = assets.filter(a => a.type === 'pose');

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-4">No project selected</p>
          <Link href="/demo" className="studio-btn inline-block">
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  const renderAssetCard = (asset: Asset, showSelect: boolean = true) => (
    <div key={asset.asset_id} className="studio-card overflow-hidden group">
      {/* Image */}
      <div className="aspect-square relative bg-[#0d0d0d]">
        <img
          src={asset.transparent_url || asset.oss_url}
          alt={asset.metadata?.pose_name || asset.type}
          className="w-full h-full object-contain p-4"
        />

        {/* Selected Badge */}
        {asset.is_selected && (
          <div className="absolute top-2 right-2 w-7 h-7 bg-blue-500 rounded-full flex items-center justify-center">
            <Check className="w-4 h-4 text-white" />
          </div>
        )}

        {/* Hover Overlay */}
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            onClick={() => handleDownload(asset.oss_url, `${asset.type}_${asset.asset_id}.png`)}
            className="p-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
            title="Download"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="p-3 border-t border-[#3c3c43]">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400 capitalize">{asset.type}</span>
          {asset.is_selected && (
            <span className="text-xs text-blue-400">Selected</span>
          )}
        </div>
        {asset.metadata?.pose_name && (
          <p className="text-xs text-gray-500 mt-1">{asset.metadata.pose_name}</p>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0d0d0d]">
      {/* Header */}
      <header className="border-b border-[#3c3c43]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/demo" className="text-gray-400 hover:text-white transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div>
                <h1 className="text-xl font-semibold">Brand Assets</h1>
                <p className="text-sm text-gray-400">{project.brand_brief?.brand_name}</p>
              </div>
            </div>
            <div className="flex gap-3">
              <Link
                href={`/brand?id=${projectId}`}
                className="studio-btn-secondary text-sm"
              >
                View Brand
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
        {assets.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 px-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mb-6">
              <ImageIcon className="w-8 h-8 text-gray-500" />
            </div>
            <h3 className="text-xl font-medium text-white mb-2">No assets yet</h3>
            <p className="text-gray-400 text-center max-w-md mb-6">
              Your generated assets will appear here. Continue with your project to create mascots, avatars, and poses.
            </p>
            <Link href={`/demo?id=${projectId}`} className="studio-btn">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Continue Project
            </Link>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Mascots */}
            {mascots.length > 0 && (
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                    <ImageIcon className="w-4 h-4 text-blue-400" />
                  </div>
                  <h2 className="text-lg font-medium">Mascots</h2>
                  <span className="text-sm text-gray-500">({mascots.length})</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                  {mascots.map(asset => renderAssetCard(asset))}
                </div>
              </section>
            )}

            {/* Avatars */}
            {avatars.length > 0 && (
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <User className="w-4 h-4 text-purple-400" />
                  </div>
                  <h2 className="text-lg font-medium">Avatars</h2>
                  <span className="text-sm text-gray-500">({avatars.length})</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                  {avatars.map(asset => renderAssetCard(asset))}
                </div>
              </section>
            )}

            {/* Poses */}
            {poses.length > 0 && (
              <section>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <Move className="w-4 h-4 text-green-400" />
                  </div>
                  <h2 className="text-lg font-medium">Pose Pack</h2>
                  <span className="text-sm text-gray-500">({poses.length})</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                  {poses.map(asset => renderAssetCard(asset, false))}
                </div>
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default function AssetsPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <AssetsContent />
    </Suspense>
  );
}
