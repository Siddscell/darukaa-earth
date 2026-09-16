import { useState } from 'react';
import { api } from '@/lib/api';
import type { ChatMessage, EnvironmentalProfile, DemoScenario } from '@/types';
import { v4 as uuidv4 } from 'uuid'; // need to install uuid or just generate random string

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [environmentalProfile, setEnvironmentalProfile] = useState<EnvironmentalProfile | null>(null);

  const sendMessage = async (text: string) => {
    setIsLoading(true);
    setError(null);
    
    const userMsg: ChatMessage = {
      id: Math.random().toString(36).substring(7),
      role: 'user',
      content: text,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMsg]);
    
    try {
      const response = await api.sendMessage(text, conversationId || undefined);
      
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      
      if (response.environmental_profile) {
        setEnvironmentalProfile(response.environmental_profile);
      }
      
      const assistantMsg: ChatMessage = {
        id: Math.random().toString(36).substring(7),
        role: 'assistant',
        content: response.message,
        recommendations: response.recommendations,
        reasoning_trace: response.reasoning_trace,
        needs_clarification: response.needs_clarification,
        clarification_questions: response.clarification_questions,
        demo_mode: response.demo_mode,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || 'An error occurred while sending message');
    } finally {
      setIsLoading(false);
    }
  };

  const loadScenario = async (scenario: DemoScenario) => {
    setIsLoading(true);
    try {
      // Mock conversation ID for scenario
      const newConvId = Math.random().toString(36).substring(7);
      setConversationId(newConvId);
      setEnvironmentalProfile(scenario.profile);
      
      await api.setEnvironmentalProfile(scenario.profile, newConvId);
      await sendMessage(scenario.initial_message);
    } catch (err: any) {
      setError('Failed to load scenario: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setConversationId('');
    setEnvironmentalProfile(null);
    setError(null);
  };

  return {
    messages,
    conversationId,
    isLoading,
    error,
    environmentalProfile,
    sendMessage,
    loadScenario,
    clearConversation
  };
}
