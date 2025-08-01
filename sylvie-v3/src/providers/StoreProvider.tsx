'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useSylvieStore } from '@/store/sylvieStore';

interface SylvieStoreProviderProps {
  children: ReactNode;
}

const SylvieStoreContext = createContext<typeof useSylvieStore | null>(null);

export function SylvieStoreProvider({ children }: SylvieStoreProviderProps) {
  return (
    <SylvieStoreContext.Provider value={useSylvieStore}>
      {children}
    </SylvieStoreContext.Provider>
  );
}

export function useSylvieStoreContext() {
  const context = useContext(SylvieStoreContext);
  if (!context) {
    throw new Error('useSylvieStoreContext must be used within SylvieStoreProvider');
  }
  return context;
}
