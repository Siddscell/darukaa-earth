import React from 'react';
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
}
