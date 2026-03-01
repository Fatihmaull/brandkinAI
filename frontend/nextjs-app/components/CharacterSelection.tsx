'use client';

import { useState } from 'react';
import Image from 'next/image';

interface Asset {
  asset_id: string;
  oss_url: string;
  transparent_url: string;
}

interface CharacterSelectionProps {
  mascot: Asset;
  avatar: Asset;
  onSelect: (assetId: string) => void;
  onRegenerate: () => void;
}

export default function CharacterSelection({ mascot, avatar, onSelect, onRegenerate }: CharacterSelectionProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSelect = async (assetId: string) => {
    setSelectedId(assetId);
    setIsSubmitting(true);
    try {
      await onSelect(assetId);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 mt-6">
      <h3 className="text-xl font-semibold text-white mb-4">Select Your Brand Character</h3>
      <p className="text-gray-400 mb-6">
        Choose the character that best represents your brand. This will be used for all pose variations and code components.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Mascot Option */}
        <div
          onClick={() => handleSelect(mascot.asset_id)}
          className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
            selectedId === mascot.asset_id
              ? 'border-green-500 ring-2 ring-green-500'
              : 'border-gray-600 hover:border-gray-500'
          }`}
        >
          <div className="aspect-square relative bg-gray-700">
            <img
              src={mascot.oss_url}
              alt="Brand Mascot"
              className="w-full h-full object-contain"
            />
          </div>
          <div className="p-4 bg-gray-750">
            <h4 className="text-white font-medium">Brand Mascot</h4>
            <p className="text-sm text-gray-400">Full-body character</p>
          </div>
          {selectedId === mascot.asset_id && (
            <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </div>

        {/* Avatar Option */}
        <div
          onClick={() => handleSelect(avatar.asset_id)}
          className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
            selectedId === avatar.asset_id
              ? 'border-green-500 ring-2 ring-green-500'
              : 'border-gray-600 hover:border-gray-500'
          }`}
        >
          <div className="aspect-square relative bg-gray-700">
            <img
              src={avatar.oss_url}
              alt="Brand Avatar"
              className="w-full h-full object-contain"
            />
          </div>
          <div className="p-4 bg-gray-750">
            <h4 className="text-white font-medium">Brand Avatar</h4>
            <p className="text-sm text-gray-400">Portrait/headshot character</p>
          </div>
          {selectedId === avatar.asset_id && (
            <div className="absolute top-2 right-2 bg-green-500 text-white rounded-full p-1">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mt-6">
        <button
          onClick={onRegenerate}
          disabled={isSubmitting}
          className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50 transition-colors"
        >
          Regenerate Characters
        </button>
      </div>

      {isSubmitting && (
        <div className="mt-4 text-center text-gray-400">
          <div className="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
          Processing selection...
        </div>
      )}
    </div>
  );
}
