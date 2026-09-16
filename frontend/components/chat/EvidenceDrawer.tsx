import React from 'react';
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
}
