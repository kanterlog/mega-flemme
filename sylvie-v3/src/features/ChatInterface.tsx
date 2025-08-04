import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
// Améliorations mineures : extraction des styles, centralisation des constantes, logs conditionnels
import ShortcutModal from './components/ShortcutModal';
import { MailOutlined, CalendarOutlined, FileOutlined, UserOutlined, PlusOutlined } from '@ant-design/icons';
import { useSylvieStore } from '../store/sylvieStore';
import ConversationsList from './components/ConversationsList';
import MessageBubble from './components/MessageBubble';
import ShortcutManager from './components/ShortcutManager';
import { useConversations, Message as ConversationMessage } from './hooks/useConversations';
import { THEME } from '../constants/theme';
import { useShortcuts } from './hooks/useShortcuts';
import useLocalStorage from './hooks/useLocalStorage';

// Constantes de validation centralisées
const MESSAGE_MAX_LENGTH = 1000;
const MESSAGE_MIN_LENGTH = 1;

// Styles extraits
const suggestionButtonStyle = {
  background: THEME.colors.card,
  color: THEME.colors.text,
  border: `1px solid ${THEME.colors.border}`,
  borderRadius: 16,
  padding: '6px 16px',
  fontSize: 14,
  cursor: 'pointer',
  boxShadow: '0 2px 8px #0002',
  marginBottom: 4,
};
const sendButtonStyle = {
  background: THEME.colors.primary,
  color: '#fff',
  border: 'none',
  borderRadius: 8,
  padding: '8px 18px',
  fontWeight: 'bold',
  fontSize: 15,
  boxShadow: `0 0 0 2px ${THEME.colors.primary}`,
};
const resetButtonStyle = {
  background: THEME.colors.error,
  color: '#fff',
  border: 'none',
  borderRadius: 8,
  padding: '8px 16px',
  fontWeight: 'bold',
  fontSize: 14,
  marginLeft: 8,
  boxShadow: `0 0 0 2px ${THEME.colors.error}`,
};


// ...existing code...


/**
 * Composant principal d'interface de chat Sylvie v3.
 * Gère l'affichage des conversations, messages, raccourcis, préférences UI et notifications.
 * Optimisé pour la performance et la maintenabilité.
 */

