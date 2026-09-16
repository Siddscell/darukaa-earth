const fs = require('fs');
const path = require('path');

const files = {
  'components/layout/Header.tsx': `import React from 'react';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import { AlertCircle } from 'lucide-react';

export default function Header() {
  const { status } = useSystemStatus();

  return (
    <header className="h-16 flex items-center justify-between px-6 bg-earth-dark border-b border-earth-border">
      <h1 className="text-xl font-medium text-gray-100">AI Environmental Scientist</h1>
      <div className="flex items-center gap-3">
        {status?.demo_mode && (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-yellow-900/50 text-yellow-500 border border-yellow-700/50 text-xs font-medium">
            <AlertCircle className="w-3.5 h-3.5" />
            Demo Mode Active
          </div>
        )}
      </div>
    </header>
  );
}`,
  'components/chat/UserMessage.tsx': `import React from 'react';

export default function UserMessage({ content }: { content: string }) {
  return (
    <div className="flex justify-end mb-4">
      <div className="bg-earth-accent/20 border border-earth-accent/30 text-gray-100 px-4 py-3 rounded-2xl rounded-tr-sm max-w-[85%] text-sm leading-relaxed">
        {content}
      </div>
    </div>
  );
}`,
  'components/chat/ReasoningTrace.tsx': `import React, { useState } from 'react';
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
}`,
  'components/chat/EvidenceDrawer.tsx': `import React from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X, ExternalLink, BookOpen } from 'lucide-react';
import type { EvidenceItem } from '@/types';

interface Props {
  evidence: EvidenceItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function EvidenceDrawer({ evidence, isOpen, onClose }: Props) {
  if (!evidence) return null;

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40" />
        <Dialog.Content className="fixed right-0 top-0 bottom-0 w-full max-w-md bg-earth-panel border-l border-earth-border p-6 shadow-2xl z-50 overflow-y-auto outline-none focus:outline-none flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <div className="flex items-center gap-2 text-earth-accent">
              <BookOpen className="w-5 h-5" />
              <Dialog.Title className="text-lg font-medium text-gray-100">Source Evidence</Dialog.Title>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-white p-1 rounded-full hover:bg-earth-card">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="space-y-6 flex-1">
            <div>
              <h3 className="text-xl font-medium text-white mb-2">{evidence.title}</h3>
              <div className="flex flex-wrap gap-2 text-sm text-gray-400">
                <span>{evidence.source}</span>
                {evidence.year && <span>• {evidence.year}</span>}
              </div>
            </div>

            {evidence.url && (
              <a href={evidence.url} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-earth-accent hover:text-earth-light transition-colors text-sm font-medium">
                <ExternalLink className="w-4 h-4" /> View Original Source
              </a>
            )}

            <div className="flex flex-wrap gap-2 pt-2">
              {evidence.topic && (
                <span className="px-2.5 py-1 bg-earth-card rounded-md text-xs font-medium text-gray-300">Topic: {evidence.topic}</span>
              )}
              {evidence.variables?.map((v, i) => (
                <span key={i} className="px-2.5 py-1 bg-earth-border rounded-md text-xs font-medium text-gray-400">{v}</span>
              ))}
            </div>

            <div className="pt-4 border-t border-earth-border">
              <h4 className="text-sm text-gray-400 uppercase tracking-wider font-semibold mb-3">Supporting Excerpt</h4>
              <blockquote className="border-l-2 border-earth-accent pl-4 text-gray-300 italic text-sm leading-relaxed">
                "{evidence.supporting_excerpt}"
              </blockquote>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}`,
  'components/chat/RecommendationCard.tsx': `import React, { useState } from 'react';
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
}`,
  'components/chat/AssistantMessage.tsx': `import React from 'react';
import { Bot, AlertCircle } from 'lucide-react';
import type { ChatMessage } from '@/types';
import RecommendationCard from './RecommendationCard';
import ReasoningTrace from './ReasoningTrace';

export default function AssistantMessage({ msg }: { msg: ChatMessage }) {
  return (
    <div className="flex gap-4 mb-6">
      <div className="w-8 h-8 rounded-full bg-earth-border flex items-center justify-center shrink-0 mt-1">
        <Bot className="w-5 h-5 text-earth-accent" />
      </div>
      <div className="flex-1 max-w-[85%]">
        <div className="text-sm font-medium text-gray-400 mb-1">AI Environmental Scientist</div>
        
        <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap mb-4">
          {msg.content}
        </div>

        {msg.needs_clarification && msg.clarification_questions && msg.clarification_questions.length > 0 && (
          <div className="bg-orange-900/20 border border-orange-900/50 rounded-lg p-4 mb-4">
            <div className="flex items-center gap-2 text-orange-400 font-medium text-sm mb-2">
              <AlertCircle className="w-4 h-4" /> Additional Information Needed
            </div>
            <ul className="list-disc list-inside text-sm text-gray-300 space-y-1 ml-2">
              {msg.clarification_questions.map((q, i) => <li key={i}>{q}</li>)}
            </ul>
          </div>
        )}

        {msg.recommendations && msg.recommendations.map((rec, i) => (
          <RecommendationCard key={i} rec={rec} />
        ))}

        {msg.reasoning_trace && (
          <ReasoningTrace trace={msg.reasoning_trace} />
        )}
      </div>
    </div>
  );
}`,
  'components/chat/ChatInterface.tsx': `import React, { useRef, useEffect, useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import type { ChatMessage } from '@/types';
import UserMessage from './UserMessage';
import AssistantMessage from './AssistantMessage';

interface Props {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
}

export default function ChatInterface({ messages, isLoading, onSendMessage }: Props) {
  const [input, setInput] = useState('');
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-earth-dark">
      <div className="flex-1 overflow-y-auto p-4 md:p-6 scroll-smooth">
        {messages.map((msg) => (
          msg.role === 'user' 
            ? <UserMessage key={msg.id} content={msg.content} />
            : <AssistantMessage key={msg.id} msg={msg} />
        ))}
        {isLoading && (
          <div className="flex gap-4 mb-6 animate-pulse">
             <div className="w-8 h-8 rounded-full bg-earth-border flex items-center justify-center shrink-0 mt-1" />
             <div className="flex items-center text-sm text-gray-500">Thinking<span className="ml-1 tracking-widest">...</span></div>
          </div>
        )}
        <div ref={endRef} />
      </div>
      
      <div className="p-4 border-t border-earth-border bg-earth-panel">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about biodiversity, soil health, or interventions..."
            className="w-full bg-earth-card border border-earth-border rounded-full py-3 pl-5 pr-12 text-sm text-white focus:outline-none focus:border-earth-accent focus:ring-1 focus:ring-earth-accent placeholder-gray-500"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 rounded-full bg-earth-accent text-white hover:bg-earth-light transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </form>
        <div className="text-center mt-2 text-[10px] text-gray-600">
          Darukaa.Earth AI may produce inaccurate information about environmental science.
        </div>
      </div>
    </div>
  );
}`,
  'components/panels/EnvironmentalPanel.tsx': `import React from 'react';
import type { EnvironmentalProfile } from '@/types';
import { Droplet, ThermometerSun, Leaf, Sprout, Factory, MapPin } from 'lucide-react';

export default function EnvironmentalPanel({ profile }: { profile: EnvironmentalProfile | null }) {
  if (!profile) {
    return (
      <div className="p-6 text-center text-gray-500 flex flex-col items-center justify-center h-full">
        <MapPin className="w-12 h-12 mb-3 opacity-20" />
        <p className="text-sm">No active environmental profile.</p>
        <p className="text-xs mt-1">Start a conversation or load a scenario.</p>
      </div>
    );
  }

  const Metric = ({ label, value }: { label: string, value: any }) => (
    <div className="flex justify-between items-center py-1.5 border-b border-earth-border/50 last:border-0">
      <span className="text-xs text-gray-400">{label}</span>
      <span className="text-xs font-medium text-gray-200">
        {value !== undefined && value !== null && value !== '' ? value : <span className="text-gray-600">Missing</span>}
      </span>
    </div>
  );

  return (
    <div className="p-4 space-y-4 overflow-y-auto h-full pb-20">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-white mb-1">Context Profile</h2>
        <div className="text-sm text-earth-accent flex items-center gap-1.5">
          <MapPin className="w-3.5 h-3.5" />
          {profile.region || 'Unknown Region'}
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Droplet className="w-4 h-4 text-blue-400" /> Soil Health
        </h3>
        <div className="space-y-1">
          <Metric label="pH Level" value={profile.soil?.ph} />
          <Metric label="Organic Carbon (%)" value={profile.soil?.organic_carbon_percent} />
          <Metric label="Moisture (%)" value={profile.soil?.moisture_percent} />
          <Metric label="Structure" value={profile.soil?.structure} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <ThermometerSun className="w-4 h-4 text-orange-400" /> Climate
        </h3>
        <div className="space-y-1">
          <Metric label="Temp (°C)" value={profile.climate?.temperature_c} />
          <Metric label="Rainfall (mm)" value={profile.climate?.rainfall_mm} />
          <Metric label="Pattern" value={profile.climate?.rainfall_pattern} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Sprout className="w-4 h-4 text-green-400" /> Land Use
        </h3>
        <div className="space-y-1">
          <Metric label="Primary Type" value={profile.land_use?.primary_type} />
          <Metric label="Cropping System" value={profile.land_use?.cropping_system} />
          <Metric label="Main Crop" value={profile.land_use?.crop} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Leaf className="w-4 h-4 text-emerald-400" /> Biodiversity
        </h3>
        <div className="space-y-1">
          <Metric label="Species Richness" value={profile.biodiversity?.species_richness} />
          <Metric label="Habitat Diversity" value={profile.biodiversity?.habitat_diversity} />
          <Metric label="Pollinators" value={profile.biodiversity?.pollinator_presence} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Factory className="w-4 h-4 text-gray-400" /> Human Impact
        </h3>
        <div className="space-y-1">
          <Metric label="Pesticide Pressure" value={profile.human_impact?.pesticide_pressure} />
          <Metric label="Pollution Level" value={profile.human_impact?.pollution_level} />
          <Metric label="Deforestation" value={profile.human_impact?.deforestation_pressure} />
        </div>
      </div>
    </div>
  );
}`,
  'components/panels/ScenarioLoader.tsx': `import React from 'react';
import { DEMO_SCENARIOS } from '@/lib/scenarios';
import type { DemoScenario } from '@/types';
import { Sparkles, ArrowRight } from 'lucide-react';

interface Props {
  onSelect: (scenario: DemoScenario) => void;
}

export default function ScenarioLoader({ onSelect }: Props) {
  return (
    <div className="w-full max-w-4xl mx-auto p-4 md:p-8">
      <div className="text-center mb-10 mt-10">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-earth-card border border-earth-border mb-4 text-earth-accent shadow-lg shadow-black/20">
          <Sparkles className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-white mb-2">Welcome to Darukaa.Earth</h1>
        <p className="text-gray-400 text-sm max-w-lg mx-auto">
          Our AI Scientist helps you analyze environmental profiles, identify degradation patterns, and recommends context-specific interventions.
        </p>
      </div>

      <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4 px-1">Select a Demo Scenario</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {DEMO_SCENARIOS.map((scenario) => (
          <button
            key={scenario.id}
            onClick={() => onSelect(scenario)}
            className="text-left bg-earth-panel border border-earth-border p-5 rounded-xl hover:bg-earth-card hover:border-earth-accent/50 transition-all group flex flex-col h-full"
          >
            <h4 className="text-base font-medium text-white mb-1 group-hover:text-earth-accent transition-colors">{scenario.name}</h4>
            <p className="text-xs text-gray-400 mb-4 flex-1">{scenario.description}</p>
            <div className="flex items-center justify-between text-xs font-medium text-earth-light mt-auto pt-4 border-t border-earth-border/50">
              Load Profile & Start <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}`,
  'components/panels/SystemStatus.tsx': `import React from 'react';
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
        <Brain className="w-3.5 h-3.5" /> <Dot ok={!!status?.llm_provider} />
        {status?.ollama_model && <span className="opacity-70 ml-1 truncate max-w-[100px]">({status.ollama_model})</span>}
      </div>
      {status?.knowledge_base_docs !== undefined && (
        <div className="ml-auto opacity-70">
          {status.knowledge_base_docs} Docs Loaded
        </div>
      )}
    </div>
  );
}`,
  'app/page.tsx': `// page
'use client';
import React from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';
import ChatInterface from '@/components/chat/ChatInterface';
import EnvironmentalPanel from '@/components/panels/EnvironmentalPanel';
import ScenarioLoader from '@/components/panels/ScenarioLoader';
import SystemStatusBar from '@/components/panels/SystemStatus';
import { useChat } from '@/hooks/useChat';

export default function Dashboard() {
  const { messages, isLoading, environmentalProfile, sendMessage, loadScenario } = useChat();

  return (
    <div className="flex h-screen bg-earth-dark text-earth-text overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        
        <div className="flex-1 flex overflow-hidden relative">
          <main className="flex-1 flex flex-col min-w-0 bg-earth-dark">
            {messages.length === 0 ? (
              <div className="flex-1 overflow-y-auto">
                <ScenarioLoader onSelect={loadScenario} />
              </div>
            ) : (
              <ChatInterface 
                messages={messages} 
                isLoading={isLoading} 
                onSendMessage={sendMessage} 
              />
            )}
          </main>
          
          <aside className="hidden lg:block w-[320px] bg-earth-panel border-l border-earth-border shrink-0">
            <EnvironmentalPanel profile={environmentalProfile} />
          </aside>
        </div>
        
        <SystemStatusBar />
      </div>
    </div>
  );
}`
};

Object.keys(files).forEach(filepath => {
  const fullPath = path.join('d:/Darukaa_Hackathon/frontend', filepath);
  fs.mkdirSync(path.dirname(fullPath), { recursive: true });
  fs.writeFileSync(fullPath, files[filepath]);
});

// Environment config
fs.writeFileSync('d:/Darukaa_Hackathon/frontend/.env.local', 'NEXT_PUBLIC_API_URL=http://localhost:8000\n');
fs.writeFileSync('d:/Darukaa_Hackathon/frontend/next.config.ts', `import type { NextConfig } from 'next';
const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api-backend/:path*',
        destination: 'http://localhost:8000/:path*',
      },
    ];
  },
};
export default nextConfig;`);
