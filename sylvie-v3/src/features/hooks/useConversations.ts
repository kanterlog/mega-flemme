import { useState } from 'react';

export interface Message {
  id: number;
  sender: string;
  content: string;
  timestamp: string;
}

export interface Conversation {
  id: number;
  title: string;
  messages: Message[];
}

const initialMessages: Message[] = [
  { id: 1, sender: 'Sylvie', content: 'Bonjour, comment puis-je vous aider ?', timestamp: '10:00' },
  { id: 2, sender: 'Utilisateur', content: 'Montre-moi mes emails.', timestamp: '10:01' },
];

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: 1, title: 'Général', messages: [...initialMessages] },
  ]);
  const [currentConvId, setCurrentConvId] = useState(1);

  const currentConv = conversations.find(c => c.id === currentConvId);

  const addMessage = (msg: Message) => {
    setConversations(convs => convs.map(c =>
      c.id === currentConvId ? { ...c, messages: [...c.messages, msg] } : c
    ));
  };

  const selectConversation = (id: number) => setCurrentConvId(id);

  const newConversation = () => {
    const newId = Math.max(...conversations.map(c => c.id)) + 1;
    setConversations([...conversations, { id: newId, title: `Conversation ${newId}`, messages: [] }]);
    setCurrentConvId(newId);
  };

  const resetConversation = () => {
    setConversations(convs => convs.map(c =>
      c.id === currentConvId ? { ...c, messages: [] } : c
    ));
  };

  return {
    conversations,
    currentConvId,
    currentConv,
    addMessage,
    selectConversation,
    newConversation,
    resetConversation,
  };
}
