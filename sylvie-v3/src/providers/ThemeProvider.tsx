'use client';

import { createContext, useContext, ReactNode } from 'react';

interface SylvieThemeProviderProps {
  children: ReactNode;
}

const SylvieThemeContext = createContext<{
  isDark: boolean;
  toggleTheme: () => void;
} | null>(null);

export function SylvieThemeProvider({ children }: SylvieThemeProviderProps) {
  const isDark = false; // TODO: Implement theme switching logic
  const toggleTheme = () => {
    // TODO: Implement theme toggle
    console.log('Toggle theme');
  };

  return (
    <SylvieThemeContext.Provider value={{ isDark, toggleTheme }}>
      {children}
    </SylvieThemeContext.Provider>
  );
}

export function useSylvieTheme() {
  const context = useContext(SylvieThemeContext);
  if (!context) {
    throw new Error('useSylvieTheme must be used within SylvieThemeProvider');
  }
  return context;
}
