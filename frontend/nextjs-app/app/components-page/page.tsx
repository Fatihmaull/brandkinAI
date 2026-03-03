'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Code, Copy, Check, ArrowLeft, FileCode, Palette, Terminal } from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';

interface CodeExport {
  export_id: string;
  component_name: string;
  react_code: string;
  css_keyframes: string;
  usage_snippet: string;
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
        <p className="text-gray-400 text-sm">Loading components...</p>
      </div>
    </div>
  );
}

function ComponentsContent() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get('id');
  
  const [project, setProject] = useState<Project | null>(null);
  const [exports, setExports] = useState<CodeExport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'code' | 'css' | 'preview'>('code');
  const [copied, setCopied] = useState(false);
  const [selectedExport, setSelectedExport] = useState<CodeExport | null>(null);

  useEffect(() => {
    if (projectId) {
      loadData(projectId);
    } else {
      setIsLoading(false);
    }
  }, [projectId]);

  const loadData = async (id: string) => {
    try {
      const [projectRes, codeRes] = await Promise.all([
        api.getProject(id),
        api.getCodeExports(id)
      ]);
      
      if (projectRes.data) {
        setProject(projectRes.data as Project);
      }
      if (codeRes.data) {
        const codeExportsData = (codeRes.data as any).code_exports;
        const codeExports = Array.isArray(codeExportsData) ? codeExportsData : [];
        setExports(codeExports);
        if (codeExports.length > 0) {
          setSelectedExport(codeExports[0]);
        }
      } else {
        setExports([]);
      }
    } catch (error) {
      console.error('Error loading code exports:', error);
      setExports([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getActiveContent = () => {
    if (!selectedExport) return '';
    
    switch (activeTab) {
      case 'code':
        return selectedExport.react_code;
      case 'css':
        return selectedExport.css_keyframes;
      case 'preview':
        return selectedExport.usage_snippet;
      default:
        return '';
    }
  };

  const getTabIcon = (tab: 'code' | 'css' | 'preview') => {
    switch (tab) {
      case 'code':
        return <FileCode className="w-4 h-4" />;
      case 'css':
        return <Palette className="w-4 h-4" />;
      case 'preview':
        return <Terminal className="w-4 h-4" />;
    }
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
          <Link href="/" className="studio-btn inline-block">
            Go Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0d0d0d]">
      {/* Header */}
      <header className="border-b border-[#3c3c43]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-gray-400 hover:text-white transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div>
                <h1 className="text-xl font-semibold">React Components</h1>
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
                href={`/assets?id=${projectId}`}
                className="studio-btn-secondary text-sm"
              >
                View Assets
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {exports.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 px-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mb-6">
              <Code className="w-8 h-8 text-gray-500" />
            </div>
            <h3 className="text-xl font-medium text-white mb-2">No components yet</h3>
            <p className="text-gray-400 text-center max-w-md mb-6">
              Your generated React components will appear here. Complete your project to export code.
            </p>
            <Link href={`/?project=${projectId}`} className="studio-btn">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Continue Project
            </Link>
          </div>
        ) : (
          <div className="studio-card p-6">
            {/* Component Selector */}
            {exports.length > 1 && (
              <div className="mb-6">
                <label className="text-sm text-gray-400 mb-2 block">Select Component</label>
                <select
                  value={selectedExport?.export_id}
                  onChange={(e) => {
                    const exp = exports.find(ex => ex.export_id === e.target.value);
                    if (exp) setSelectedExport(exp);
                  }}
                  className="studio-input w-full max-w-md"
                >
                  {exports.map(exp => (
                    <option key={exp.export_id} value={exp.export_id}>
                      {exp.component_name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-2 mb-4 p-1 bg-[#1c1c1e] rounded-lg">
              {(['code', 'css', 'preview'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                    activeTab === tab 
                      ? 'bg-[#3c3c43] text-white' 
                      : 'text-gray-400 hover:text-gray-200'
                  }`}
                >
                  {getTabIcon(tab)}
                  {tab === 'code' ? 'React Code' : tab === 'css' ? 'CSS Keyframes' : 'Usage'}
                </button>
              ))}
            </div>

            {/* Code Display */}
            <div className="relative">
              <pre className="bg-[#0d0d0d] rounded-lg p-4 overflow-x-auto text-sm font-mono text-gray-300 max-h-96 overflow-y-auto border border-[#3c3c43]">
                <code>{getActiveContent()}</code>
              </pre>
              
              {/* Copy Button */}
              <button
                onClick={() => handleCopy(getActiveContent())}
                className="absolute top-3 right-3 p-2 bg-[#1c1c1e] hover:bg-[#2c2c2e] rounded-lg transition-colors text-gray-400 hover:text-white"
                title="Copy to clipboard"
              >
                {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>

            {/* Component Info */}
            {selectedExport && (
              <div className="mt-4 p-4 bg-[#1c1c1e] rounded-lg border border-[#3c3c43]">
                <p className="text-sm text-gray-400">
                  <span className="font-medium text-gray-300">Component:</span> {selectedExport.component_name}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  <span className="font-medium text-gray-400">Export ID:</span> {selectedExport.export_id}
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default function ComponentsPage() {
  return (
    <Suspense fallback={<LoadingState />}>
      <ComponentsContent />
    </Suspense>
  );
}
