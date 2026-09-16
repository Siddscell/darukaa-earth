import React, { useState } from 'react';
import { ChevronDown, ChevronRight, BrainCircuit } from 'lucide-react';
import type { ReasoningTrace as IReasoningTrace } from '@/types';

export default function ReasoningTrace({ trace }: { trace: IReasoningTrace }) {
  const [expanded, setExpanded] = useState(false);

  if (!trace) return null;

  return (
    <div className="mt-4 border border-earth-border rounded-lg bg-earth-panel overflow-hidden text-sm">
      <button 
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full px-3 py-2 text-gray-400 hover:text-gray-200 hover:bg-earth-card transition-colors"
      >
        {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        <BrainCircuit className="w-4 h-4" />
        <span className="font-medium">How this was generated</span>
      </button>
      
      {expanded && (
        <div className="p-4 border-t border-earth-border space-y-4">
          <div>
            <h4 className="text-xs text-gray-500 uppercase font-semibold mb-2">Variables Detected</h4>
            <div className="flex flex-wrap gap-1.5">
              {trace.variables_detected?.map((v, i) => (
                <span key={i} className="px-2 py-0.5 bg-earth-light/10 text-earth-light rounded text-xs">{v}</span>
              ))}
            </div>
          </div>
          
          {trace.missing_variables?.length > 0 && (
            <div>
              <h4 className="text-xs text-gray-500 uppercase font-semibold mb-2">Missing Variables</h4>
              <div className="flex flex-wrap gap-1.5">
                {trace.missing_variables.map((v, i) => (
                  <span key={i} className="px-2 py-0.5 bg-red-900/30 text-red-400 rounded text-xs">{v}</span>
                ))}
              </div>
            </div>
          )}
          
          <div>
            <h4 className="text-xs text-gray-500 uppercase font-semibold mb-2">Environmental Relationships</h4>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              {trace.environmental_relationships?.map((rel, i) => (
                <li key={i}>{rel}</li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-xs text-gray-500 uppercase font-semibold mb-2">Retrieved Evidence ({trace.retrieved_evidence_count})</h4>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              {trace.evidence_titles?.map((title, i) => (
                <li key={i} className="truncate">{title}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
