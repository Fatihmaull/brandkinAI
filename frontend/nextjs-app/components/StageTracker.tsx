'use client';

import { Dna, Image, MousePointer, Users, Code, RefreshCw, Package, Check } from 'lucide-react';

interface StageTrackerProps {
  currentStage: number;
  status: string;
}

const STAGES = [
  { num: 1, name: 'Brand DNA', icon: Dna },
  { num: 2, name: 'Visual Gen', icon: Image },
  { num: 3, name: 'Selection', icon: MousePointer },
  { num: 4, name: 'Pose Pack', icon: Users },
  { num: 5, name: 'Code Export', icon: Code },
  { num: 6, name: 'Revision', icon: RefreshCw },
  { num: 7, name: 'Assembly', icon: Package },
];

export default function StageTracker({ currentStage, status }: StageTrackerProps) {
  const getStageStatus = (stageNum: number): 'pending' | 'processing' | 'completed' | 'error' => {
    if (status === 'failed') return stageNum === currentStage ? 'error' : 'pending';
    if (stageNum < currentStage) return 'completed';
    if (stageNum === currentStage) return 'processing';
    return 'pending';
  };

  return (
    <div className="flex items-center gap-2">
      {STAGES.map((stage, index) => {
        const stageStatus = getStageStatus(stage.num);
        const Icon = stage.icon;
        const isActive = stage.num === currentStage;
        
        return (
          <div key={stage.num} className="flex items-center">
            {/* Stage Indicator */}
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-xs ${
              stageStatus === 'completed' ? 'text-green-400' :
              stageStatus === 'processing' ? 'text-blue-400 bg-blue-500/10' :
              'text-gray-600'
            }`}>
              {stageStatus === 'completed' ? (
                <Check className="w-3 h-3" />
              ) : (
                <Icon className="w-3 h-3" />
              )}
              <span className="hidden sm:inline">{stage.name}</span>
            </div>
            
            {/* Connector */}
            {index < STAGES.length - 1 && (
              <div className="w-4 h-px bg-gray-700 mx-1" />
            )}
          </div>
        );
      })}
    </div>
  );
}
