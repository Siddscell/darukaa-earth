import React from 'react';

export default function UserMessage({ content }: { content: string }) {
  return (
    <div className="flex justify-end mb-4">
      <div className="bg-earth-accent/20 border border-earth-accent/30 text-gray-100 px-4 py-3 rounded-2xl rounded-tr-sm max-w-[85%] text-sm leading-relaxed">
        {content}
      </div>
    </div>
  );
}
