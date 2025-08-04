import React from 'react';
import { PlusOutlined } from '@ant-design/icons';

interface Shortcut {
  key: string;
  icon: React.ReactNode;
  label: string;
  message: string;
  color?: string;
  usage?: number;
}

interface Props {
  shortcuts: Shortcut[];
  compact: boolean;
  onShortcutClick: (shortcut: Shortcut) => void;
  onAddClick: () => void;
}

const ShortcutBubble = ({ icon, label, onClick, tooltip }: { icon: React.ReactNode; label: string; onClick: () => void; tooltip?: string }) => (
  <div style={{ position: 'relative', display: 'inline-block' }}>
    <button
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        background: '#181a20',
        color: '#e3e3e3',
        border: '1px solid #444',
        borderRadius: 24,
        padding: '8px 18px',
        fontWeight: 'bold',
        fontSize: 15,
        cursor: 'pointer',
        boxShadow: '0 2px 8px #0002',
        transition: 'background 0.2s, transform 0.3s',
      }}
    >
      {icon}
      {label}
    </button>
    {tooltip && (
      <div style={{
        position: 'absolute',
        top: '-38px',
        left: '50%',
        transform: 'translateX(-50%)',
        background: '#23242b',
        color: '#e3e3e3',
        padding: '6px 14px',
        borderRadius: 8,
        fontSize: 13,
        boxShadow: '0 2px 8px #0002',
        whiteSpace: 'nowrap',
        zIndex: 10,
        opacity: 1,
      }}>{tooltip}</div>
    )}
  </div>
);

const ShortcutManager: React.FC<Props> = ({ shortcuts, compact, onShortcutClick, onAddClick }) => (
  <div
    style={{
      display: 'flex',
      gap: compact ? 8 : 16,
      padding: compact ? '10px 8px' : '16px 24px',
      background: '#23242b',
      borderBottom: '1px solid #222',
      flexWrap: compact ? 'nowrap' : 'wrap',
      overflowX: compact ? 'auto' : 'visible',
      scrollbarWidth: compact ? 'thin' : 'none',
      WebkitOverflowScrolling: 'touch',
    }}
  >
    {shortcuts.map(s => (
      <ShortcutBubble
        key={s.key || s.label}
        icon={typeof s.icon === 'string' ? <span>{s.icon}</span> : s.icon}
        label={compact ? '' : s.label}
        tooltip={s.label + (s.message ? ` : ${s.message}` : '')}
        onClick={() => onShortcutClick(s)}
      />
    ))}
    <ShortcutBubble icon={<PlusOutlined />} label={compact ? '' : 'Ajouter un raccourci'} tooltip="Ajouter un raccourci personnalisé" onClick={onAddClick} />
  </div>
);

export default ShortcutManager;
