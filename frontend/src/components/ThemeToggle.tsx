'use client';

import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div
      onClick={toggleTheme}
      className="relative flex items-center bg-slate-200/90 dark:bg-slate-900/90 p-0.5 rounded-full border border-slate-300 dark:border-slate-800 cursor-pointer select-none transition-all shadow-inner group hover:border-slate-400 dark:hover:border-slate-700"
      title={`Current: ${theme.toUpperCase()} mode. Click to switch.`}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && toggleTheme()}
      aria-label="Toggle light and dark mode"
    >
      <div
        className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-bold transition-all duration-200 ${
          theme === 'light'
            ? 'bg-white text-amber-600 shadow-sm'
            : 'text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
        }`}
      >
        <Sun className={`h-3.5 w-3.5 ${theme === 'light' ? 'text-amber-500 fill-amber-500/20' : 'text-slate-400 dark:text-slate-500'}`} />
        <span className="text-[10px] hidden sm:inline tracking-wider font-extrabold uppercase">Light</span>
      </div>

      <div
        className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-bold transition-all duration-200 ${
          theme === 'dark'
            ? 'bg-slate-800 text-blue-400 shadow-sm'
            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
        }`}
      >
        <Moon className={`h-3.5 w-3.5 ${theme === 'dark' ? 'text-blue-400 fill-blue-400/20' : 'text-slate-400'}`} />
        <span className="text-[10px] hidden sm:inline tracking-wider font-extrabold uppercase">Dark</span>
      </div>
    </div>
  );
}
