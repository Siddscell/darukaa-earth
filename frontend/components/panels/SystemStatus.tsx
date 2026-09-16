import React from 'react';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { Server, Database, Brain, Network } from 'lucide-react';
import clsx from 'clsx';

export default function SystemStatusBar() {
  const { status } = useSystemStatus();

  const Dot = ({ ok }: { ok: boolean }) => (
    <div className={clsx("w-2 h-2 rounded-full", ok ? "bg-green-500" : "bg-red-500")} />
  );

  return (
    <div className="flex items-center gap-4 text-xs font-medium bg-earth-dark py-1 px-4 border-t border-earth-border text-gray-400">
      <div className="flex items-center gap-1.5" title="API Status">
        <Server className="w-3.5 h-3.5" /> <Dot ok={true} />
      </div>
      <div className="flex items-center gap-1.5" title="Relational Database">
        <Database className="w-3.5 h-3.5" /> <Dot ok={!!status?.database} />
      </div>
      <div className="flex items-center gap-1.5" title="Vector Database">
        <Network className="w-3.5 h-3.5" /> <Dot ok={!!status?.vector_db} />
      </div>
      <div className="flex items-center gap-1.5" title="LLM Provider">
        <Brain className="w-3.5 h-3.5" /> <Dot ok={!!status?.ollama_available} />
        {status?.ollama_model && <span className="opacity-70 ml-1 truncate max-w-[100px]">({status.ollama_model})</span>}
      </div>
      {status?.knowledge_base_docs !== undefined && (
        <div className="ml-auto opacity-70">
          {status.knowledge_base_docs} Docs Loaded
        </div>
      )}
    </div>
  );
}
