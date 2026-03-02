'use client';

import { useState } from 'react';
import { Code, Copy, Check, FileCode, Palette, Terminal } from 'lucide-react';

interface CodeExport {
  export_id: string;
  component_name: string;
  react_code: string;
  css_keyframes: string;
  usage_snippet: string;
}

interface CodePreviewProps {
  exports: CodeExport[];
}

export default function CodePreview({ exports }: CodePreviewProps) {
  const [activeTab, setActiveTab] = useState<'code' | 'css' | 'preview'>('code');
  const [copied, setCopied] = useState(false);
  const [selectedExport, setSelectedExport] = useState<CodeExport | null>(exports[0] || null);

  if (!exports.length) return null;

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

  return (
    <div className="studio-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
            <Code className="w-4 h-4 text-blue-400" />
          </div>
          <h3 className="text-lg font-medium text-white">Generated React Component</h3>
        </div>
        
        {/* Component Selector */}
        {exports.length > 1 && (
          <select
            value={selectedExport?.export_id}
            onChange={(e) => {
              const exp = exports.find(ex => ex.export_id === e.target.value);
              if (exp) setSelectedExport(exp);
            }}
            className="studio-input py-2 text-sm"
          >
            {exports.map(exp => (
              <option key={exp.export_id} value={exp.export_id}>
                {exp.component_name}
              </option>
            ))}
          </select>
        )}
      </div>

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
  );
}
