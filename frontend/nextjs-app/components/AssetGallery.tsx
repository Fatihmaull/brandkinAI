'use client';

import { useState } from 'react';
import { Check, RefreshCw, ZoomIn } from 'lucide-react';

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
  onSelect: (assetId: string, type: string) => void;
  onRevise: (assetId: string, feedback: string, type: string) => void;
}

export default function AssetGallery({ assets, onSelect, onRevise }: AssetGalleryProps) {
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
      className={`relative glass rounded-xl overflow-hidden transition-all ${
        asset.is_selected ? 'ring-2 ring-brand-500' : ''
      } ${selectedAsset === asset.asset_id ? 'ring-2 ring-alchemy-accent' : ''}`}
    >
      {/* Image */}
      <div className="aspect-square relative bg-gray-900">
        <img
          src={asset.transparent_url || asset.oss_url}
          alt={asset.metadata?.pose_name || asset.type}
          className="w-full h-full object-contain p-4"
        />
        
        {/* Selected Badge */}
        {asset.is_selected && (
          <div className="absolute top-2 right-2 w-8 h-8 bg-brand-500 rounded-full flex items-center justify-center">
            <Check className="w-5 h-5 text-white" />
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 flex gap-2">
        {showSelect && (
          <button
            onClick={() => handleSelect(asset)}
            className={`flex-1 py-2 rounded-lg font-medium transition-colors ${
              asset.is_selected
                ? 'bg-brand-500 text-white'
                : 'bg-white/10 hover:bg-white/20'
            }`}
          >
            {asset.is_selected ? 'Selected' : 'Select'}
          </button>
        )}
        
        <button
          onClick={() => openRevision(asset)}
          className="p-2 bg-white/10 hover:bg-white/20 rounded-lg"
          title="Request Revision"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {/* Pose Name */}
      {asset.metadata?.pose_name && (
        <div className="px-4 pb-2 text-sm text-gray-400">
          {asset.metadata.pose_name}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Mascots */}
      {mascots.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-xl font-bold mb-4">Mascot Options</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {mascots.map(asset => renderAssetCard(asset))}
          </div>
        </div>
      )}

      {/* Avatars */}
      {avatars.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-xl font-bold mb-4">Avatar Options</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {avatars.map(asset => renderAssetCard(asset))}
          </div>
        </div>
      )}

      {/* Poses */}
      {poses.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h3 className="text-xl font-bold mb-4">Pose Pack</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {poses.map(asset => renderAssetCard(asset, false))}
          </div>
        </div>
      )}

      {/* Revision Modal */}
      {showRevisionModal && revisionAsset && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="glass rounded-xl p-6 max-w-lg w-full">
            <h3 className="text-xl font-bold mb-4">Request Revision</h3>
            
            <div className="mb-4">
              <img
                src={revisionAsset.transparent_url || revisionAsset.oss_url}
                alt="Current asset"
                className="w-32 h-32 object-contain mx-auto bg-gray-900 rounded-lg"
              />
            </div>

            <textarea
              value={revisionFeedback}
              onChange={(e) => setRevisionFeedback(e.target.value)}
              className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-brand-500 focus:outline-none h-32 mb-4"
              placeholder="Describe what you'd like to change..."
            />

            <div className="flex gap-3">
              <button
                onClick={() => setShowRevisionModal(false)}
                className="flex-1 py-3 bg-white/10 hover:bg-white/20 rounded-lg font-medium"
              >
                Cancel
              </button>
              <button
                onClick={submitRevision}
                disabled={!revisionFeedback}
                className="flex-1 py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 rounded-lg font-medium"
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
