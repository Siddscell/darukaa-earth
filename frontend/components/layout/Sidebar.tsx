import React, { useState } from 'react';
import { Leaf, LayoutDashboard, Microscope, Map, BookOpen, History, Menu } from 'lucide-react';
import clsx from 'clsx';
import { useSystemStatus } from '@/hooks/useSystemStatus';

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { status } = useSystemStatus();

  const isHealthy = status?.database && status?.vector_db && status?.ollama_available;

  const navItems = [
    { icon: LayoutDashboard, label: 'Overview' },
    { icon: Microscope, label: 'AI Scientist', active: true },
    { icon: Map, label: 'Environmental Profile' },
    { icon: BookOpen, label: 'Evidence Library' },
    { icon: History, label: 'History' },
  ];

  return (
    <div className={clsx(
      "flex flex-col bg-earth-panel border-r border-earth-border transition-all duration-300",
      collapsed ? "w-[60px]" : "w-[240px]"
    )}>
      <div className="flex items-center p-4 h-16 border-b border-earth-border justify-between">
        <div className={clsx("flex items-center gap-2 overflow-hidden", collapsed && "hidden")}>
          <Leaf className="w-6 h-6 text-earth-accent shrink-0" />
          <span className="font-semibold text-earth-text whitespace-nowrap">Darukaa.Earth</span>
        </div>
        <button onClick={() => setCollapsed(!collapsed)} className="text-gray-400 hover:text-white p-1">
          {collapsed ? <Leaf className="w-6 h-6 text-earth-accent" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      <nav className="flex-1 py-4 flex flex-col gap-2 px-2 overflow-y-auto overflow-x-hidden">
        {navItems.map((item, i) => (
          <button
            key={i}
            className={clsx(
              "flex items-center gap-3 px-3 py-2 rounded-md transition-colors w-full text-left",
              item.active ? "bg-earth-card text-earth-accent" : "text-gray-400 hover:bg-earth-card/50 hover:text-gray-200"
            )}
            title={item.label}
          >
            <item.icon className="w-5 h-5 shrink-0" />
            {!collapsed && <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>}
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-earth-border">
        <div className="flex items-center justify-center lg:justify-start gap-2" title={isHealthy ? 'System Healthy' : 'System degraded'}>
          <div className={clsx("w-2.5 h-2.5 rounded-full shrink-0", isHealthy ? "bg-green-500" : "bg-red-500")} />
          {!collapsed && <span className="text-xs text-gray-400">System Status</span>}
        </div>
      </div>
    </div>
  );
}
