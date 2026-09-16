import React from 'react';
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
}
