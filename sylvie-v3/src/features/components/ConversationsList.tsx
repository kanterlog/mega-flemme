import React from 'react';

interface Conversation {
  id: number;
  title: string;
  messages: Array<{ id: number; sender: string; content: string; timestamp: string }>;
}

interface Props {
  conversations: Conversation[];
  currentConvId: number;
  onSelect: (id: number) => void;
  onNew: () => void;
  leftHanded: boolean;
}

const ConversationsList: React.FC<Props> = ({ conversations, currentConvId, onSelect, onNew, leftHanded }) => (
  <div style={{ width: 260, background: '#23242b', borderRight: leftHanded ? 'none' : '1px solid #222', borderLeft: leftHanded ? '1px solid #222' : 'none', padding: 16 }}>
    <div style={{ fontWeight: 'bold', marginBottom: 12, color: '#e3e3e3' }}>Conversations</div>
    <ul style={{ listStyle: 'none', padding: 0 }}>
      {conversations.map(conv => (
        <li key={conv.id}>
          <button
            onClick={() => onSelect(conv.id)}
            style={{
              width: '100%',
              background: conv.id === currentConvId ? '#4285f4' : '#23242b',
              color: conv.id === currentConvId ? '#fff' : '#e3e3e3',
              border: 'none',
              borderRadius: 6,
              padding: '8px 12px',
              marginBottom: 6,
              fontWeight: 'bold',
              cursor: 'pointer',
              boxShadow: conv.id === currentConvId ? '0 0 0 2px #4285f4' : 'none'
            }}
            aria-label={`Sélectionner la conversation ${conv.title}`}
            tabIndex={0}
          >
            {conv.title}
          </button>
        </li>
      ))}
    </ul>
    <button
      onClick={onNew}
      style={{ background: '#34a853', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', fontWeight: 'bold', fontSize: 14, marginTop: 12, width: '100%', boxShadow: '0 0 0 2px #34a85333' }}
      aria-label="Créer une nouvelle conversation"
      tabIndex={0}
    >
      Nouvelle conversation
    </button>
  </div>
);

export default ConversationsList;
