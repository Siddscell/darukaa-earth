import React, { useRef, useEffect, useState } from 'react';
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
}
