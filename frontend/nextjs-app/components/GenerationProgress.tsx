'use client';

import { useState, useEffect } from 'react';
import {
    Dna, Image, MousePointer, Users, Code, RefreshCw, Package,
    Check, Sparkles, Loader2
} from 'lucide-react';

interface GenerationProgressProps {
    currentStage: number;
    status: string;
}

const STAGES = [
    {
        num: 1,
        name: 'Brand DNA Analysis',
        icon: Dna,
        description: 'AI is analyzing your brand brief and generating your unique Brand DNA...',
        details: ['Analyzing brand personality', 'Defining visual direction', 'Building color palette', 'Designing mascot concept']
    },
    {
        num: 2,
        name: 'Visual Identity',
        icon: Image,
        description: 'Generating your brand mascot and avatar with AI...',
        details: ['Crafting mascot design', 'Generating character image', 'Creating avatar portrait', 'Applying brand colors']
    },
    {
        num: 3,
        name: 'Character Selection',
        icon: MousePointer,
        description: 'Review and select your brand character.',
        details: ['Choose mascot or avatar', 'Request revisions if needed']
    },
    {
        num: 4,
        name: 'Pose Collection',
        icon: Users,
        description: 'Generating character poses for different use cases...',
        details: ['Waving pose', 'Pointing pose', 'Thoughtful pose', 'Celebrating pose']
    },
    {
        num: 5,
        name: 'Code Components',
        icon: Code,
        description: 'Building React components and CSS for your brand...',
        details: ['Creating React widget', 'Generating CSS styles', 'Building usage examples']
    },
    {
        num: 6,
        name: 'Refinement',
        icon: RefreshCw,
        description: 'Polishing and refining your brand assets...',
        details: ['Generating LinkedIn banner', 'Finalizing visual assets']
    },
    {
        num: 7,
        name: 'Brand Kit Assembly',
        icon: Package,
        description: 'Packaging your complete brand kit...',
        details: ['Bundling all assets', 'Creating ZIP download', 'Generating final package']
    },
];