const ChatInterface: React.FC = () => {
  /**
   * Message en cours d'édition par l'utilisateur.
   */
  // Hooks personnalisés
  const [message, setMessage] = useState('');
  const defaultSuggestions = useMemo(() => [
    'Merci', 'Peux-tu détailler ?', 'C’est urgent', 'Donne-moi un exemple'
  ], []);
  const [suggestions, setSuggestions] = useState<string[]>(defaultSuggestions);
  const [tone, setTone] = useState<'Neutre' | 'Amical' | 'Professionnel' | 'Enthousiaste'>('Neutre');
  const [toast, setToast] = useState<{ message: string; type?: 'error' | 'success'; action?: { label: string; onClick: () => void } } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Conversations
  const {
    conversations,
    currentConvId,
    currentConv,
    addMessage,
    selectConversation,
    newConversation,
    resetConversation,
  } = useConversations();

  // Raccourcis
  const {
    allShortcuts,
    customShortcuts,
    setCustomShortcuts,
    incrementUsage,
  } = useShortcuts();

  // États locaux pour le modal et le formulaire de raccourci
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [formShortcut, setFormShortcut] = useState({ label: '', message: '', icon: '', color: '#4285f4' });
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [confirmDeleteIdx, setConfirmDeleteIdx] = useState<number | null>(null);
  const [dragIdx, setDragIdx] = useState<number | null>(null);

  // Préférences UI
  const [leftHanded, setLeftHanded] = useLocalStorage('sylvie_left_handed', false);
  const [compact, setCompact] = useLocalStorage('sylvie_compact_mode', false);

  // currentConv déjà fourni par le hook

  // Scroll auto vers le bas
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentConv?.messages]);

  // Nettoyage automatique du toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), THEME.durations.toast);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  /**
   * Valide le contenu d'un message utilisateur.
   * @param msg Message à valider
   * @returns true si le message est valide
   */
  /**
   * Valide le contenu d'un message utilisateur.
   * @param msg Message à valider
   * @returns true si le message est valide
   */
  const validateMessage = useCallback((msg: string) => {
    return msg.trim().length >= MESSAGE_MIN_LENGTH && msg.length <= MESSAGE_MAX_LENGTH;
  }, []);

  /**
   * Envoie le message utilisateur dans la conversation courante.
   * Affiche un toast en cas d'erreur ou de validation échouée.
   */
  const handleSend = useCallback(() => {
    if (!validateMessage(message)) {
      setToast({ message: 'Message invalide', type: 'error' });
      return;
    }
    try {
      addMessage({
        id: Date.now(),
        sender: 'Utilisateur',
        content: message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      });
      setMessage('');
      setSuggestions(defaultSuggestions);
      // Log conditionnel en dev
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.log('[ChatInterface] Message envoyé:', message);
      }
    } catch (error: any) {
      let errorMsg = "Erreur d'envoi";
      if (error?.message) errorMsg += ` : ${error.message}`;
      setToast({ message: errorMsg, type: 'error' });
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Erreur lors de l’envoi du message :', error);
      }
    }
  }, [message, addMessage, defaultSuggestions, validateMessage]);

  /**
   * Sélectionne une conversation par son identifiant.
   * @param id Identifiant de la conversation
   */
  const handleSelectConversation = useCallback((id: number) => {
    selectConversation(id);
  }, [selectConversation]);

  /**
   * Crée une nouvelle conversation.
   */
  const handleNewConversation = useCallback(() => {
    newConversation();
  }, [newConversation]);

  /**
   * Réinitialise la conversation courante et le champ de saisie.
   */
  const handleResetConversation = useCallback(() => {
    resetConversation();
    setMessage('');
  }, [resetConversation]);

  const containerStyle = useMemo(() => ({
    display: 'flex',
    height: '100vh',
    background: THEME.colors.background,
    color: THEME.colors.text,
    flexDirection: (leftHanded ? 'row-reverse' : 'row') as React.CSSProperties['flexDirection'],
  }), [leftHanded]);

  return (
    <div style={containerStyle}>
      {/* Sidebar conversations */}
      {/* React.memo pour ConversationsList */}
      {React.useMemo(() => (
        <ConversationsList
          conversations={conversations}
          currentConvId={currentConvId}
          onSelect={handleSelectConversation}
          onNew={handleNewConversation}
          leftHanded={leftHanded}
        />
      ), [conversations, currentConvId, handleSelectConversation, handleNewConversation, leftHanded])}
      {/* Main chat area */}
      <div style={useMemo(() => ({ flex: 1, display: 'flex', flexDirection: 'column', background: THEME.colors.background }), [])}>
        {/* Shortcut bubbles */}
        {/* React.memo pour ShortcutManager */}
        {React.useMemo(() => (
          <ShortcutManager
            shortcuts={allShortcuts}
            compact={compact}
            onShortcutClick={useCallback((s) => {
              setMessage(s.message);
              if (s.key) incrementUsage(s.key);
              setToast({ message: `Raccourci « ${s.label} » utilisé` });
            }, [incrementUsage])}
            onAddClick={useCallback(() => setEditModalOpen(true), [])}
          />
        ), [allShortcuts, compact, incrementUsage])}
        {/* Modal édition/suppression raccourci */}
        <ShortcutModal
          open={editModalOpen}
          shortcuts={customShortcuts}
          setShortcuts={setCustomShortcuts}
          formShortcut={formShortcut}
          setFormShortcut={setFormShortcut}
          editIndex={editIndex}
          setEditIndex={setEditIndex}
          confirmDeleteIdx={confirmDeleteIdx}
          setConfirmDeleteIdx={setConfirmDeleteIdx}
          dragIdx={dragIdx}
          setDragIdx={setDragIdx}
          setToast={setToast}
          onClose={() => setEditModalOpen(false)}
        />
        {/* Bloc messages avec animation et auto-scroll */}
        <div style={useMemo(() => ({ flex: 1, overflowY: 'auto', padding: compact ? '8px 4px' : '18px 32px', background: THEME.colors.background, borderBottom: `1px solid ${THEME.colors.card}` }), [compact])}>
          {/* React.memo pour MessageBubble list */}
          {React.useMemo(() => currentConv?.messages.map((msg: ConversationMessage) => (
            <MessageBubble key={msg.id} msg={msg} />
          )), [currentConv?.messages])}
          <div ref={messagesEndRef} />
        </div>
        {/* Suggestions et sélecteur de ton regroupés */}
        <div>
          <div style={useMemo(() => ({ display: 'flex', gap: 10, margin: '12px 0 0 0', flexWrap: 'wrap' }), [])}>
            {useMemo(() => suggestions.map((sugg: string, idx: number) => (
              <button
                key={sugg + idx}
                onClick={() => setMessage(sugg)}
                style={suggestionButtonStyle}
                aria-label={`Suggestion : ${sugg}`}
              >{sugg}</button>
            )), [suggestions])}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '10px 0' }}>
            <label htmlFor="toneSelect" style={{ fontSize: 14, color: THEME.colors.text, fontWeight: 'bold' }}>Ton :</label>
            <select
              id="toneSelect"
              value={tone}
              onChange={e => setTone(e.target.value as typeof tone)}
              style={{ background: THEME.colors.card, color: THEME.colors.text, border: `1px solid ${THEME.colors.border}`, borderRadius: THEME.layout.borderRadius, padding: '6px 14px', fontSize: 15 }}
            >
              <option value="Neutre">Neutre</option>
              <option value="Amical">Amical</option>
              <option value="Professionnel">Professionnel</option>
              <option value="Enthousiaste">Enthousiaste</option>
            </select>
          </div>
        </div>
        <div style={useMemo(() => ({ display: 'flex', gap: 12, marginTop: 8 }), [])}>
          <button
            onClick={handleSend}
            style={sendButtonStyle}
          >
            Envoyer
          </button>
          <button
            onClick={handleResetConversation}
            style={resetButtonStyle}
          >
            Réinitialiser
          </button>
        </div>
        {/* Toast notification */}
        <div
          role="alert"
          aria-live="assertive"
          style={useMemo(() => ({
            pointerEvents: 'none',
            position: 'fixed',
            bottom: 24,
            left: '50%',
            minWidth: 180,
            maxWidth: 420,
            background: toast?.type === 'error' ? THEME.colors.error : THEME.colors.success,
            color: '#fff',
            padding: toast?.action ? '12px 24px 12px 18px' : '12px 24px',
            borderRadius: 8,
            fontWeight: 'bold',
            fontSize: 15,
            boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
            zIndex: 2000,
            opacity: toast ? 1 : 0,
            transition: toast ? 'opacity 0.3s, transform 0.4s' : 'opacity 0.3s',
            display: toast ? 'flex' : 'none',
            alignItems: 'center',
            gap: 16,
            cursor: toast?.action ? 'pointer' : 'default',
            userSelect: 'none',
            transform: toast ? 'translateX(-50%) translateY(0)' : 'translateX(-50%) translateY(40px)',
          }), [toast])}
          tabIndex={toast ? 0 : -1}
        >
          {toast && (
            <React.Fragment>
              <span style={{ flex: 1 }}>{toast.message}</span>
              {toast.action && (
                <button
                  style={{
                    pointerEvents: 'auto',
                    background: 'rgba(255,255,255,0.12)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 6,
                    padding: '4px 14px',
                    fontWeight: 'bold',
                    fontSize: 14,
                    marginLeft: 8,
                    cursor: 'pointer',
                    transition: 'background 0.2s',
                  }}
                  onClick={e => {
                    e.stopPropagation();
                    toast?.action?.onClick && toast.action.onClick();
                  }}
                >{toast.action.label}</button>
              )}
            </React.Fragment>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

