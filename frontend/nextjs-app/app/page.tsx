import Link from 'next/link';
import { ArrowRight, Sparkles, Layout, Database, Cloud, Code2, Layers, Cpu } from 'lucide-react';

export default function LandingPage() {
    const architectures = [
        { icon: <Cloud className="w-5 h-5 text-blue-400" />, title: 'Serverless Compute', desc: 'Alibaba Cloud Function Compute 3.0 handles all AI orchestration in Python 3.10' },
        { icon: <Layout className="w-5 h-5 text-purple-400" />, title: 'Static Frontend', desc: 'Next.js App Router deployed lightning-fast on Alibaba Cloud OSS' },
        { icon: <Database className="w-5 h-5 text-green-400" />, title: 'Data & Storage', desc: 'RDS MySQL for state tracking and OSS for secure, expiring asset storage' },
        { icon: <Cpu className="w-5 h-5 text-pink-400" />, title: 'AI Foundation', desc: 'Powered exclusively by Alibaba Model Studio (qwen-max, qwen-coder-plus, wanx-v1)' },
    ];

    const pipelineStages = [
        { stage: '1', title: 'Brand DNA Analysis', model: 'qwen-max', desc: 'Analyzes your text brief to generate a comprehensive brand identity, mission, and visual prompt instructions.' },
        { stage: '2', title: 'Visual Generation', model: 'wanx-v1', desc: 'Generates potential brand mascots and avatars based on the DNA, using a fixed seed (42) for style consistency.' },
        { stage: '3', title: 'Pose Pack Expansion', model: 'wanx-v1', desc: 'Once a character is selected, it generates 5 dynamic pose variations while strictly maintaining the original character IP.' },
        { stage: '4', title: 'Code Component Export', model: 'qwen-coder-plus', desc: 'Generates ready-to-use React & Tailwind CSS components matching your newly created brand aesthetic.' },
    ];

    return (
        <div className="min-h-screen bg-[#0a0a0b] text-white selection:bg-blue-500/30 overflow-x-hidden">
            {/* Background Effects */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 blur-[120px] rounded-full mix-blend-screen" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-600/20 blur-[120px] rounded-full mix-blend-screen" />
            </div>

            <div className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
                {/* Navigation / Header */}
                <nav className="flex items-center justify-between mb-24">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <Sparkles className="w-6 h-6 text-white" />
                        </div>
                        <span className="font-bold text-2xl tracking-tight">BrandKin AI</span>
                    </div>
                    <Link href="/demo" className="studio-btn-primary px-6 py-2.5 rounded-full text-sm font-medium flex items-center gap-2 group">
                        Launch Demo
                        <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </nav>

                {/* Hero Section */}
                <div className="text-center max-w-4xl mx-auto mb-32">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm font-medium mb-8">
                        <Sparkles className="w-4 h-4" />
                        Built for the Alibaba Qwen Hackathon
                    </div>
                    <h1 className="text-5xl sm:text-7xl font-bold mb-8 tracking-tight leading-[1.1]">
                        Build your entire brand identity with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">Agents.</span>
                    </h1>
                    <p className="text-lg sm:text-xl text-gray-400 mb-12 max-w-2xl mx-auto leading-relaxed">
                        BrandKin AI is an end-to-end intelligent platform that turns a single sentence into a comprehensive brand DNA, visual assets,
                        consistent mascot poses, and ready-to-use React codebase.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link href="/demo" className="w-full sm:w-auto px-8 py-4 bg-white text-black rounded-full font-semibold hover:bg-gray-100 transition-colors flex items-center justify-center gap-2 text-lg">
                            Start Building Now
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                        <a href="#architecture" className="w-full sm:w-auto px-8 py-4 bg-white/5 hover:bg-white/10 text-white rounded-full font-medium border border-white/10 transition-colors flex items-center justify-center text-lg">
                            How it Works
                        </a>
                    </div>
                </div>

                {/* Architecture Grid */}
                <div id="architecture" className="mb-32 scroll-mt-24">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold mb-4">Powered by Alibaba Cloud</h2>
                        <p className="text-gray-400 max-w-2xl mx-auto">A robust, scalable, serverless architecture designed for high-performance AI orchestration.</p>
                    </div>
                    <div className="grid sm:grid-cols-2 gap-6">
                        {architectures.map((item, i) => (
                            <div key={i} className="p-8 rounded-3xl bg-[#141415] border border-white/5 hover:border-white/10 transition-colors">
                                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-6">
                                    {item.icon}
                                </div>
                                <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                                <p className="text-gray-400 leading-relaxed">{item.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Pipeline Stages */}
                <div className="mb-32">
                    <div className="mb-16">
                        <h2 className="text-3xl font-bold mb-4 flex items-center gap-3">
                            <Layers className="w-8 h-8 text-blue-400" />
                            The AI Pipeline
                        </h2>
                        <p className="text-gray-400">How we turn a single prompt into a complete brand package.</p>
                    </div>

                    <div className="space-y-6 relative before:absolute before:inset-0 before:ml-6 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
                        {pipelineStages.map((stage, i) => (
                            <div key={i} className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active`}>
                                <div className="flex items-center justify-center w-12 h-12 rounded-full border-4 border-[#0a0a0b] bg-blue-500/20 text-blue-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 relative z-10 font-bold">
                                    {stage.stage}
                                </div>
                                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-3rem)] p-6 rounded-2xl bg-[#141415] border border-white/5 shadow-xl">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="text-xl font-bold text-white">{stage.title}</h3>
                                        <span className="px-3 py-1 bg-white/5 rounded-full text-xs font-medium text-gray-300 border border-white/10">
                                            {stage.model}
                                        </span>
                                    </div>
                                    <p className="text-gray-400 leading-relaxed">{stage.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* CTA */}
                <div className="rounded-3xl p-12 text-center bg-gradient-to-br from-blue-900/40 via-purple-900/40 to-[#141415] border border-white/10 relative overflow-hidden">
                    <div className="relative z-10">
                        <h2 className="text-3xl font-bold mb-6">Ready to see it in action?</h2>
                        <p className="text-gray-300 mb-8 max-w-xl mx-auto text-lg">
                            Launch the live interactive demo and generate your own custom brand identity in minutes.
                        </p>
                        <Link href="/demo" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-black rounded-full font-semibold hover:bg-gray-100 transition-transform hover:scale-105 active:scale-95 text-lg shadow-xl shadow-white/10">
                            <Code2 className="w-5 h-5" />
                            Explore the Product Demo
                        </Link>
                    </div>
                </div>

                {/* Footer */}
                <footer className="mt-24 pt-8 border-t border-white/10 text-center text-gray-500 text-sm flex flex-col sm:flex-row justify-between items-center">
                    <p>© 2026 BrandKin AI. Created for Alibaba Qwen Hackathon.</p>
                    <div className="flex space-x-6 mt-4 sm:mt-0">
                        <a href="https://github.com/Fatihmaull/brandkinAI" className="hover:text-white transition-colors">GitHub Repository</a>
                    </div>
                </footer>
            </div>
        </div>
    );
}
