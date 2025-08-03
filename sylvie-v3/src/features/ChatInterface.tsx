

import React, { useState, useEffect } from 'react';
// ...existing code...
import { useSylvieStore } from '../store/sylvieStore';

interface Conversation {
  id: number;
  title: string;
  messages: Array<{ id: number; sender: string; content: string; timestamp: string }>;
}

// Messages mock initiaux
const initialMessages = [
  { id: 1, sender: 'Sylvie', content: 'Bonjour, comment puis-je vous aider ?', timestamp: '10:00' },
  { id: 2, sender: 'Utilisateur', content: 'Montre-moi mes emails.', timestamp: '10:01' },
];

const ChatInterface: React.FC = () => {
  const [message, setMessage] = useState('');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConvId, setCurrentConvId] = useState(1);
  const [loading, setLoading] = useState(true);

  const currentConv = conversations.find(c => c.id === currentConvId);

  // Chargement initial des conversations depuis l'API
  useEffect(() => {
    const fetchConversations = async () => {
      setLoading(true);
      try {
        const res = await fetch('/api/conversations');
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setConversations(data);
          setCurrentConvId(data[0].id);
        } else {
          // Si aucune conversation, on initialise avec la principale
          const conv = {
            id: 1,
            title: 'Conversation principale',
            messages: [...initialMessages]
          };
          await fetch('/api/conversations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(conv)
          });
          setConversations([conv]);
          setCurrentConvId(1);
        }
      } catch (e) {
        // fallback localStorage si backend KO
        const saved = typeof window !== 'undefined' ? localStorage.getItem('sylvie_conversations') : null;
        if (saved) {
          try {
            const local = JSON.parse(saved);
            setConversations(local);
            setCurrentConvId(local[0]?.id || 1);
          } catch {}
        }
      }
      setLoading(false);
    };
    fetchConversations();
  }, []);

  // Sauvegarde à chaque modification
  useEffect(() => {
    if (!loading) {
      fetch('/api/conversations', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(conversations)
      });
      if (typeof window !== 'undefined') {
        localStorage.setItem('sylvie_conversations', JSON.stringify(conversations));
        localStorage.setItem('sylvie_currentConvId', String(currentConvId));
      }
    }
  }, [conversations, currentConvId, loading]);

  const handleSend = () => {
    if (!message.trim() || !currentConv) return;
    const newMsg = {
      id: currentConv.messages.length + 1,
      sender: 'Utilisateur',
      content: message,
      timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
    };
    setConversations(convs => convs.map(c =>
      c.id === currentConvId
        ? { ...c, messages: [...c.messages, newMsg] }
        : c
    ));
    setMessage('');
  };

  const handleNewConversation = () => {
    const newId = conversations.length + 1;
    setConversations([...conversations, {
      id: newId,
      title: `Conversation ${newId}`,
      messages: []
    }]);
    setCurrentConvId(newId);
  };

  const handleSelectConversation = (id: number) => {
    setCurrentConvId(id);
  };

  const handleResetConversation = () => {
    setConversations(convs => convs.map(c =>
      c.id === currentConvId
        ? { ...c, messages: [] }
        : c
    ));
  };

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f8f9fa' }}>
      <div style={{ width: 260, background: '#fff', borderRight: '1px solid #eee', padding: 16 }}>
        <div style={{ fontWeight: 'bold', marginBottom: 12 }}>Conversations</div>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {conversations.map(conv => (
            <li key={conv.id}>
              <button
                onClick={() => handleSelectConversation(conv.id)}
                style={{
                  width: '100%',
                  background: conv.id === currentConvId ? '#4285f4' : '#f0f2f5',
                  color: conv.id === currentConvId ? '#fff' : '#202124',
                  border: 'none',
                  borderRadius: 6,
                  padding: '8px 12px',
                  marginBottom: 6,
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                {conv.title}
              </button>
            </li>
          ))}
        </ul>
        <button
          onClick={handleNewConversation}
          style={{ background: '#34a853', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', fontWeight: 'bold', fontSize: 14, marginTop: 12, width: '100%' }}
        >
          Nouvelle conversation
        </button>
      </div>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
          {currentConv && currentConv.messages.length === 0 && (
            <div style={{ color: '#888', textAlign: 'center', marginTop: 40 }}>
              Aucun message dans cette conversation.
            </div>
          )}
          {currentConv && currentConv.messages.map(msg => (
            <div key={msg.id} style={{ marginBottom: 16, textAlign: msg.sender === 'Utilisateur' ? 'right' : 'left' }}>
              <div style={{ display: 'inline-block', background: msg.sender === 'Utilisateur' ? '#4285f4' : '#fff', color: msg.sender === 'Utilisateur' ? '#fff' : '#202124', borderRadius: 8, padding: '8px 16px', maxWidth: '70%' }}>
                <strong>{msg.sender}</strong> <span style={{ fontSize: 12, color: '#888' }}>{msg.timestamp}</span>
                <div>{msg.content}</div>
              </div>
            </div>
          ))}
        </div>
        <div style={{ padding: 16, background: '#fff', borderTop: '1px solid #eee', display: 'flex', gap: 8 }}>
          <input
            type="text"
            value={message}
            onChange={e => setMessage(e.target.value)}
            placeholder="Écrivez votre message..."
            style={{ flex: 1, padding: 8, borderRadius: 8, border: '1px solid #ccc', fontSize: 16 }}
            onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
          />
          <button
            onClick={handleSend}
            style={{ background: '#4285f4', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 24px', fontWeight: 'bold', fontSize: 16 }}
          >
            Envoyer
          </button>
          <button
            onClick={handleResetConversation}
            style={{ background: '#ea4335', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', fontWeight: 'bold', fontSize: 14, marginLeft: 8 }}
          >
            Réinitialiser
          </button>
        </div>
      </div>
    </div>
  );
};
