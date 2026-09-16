import React from 'react';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { AlertCircle, Brain } from 'lucide-react';

export default function Header() {
  const { status } = useSystemStatus();

  return (
    <header className="h-16 flex items-center justify-between px-6 bg-earth-dark border-b border-earth-border">
      <h1 className="text-xl font-medium text-gray-100">AI Environmental Scientist</h1>
      <div className="flex items-center gap-3">
        {status?.demo_mode ? (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-yellow-900/50 text-yellow-500 border border-yellow-700/50 text-xs font-medium">
            <AlertCircle className="w-3.5 h-3.5" />
            Demo Mode Active
          </div>
        ) : status && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-green-900/50 text-green-500 border border-green-700/50 text-xs font-medium">
            <Brain className="w-3.5 h-3.5" />
            Ollama LLM Active
          </div>
        )}
      </div>
    </header>
  );
}
