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
}
