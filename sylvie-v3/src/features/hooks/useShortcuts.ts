import useLocalStorage from './useLocalStorage';

export interface Shortcut {
  key: string;
  icon: string | React.ReactNode;
  label: string;
  message: string;
  color?: string;
  usage?: number;
}

const DEFAULT_SHORTCUTS: Shortcut[] = [
  { key: 'email', icon: '📧', label: 'Voir mes emails', message: 'Montre-moi mes emails.' },
  { key: 'agenda', icon: '📅', label: 'Voir mon agenda', message: 'Montre-moi mon agenda.' },
  { key: 'drive', icon: '📁', label: 'Accéder à mes fichiers', message: 'Accède à mes fichiers Drive.' },
  { key: 'profil', icon: '👤', label: 'Profil', message: 'Montre mon profil.' },
];

export function useShortcuts() {
  const [customShortcuts, setCustomShortcuts] = useLocalStorage<Shortcut[]>('sylvie_custom_shortcuts', []);
  const [usage, setUsage] = useLocalStorage<Record<string, number>>('sylvie_shortcut_usage', {});

  const allShortcuts = [...DEFAULT_SHORTCUTS, ...customShortcuts].map(s => ({ ...s, usage: usage[s.key] || 0 }));

  const incrementUsage = (key: string) => {
    setUsage({ ...usage, [key]: (usage[key] || 0) + 1 });
  };

  const addShortcut = (shortcut: Shortcut) => {
    setCustomShortcuts([...customShortcuts, shortcut]);
  };

  const editShortcut = (index: number, shortcut: Shortcut) => {
    setCustomShortcuts(customShortcuts.map((sc, i) => i === index ? shortcut : sc));
  };

  const deleteShortcut = (index: number) => {
    setCustomShortcuts(customShortcuts.filter((_, i) => i !== index));
  };

  return {
    allShortcuts,
    customShortcuts,
    addShortcut,
    editShortcut,
    deleteShortcut,
    incrementUsage,
    setCustomShortcuts,
  };
}
