import React, { useState } from 'react';
import { ArrowUp, Clock, AlertTriangle, CheckCircle, Info, BookOpen } from 'lucide-react';
import clsx from 'clsx';
import type { RecommendationItem, EvidenceItem } from '@/types';
import EvidenceDrawer from './EvidenceDrawer';

export default function RecommendationCard({ rec }: { rec: RecommendationItem }) {
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);

  const confidenceColors = {
    'High': 'bg-green-900/50 text-green-400 border-green-800',
    'Medium': 'bg-yellow-900/50 text-yellow-400 border-yellow-800',
    'Low': 'bg-orange-900/50 text-orange-400 border-orange-800'
  };

  return (
    <div className="bg-earth-card border border-earth-border rounded-xl p-5 mb-4 shadow-sm">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-medium text-white">{rec.title}</h3>
        <span className={clsx("text-xs font-medium px-2 py-1 rounded-full border", (confidenceColors as any)[rec.confidence] || confidenceColors['Medium'])}>
          {rec.confidence} Confidence
        </span>
      </div>

      <div className="bg-earth-accent/10 border-l-2 border-earth-accent p-3 rounded-r-md mb-4 text-sm text-gray-200 font-medium">
        {rec.action}
      </div>

      <div className="text-sm text-gray-400 mb-4 leading-relaxed">
        {rec.reasoning}
      </div>

      <div className="flex flex-wrap items-center gap-4 mb-4">
        <div className="flex flex-wrap gap-2">
          {rec.impacted_metrics?.map((metric, i) => (
            <div key={i} className="flex items-center gap-1 px-2 py-1 bg-earth-border rounded-md text-xs text-gray-300">
              <ArrowUp className="w-3 h-3 text-earth-light" />
              {metric}
            </div>
          ))}
        </div>
        
        <div className="flex items-center gap-1.5 text-xs text-gray-400 bg-earth-panel px-2 py-1 rounded-md border border-earth-border">
          <Clock className="w-3.5 h-3.5" />
          {rec.time_horizon}
        </div>
      </div>

      {rec.evidence && rec.evidence.length > 0 && (
        <div className="mt-4 pt-4 border-t border-earth-border">
          <h4 className="text-xs text-gray-500 font-semibold mb-2 uppercase flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5" /> Supporting Evidence ({rec.evidence.length})
          </h4>
          <div className="flex flex-col gap-2">
            {rec.evidence.map((ev, i) => (
              <button 
                key={i}
                onClick={() => setSelectedEvidence(ev)}
                className="text-left text-sm text-gray-300 hover:text-earth-light bg-earth-panel hover:bg-earth-border/50 px-3 py-2 rounded-lg border border-earth-border transition-colors truncate"
              >
                {ev.title} <span className="text-gray-500 text-xs ml-1">• {ev.source}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <EvidenceDrawer 
        evidence={selectedEvidence} 
        isOpen={!!selectedEvidence} 
        onClose={() => setSelectedEvidence(null)} 
      />
    </div>
  );
}
