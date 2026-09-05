'use client';

import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      type="button"
      role="switch"
      aria-checked={isDark}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      title={`Current: ${theme.toUpperCase()} mode. Click to toggle.`}
      className="group relative inline-flex h-7 w-13 shrink-0 cursor-pointer items-center rounded-full p-0.5 transition-colors duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 bg-slate-200/80 dark:bg-white/[0.08] border border-slate-300/70 dark:border-white/10 shadow-inner hover:border-slate-400 dark:hover:border-white/20"
    >
      {/* Background static icons for track */}
      <span className="absolute left-1.5 flex h-4 w-4 items-center justify-center pointer-events-none text-amber-500/60 dark:text-slate-600 transition-opacity">
        <Sun className="h-3 w-3" />
      </span>
      <span className="absolute right-1.5 flex h-4 w-4 items-center justify-center pointer-events-none text-slate-400 dark:text-blue-400/60 transition-opacity">
        <Moon className="h-3 w-3" />
      </span>

      {/* Smooth sliding thumb */}
      <span
        className={`pointer-events-none flex h-6 w-6 items-center justify-center rounded-full shadow-md transition-all duration-300 ease-out transform ${
          isDark
            ? 'translate-x-6 bg-[#0E131F] text-blue-400 border border-blue-500/30 shadow-blue-500/20'
            : 'translate-x-0 bg-white text-amber-500 border border-amber-200/80 shadow-amber-500/10'
        } group-hover:scale-105`}
      >
        {isDark ? (
          <Moon className="h-3.5 w-3.5 fill-blue-400/20 text-blue-400 transition-transform duration-300 -rotate-12" />
        ) : (
          <Sun className="h-3.5 w-3.5 fill-amber-500/20 text-amber-500 transition-transform duration-300 rotate-0" />
        )}
      </span>
    </button>
  );
}

