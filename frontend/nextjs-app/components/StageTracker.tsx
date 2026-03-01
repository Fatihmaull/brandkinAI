'use client';

import { FlaskConical, Dna, Image, MousePointer, Users, Code, RefreshCw, Package } from 'lucide-react';

interface StageTrackerProps {
  currentStage: number;
  status: string;
}

const STAGES = [
  { num: 0, name: 'Initialize', icon: FlaskConical },
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
    <div className="glass rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-4 text-center">Alchemy Progress</h3>
      
      <div className="flex items-center justify-between">
        {STAGES.map((stage, index) => {
          const stageStatus = getStageStatus(stage.num);
          const Icon = stage.icon;
          
          return (
            <div key={stage.num} className="flex items-center">
              {/* Stage Dot */}
              <div className="flex flex-col items-center">
                <div className={`stage-dot ${stageStatus} flex items-center justify-center w-10 h-10`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <span className="text-xs mt-2 text-gray-400 hidden sm:block">{stage.name}</span>
              </div>
              
              {/* Connector Line */}
              {index < STAGES.length - 1 && (
                <div className={`w-8 sm:w-12 h-0.5 mx-1 ${
                  stage.num < currentStage ? 'bg-green-500' : 'bg-gray-700'
                }`} />
              )}
            </div>
          );
        })}
      </div>
      
      {/* Current Status */}
      <div className="mt-4 text-center">
        <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm ${
          status === 'failed' ? 'bg-red-500/20 text-red-400' :
          status === 'completed' ? 'bg-green-500/20 text-green-400' :
          'bg-brand-500/20 text-brand-400'
        }`}>
          {status === 'processing' && <span className="w-2 h-2 bg-brand-500 rounded-full animate-pulse" />}
          {status === 'failed' && <span className="w-2 h-2 bg-red-500 rounded-full" />}
          {status === 'completed' && <span className="w-2 h-2 bg-green-500 rounded-full" />}
          Stage {currentStage}: {STAGES[currentStage]?.name} - {status}
        </span>
      </div>
    </div>
  );
}
