import React, { useMemo } from 'react';

interface Message {
  id: number;
  sender: string;
  content: string;
  timestamp: string;
}

interface Props {
  msg: Message;
}

const MessageBubble: React.FC<Props> = ({ msg }) => {
  const bubbleStyle = useMemo(() => ({
    marginBottom: 12,
    display: 'flex',
    flexDirection: (msg.sender === 'Utilisateur' ? 'row-reverse' : 'row') as 'row' | 'row-reverse',
    alignItems: 'flex-end',
    gap: 10,
  }), [msg.sender]);

  const contentStyle = useMemo(() => ({
    background: msg.sender === 'Utilisateur' ? '#4285f4' : '#23242b',
    color: msg.sender === 'Utilisateur' ? '#fff' : '#e3e3e3',
    borderRadius: 16,
    padding: '10px 18px',
    fontWeight: 'bold',
    fontSize: 15,
    boxShadow: '0 2px 8px #0002',
    maxWidth: '70%',
    wordBreak: 'break-word' as 'break-word',
    transition: 'background 0.2s',
  }), [msg.sender]);

  return (
    <div className="message-appear" style={bubbleStyle}>
      <div style={contentStyle}>
        {msg.content}
      </div>
      <span style={{ fontSize: 12, color: '#888', minWidth: 48, textAlign: 'center' }}>{msg.timestamp}</span>
    </div>
  );
};

export default MessageBubble;
