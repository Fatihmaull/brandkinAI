'use client';

import { useState } from 'react';
import { Code, Copy, Check, Play } from 'lucide-react';

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

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Code className="w-6 h-6 text-brand-500" />
          <h3 className="text-xl font-bold">Generated React Component</h3>
        </div>
        
        {/* Component Selector */}
        {exports.length > 1 && (
          <select
            value={selectedExport?.export_id}
            onChange={(e) => {
              const exp = exports.find(ex => ex.export_id === e.target.value);
              if (exp) setSelectedExport(exp);
            }}
            className="px-3 py-2 rounded-lg bg-white/5 border border-white/10"
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
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab('code')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'code' ? 'bg-brand-500 text-white' : 'bg-white/10 hover:bg-white/20'
          }`}
        >
          React Code
        </button>
        <button
          onClick={() => setActiveTab('css')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'css' ? 'bg-brand-500 text-white' : 'bg-white/10 hover:bg-white/20'
          }`}
        >
          CSS Keyframes
        </button>
        <button
          onClick={() => setActiveTab('preview')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeTab === 'preview' ? 'bg-brand-500 text-white' : 'bg-white/10 hover:bg-white/20'
          }`}
        >
          Usage
        </button>
      </div>

      {/* Code Display */}
      <div className="relative">
        <pre className="bg-gray-900 rounded-lg p-4 overflow-x-auto text-sm font-mono text-gray-300 max-h-96 overflow-y-auto">
          <code>{getActiveContent()}</code>
        </pre>
        
        {/* Copy Button */}
        <button
          onClick={() => handleCopy(getActiveContent())}
          className="absolute top-2 right-2 p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
          title="Copy to clipboard"
        >
          {copied ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
        </button>
      </div>

      {/* Component Info */}
      {selectedExport && (
        <div className="mt-4 p-4 bg-white/5 rounded-lg">
          <p className="text-sm text-gray-400">
            <span className="font-semibold text-gray-300">Component:</span> {selectedExport.component_name}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            <span className="font-semibold text-gray-300">Export ID:</span> {selectedExport.export_id}
          </p>
        </div>
      )}
    </div>
  );
}