export default function GenerationProgress({ currentStage, status }: GenerationProgressProps) {
    const [activeDetailIdx, setActiveDetailIdx] = useState(0);
    const [elapsed, setElapsed] = useState(0);

    // Cycle through detail items for the active stage
    useEffect(() => {
        const currentStageData = STAGES.find(s => s.num === currentStage);
        if (!currentStageData) return;

        const interval = setInterval(() => {
            setActiveDetailIdx(prev => (prev + 1) % currentStageData.details.length);
        }, 2500);

        return () => clearInterval(interval);
    }, [currentStage]);

    // Track elapsed time
    useEffect(() => {
        const interval = setInterval(() => {
            setElapsed(prev => prev + 1);
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    // Reset detail index when stage changes
    useEffect(() => {
        setActiveDetailIdx(0);
    }, [currentStage]);

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return m > 0 ? `${m}m ${s}s` : `${s}s`;
    };

    const progressPercent = Math.min(((currentStage - 1) / STAGES.length) * 100 +
        (status === 'processing' ? 8 : 14), 100);

    const currentStageData = STAGES.find(s => s.num === currentStage);

    return (
        <div className="studio-card overflow-hidden">
            {/* Top gradient accent bar */}
            <div className="h-1 bg-gradient-to-r from-blue-600 via-purple-500 to-pink-500 relative overflow-hidden">
                <div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                    style={{
                        animation: 'shimmer 2s infinite',
                    }}
                />
            </div>

            <div className="p-8">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <div className="relative">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center border border-blue-500/30">
                            <Sparkles className="w-7 h-7 text-blue-400" />
                        </div>
                        {/* Pulse ring */}
                        <div className="absolute inset-0 rounded-2xl border-2 border-blue-500/40 animate-ping" style={{ animationDuration: '2s' }} />
                    </div>
                    <div>
                        <h2 className="text-xl font-semibold text-white">Creating Your Brand</h2>
                        <p className="text-sm text-gray-400 mt-0.5">
                            Elapsed: {formatTime(elapsed)}
                        </p>
                    </div>
                </div>

                {/* Overall Progress Bar */}
                <div className="mb-8">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-gray-400">
                            Stage {currentStage} of {STAGES.length}
                        </span>
                        <span className="text-xs text-gray-400">
                            {Math.round(progressPercent)}%
                        </span>
                    </div>
                    <div className="h-2 bg-[#1c1c1e] rounded-full overflow-hidden">
                        <div
                            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-1000 ease-out relative"
                            style={{ width: `${progressPercent}%` }}
                        >
                            {/* Animated glow on the progress bar edge */}
                            <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-r from-transparent to-white/30 rounded-full" />
                        </div>
                    </div>
                </div>

                {/* Stage Steps */}
                <div className="space-y-1">
                    {STAGES.map((stage, index) => {
                        const isCompleted = stage.num < currentStage;
                        const isCurrent = stage.num === currentStage;
                        const isPending = stage.num > currentStage;
                        const Icon = stage.icon;

                        return (
                            <div key={stage.num}>
                                <div className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-500 ${isCurrent
                                        ? 'bg-blue-500/10 border border-blue-500/20'
                                        : isCompleted
                                            ? 'opacity-60'
                                            : 'opacity-30'
                                    }`}>
                                    {/* Status Icon */}
                                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-500 ${isCompleted
                                            ? 'bg-green-500/20'
                                            : isCurrent
                                                ? 'bg-blue-500/20'
                                                : 'bg-[#1c1c1e]'
                                        }`}>
                                        {isCompleted ? (
                                            <Check className="w-4 h-4 text-green-400" />
                                        ) : isCurrent ? (
                                            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                                        ) : (
                                            <Icon className="w-4 h-4 text-gray-600" />
                                        )}
                                    </div>

                                    {/* Stage Info */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span className={`text-sm font-medium ${isCompleted ? 'text-green-400' :
                                                    isCurrent ? 'text-white' : 'text-gray-600'
                                                }`}>
                                                {stage.name}
                                            </span>
                                            {isCompleted && (
                                                <span className="text-xs text-green-500/60">Done</span>
                                            )}
                                        </div>

                                        {/* Current stage detail animation */}
                                        {isCurrent && status === 'processing' && (
                                            <div className="mt-1 overflow-hidden">
                                                <p className="text-xs text-blue-300/70 animate-pulse">
                                                    {stage.details[activeDetailIdx]}...
                                                </p>
                                            </div>
                                        )}
                                    </div>

                                    {/* Stage number */}
                                    <span className={`text-xs font-mono ${isCurrent ? 'text-blue-400' : 'text-gray-700'
                                        }`}>
                                        {stage.num}/{STAGES.length}
                                    </span>
                                </div>

                                {/* Connector line between stages */}
                                {index < STAGES.length - 1 && (
                                    <div className="ml-[1.65rem] h-1 flex items-center">
                                        <div className={`w-px h-full transition-colors duration-500 ${isCompleted ? 'bg-green-500/30' : 'bg-gray-800'
                                            }`} />
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Current stage description */}
                {currentStageData && status === 'processing' && (
                    <div className="mt-6 px-4 py-3 bg-[#1c1c1e] rounded-xl border border-[#2c2c2e]">
                        <div className="flex items-start gap-3">
                            <div className="mt-0.5">
                                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-300">{currentStageData.description}</p>
                                <p className="text-xs text-gray-500 mt-1">
                                    Please wait — AI processing typically takes 15-30 seconds per stage.
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Awaiting user action */}
                {status === 'awaiting_selection' && (
                    <div className="mt-6 px-4 py-3 bg-yellow-500/10 rounded-xl border border-yellow-500/20">
                        <div className="flex items-start gap-3">
                            <MousePointer className="w-4 h-4 text-yellow-400 mt-0.5" />
                            <div>
                                <p className="text-sm text-yellow-300">Your turn! Select your brand character below.</p>
                                <p className="text-xs text-yellow-400/50 mt-1">
                                    Choose between the mascot and avatar, then processing will continue.
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* CSS for shimmer animation */}
            <style jsx>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
      `}</style>
        </div>
    );
}
