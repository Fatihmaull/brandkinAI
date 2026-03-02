'use client';

import { useState } from 'react';
import { Check, RefreshCw, Sparkles } from 'lucide-react';

interface Asset {
  asset_id: string;
  oss_url: string;
  transparent_url: string;
}

interface CharacterSelectionProps {
  mascot: Asset;
  avatar: Asset;
  onSelect: (assetId: string, type: string) => void;
  onRegenerate: () => void;
}

export default function CharacterSelection({ mascot, avatar, onSelect, onRegenerate }: CharacterSelectionProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSelect = async (assetId: string, type: string) => {
    setSelectedId(assetId);
    setIsSubmitting(true);
    try {
      await onSelect(assetId, type);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="studio-card p-6">
      <div className="flex items-center gap-3 mb-2">
        <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-blue-400" />
        </div>
        <h3 className="text-lg font-medium text-white">Select Your Brand Character</h3>
      </div>
      <p className="text-sm text-gray-400 mb-6 ml-11">
        Choose the character that best represents your brand
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Mascot Option */}
        <div
          onClick={() => !isSubmitting && handleSelect(mascot.asset_id, 'mascot')}
          className={`relative cursor-pointer rounded-xl overflow-hidden border-2 transition-all ${
            selectedId === mascot.asset_id
              ? 'border-blue-500 bg-blue-500/5'
              : 'border-[#3c3c43] hover:border-[#48484f] hover:bg-[#1c1c1e]'
          } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className="aspect-square relative bg-[#0d0d0d]">
            <img
              src={mascot.oss_url}
              alt="Brand Mascot"
              className="w-full h-full object-contain p-6"
            />
          </div>
          <div className="p-4 border-t border-[#3c3c43]">
            <h4 className="text-white font-medium text-sm">Brand Mascot</h4>
            <p className="text-xs text-gray-500 mt-0.5">Full-body character</p>
          </div>
          {selectedId === mascot.asset_id && (
            <div className="absolute top-3 right-3 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center">
              <Check className="w-4 h-4" />
            </div>
          )}
        </div>

        {/* Avatar Option */}
        <div
          onClick={() => !isSubmitting && handleSelect(avatar.asset_id, 'avatar')}
          className={`relative cursor-pointer rounded-xl overflow-hidden border-2 transition-all ${
            selectedId === avatar.asset_id
              ? 'border-blue-500 bg-blue-500/5'
              : 'border-[#3c3c43] hover:border-[#48484f] hover:bg-[#1c1c1e]'
          } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <div className="aspect-square relative bg-[#0d0d0d]">
            <img
              src={avatar.oss_url}
              alt="Brand Avatar"
              className="w-full h-full object-contain p-6"
            />
          </div>
          <div className="p-4 border-t border-[#3c3c43]">
            <h4 className="text-white font-medium text-sm">Brand Avatar</h4>
            <p className="text-xs text-gray-500 mt-0.5">Portrait/headshot character</p>
          </div>
          {selectedId === avatar.asset_id && (
            <div className="absolute top-3 right-3 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center">
              <Check className="w-4 h-4" />
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mt-6">
        <button
          onClick={onRegenerate}
          disabled={isSubmitting}
          className="studio-btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isSubmitting ? 'animate-spin' : ''}`} />
          Regenerate Characters
        </button>
      </div>

      {isSubmitting && (
        <div className="mt-4 flex items-center justify-center gap-3 text-gray-400 bg-[#1c1c1e] rounded-lg p-4">
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-sm">Processing your selection...</span>
        </div>
      )}
    </div>
  );
}
