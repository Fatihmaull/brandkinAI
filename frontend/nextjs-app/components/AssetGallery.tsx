'use client';

import { useState } from 'react';
import { Check, RefreshCw, ImageIcon, User, Move } from 'lucide-react';

interface Asset {
  asset_id: string;
  type: string;
  oss_url: string;
  transparent_url: string;
  is_selected: boolean;
  metadata?: {
    pose_name?: string;
  };
}

interface AssetGalleryProps {
  assets: Asset[];
  status?: string;
  onSelect: (assetId: string, type: string) => void;
  onRevise: (assetId: string, feedback: string, type: string) => void;
}

export default function AssetGallery({ assets, status, onSelect, onRevise }: AssetGalleryProps) {
  const [selectedAsset, setSelectedAsset] = useState<string | null>(null);
  const [revisionFeedback, setRevisionFeedback] = useState('');
  const [showRevisionModal, setShowRevisionModal] = useState(false);
  const [revisionAsset, setRevisionAsset] = useState<Asset | null>(null);

  const mascots = assets.filter(a => a.type === 'mascot');
  const avatars = assets.filter(a => a.type === 'avatar');
  const poses = assets.filter(a => a.type === 'pose');

  const handleSelect = (asset: Asset) => {
    setSelectedAsset(asset.asset_id);
    onSelect(asset.asset_id, asset.type);
  };

  const openRevision = (asset: Asset) => {
    setRevisionAsset(asset);
    setShowRevisionModal(true);
  };

  const submitRevision = () => {
    if (revisionAsset && revisionFeedback) {
      onRevise(revisionAsset.asset_id, revisionFeedback, revisionAsset.type);
      setShowRevisionModal(false);
      setRevisionFeedback('');
      setRevisionAsset(null);
    }
  };

  const renderAssetCard = (asset: Asset, showSelect: boolean = true) => (
    <div
      key={asset.asset_id}
      className={`relative studio-card overflow-hidden transition-all ${asset.is_selected ? 'ring-2 ring-blue-500' : ''
        } ${selectedAsset === asset.asset_id ? 'ring-2 ring-blue-400' : ''}`}
    >
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
      </div>

      {/* Actions */}
      <div className="p-3 flex gap-2 border-t border-[#3c3c43]">
        {showSelect && (
          <button
            onClick={() => handleSelect(asset)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${asset.is_selected
              ? 'bg-blue-500 text-white'
              : 'bg-[#1c1c1e] hover:bg-[#2c2c2e] text-gray-300'
              }`}
          >
            {asset.is_selected ? 'Selected' : 'Select'}
          </button>
        )}

        <button
          onClick={() => openRevision(asset)}
          className="p-2 bg-[#1c1c1e] hover:bg-[#2c2c2e] rounded-lg text-gray-400 hover:text-white transition-colors"
          title="Request Revision"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Pose Name */}
      {asset.metadata?.pose_name && (
        <div className="px-3 pb-3 text-xs text-gray-500">
          {asset.metadata.pose_name}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Mascots */}
      {mascots.length > 0 && (
        <div className="studio-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <ImageIcon className="w-4 h-4 text-blue-400" />
            </div>
            <h3 className="text-lg font-medium text-white">Mascot Options</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {mascots.map(asset => renderAssetCard(asset))}
          </div>
        </div>
      )}

      {/* Avatars */}
      {avatars.length > 0 && (
        <div className="studio-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <User className="w-4 h-4 text-purple-400" />
            </div>
            <h3 className="text-lg font-medium text-white">Avatar Options</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {avatars.map(asset => renderAssetCard(asset))}
          </div>
        </div>
      )}

      {/* Poses */}
      {(poses.length > 0 || status === 'awaiting_finalization') && (
        <div className="studio-card p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                <Move className="w-4 h-4 text-green-400" />
              </div>
              <h3 className="text-lg font-medium text-white">Pose Pack</h3>
            </div>

            {/* Generation Status Indicator */}
            {status === 'awaiting_finalization' && poses.length < 4 && (
              <div className="flex items-center gap-3 px-4 py-2 bg-[#0d0d0d] rounded-full border border-[#2c2c2e]">
                <div className="w-4 h-4 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
                <span className="text-sm text-gray-400">
                  <span className="text-white font-medium">{poses.length}</span> out of <span className="text-white font-medium">4</span> poses generated. Please wait...
                </span>
              </div>
            )}
            {status === 'awaiting_finalization' && poses.length >= 4 && (
              <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 rounded-full border border-green-500/30">
                <Check className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-400 font-medium">All 4 poses generated!</span>
              </div>
            )}
          </div>

          {poses.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {poses.map(asset => renderAssetCard(asset, false))}
            </div>
          ) : (
            <div className="py-12 flex flex-col items-center justify-center border border-dashed border-[#2c2c2e] rounded-xl bg-black/20">
              <div className="w-10 h-10 rounded-full border-4 border-[#2c2c2e] border-t-blue-500 animate-spin mb-4" />
              <p className="text-gray-400">Generating your brand's custom poses...</p>
            </div>
          )}
        </div>
      )}

      {/* Revision Modal */}
      {showRevisionModal && revisionAsset && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="studio-card p-6 max-w-lg w-full">
            <h3 className="text-lg font-medium text-white mb-4">Request Revision</h3>

            <div className="mb-4 p-4 bg-[#0d0d0d] rounded-lg">
              <img
                src={revisionAsset.transparent_url || revisionAsset.oss_url}
                alt="Current asset"
                className="w-32 h-32 object-contain mx-auto"
              />
            </div>

            <textarea
              value={revisionFeedback}
              onChange={(e) => setRevisionFeedback(e.target.value)}
              className="studio-input w-full h-32 mb-4"
              placeholder="Describe what you'd like to change..."
            />

            <div className="flex gap-3">
              <button
                onClick={() => setShowRevisionModal(false)}
                className="studio-btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                onClick={submitRevision}
                disabled={!revisionFeedback}
                className="studio-btn-primary flex-1 disabled:opacity-50"
              >
                Submit Revision
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
