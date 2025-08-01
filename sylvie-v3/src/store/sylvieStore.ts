'use client';

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';
import type { 
  SylvieState, 
  SylvieActions, 
  SylvieMessage, 
  ConversationBranch,
  User,
  SylvieConfig,
  WorkspaceAction,
  MCPServerConfig 
} from '@/types';

const defaultConfig: SylvieConfig = {
  theme: 'light',
  language: 'fr',
  workspace: {
    services: {
      gmail: true,
      calendar: true,
      drive: true,
      docs: true,
      sheets: true,
      slides: true,
      tasks: true,
    },
    scopes: [
      'https://www.googleapis.com/auth/gmail.modify',
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/documents',
      'https://www.googleapis.com/auth/spreadsheets',
      'https://www.googleapis.com/auth/presentations',
      'https://www.googleapis.com/auth/tasks',
    ],
    cacheEnabled: true,
    cacheTtl: 1800, // 30 minutes
  },
  mcpServers: [],
  ai: {
    provider: 'openai',
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 2048,
  },
};

export const useSylvieStore = create<SylvieState & SylvieActions>()(
  devtools(
    persist(
      (set, get) => ({
        // État initial
        user: null,
        isAuthenticated: false,
        conversations: [],
        activeConversationId: null,
        messages: [],
        isThinking: false,
        config: defaultConfig,
        sidebarOpen: true,
        branchModalOpen: false,
        settingsModalOpen: false,
        mcpServers: [],
        availableActions: [],

        // Actions d'authentification
        setUser: (user: User | null) => {
          set({ 
            user, 
            isAuthenticated: !!user 
          }, false, 'setUser');
        },

        logout: () => {
          set({ 
            user: null, 
            isAuthenticated: false,
            conversations: [],
            activeConversationId: null,
            messages: [],
          }, false, 'logout');
        },

        // Actions de conversation
        createConversation: (title?: string) => {
          const id = uuidv4();
          const newConversation: ConversationBranch = {
            id,
            title: title || `Conversation ${new Date().toLocaleDateString('fr-FR')}`,
            messages: [],
            createdAt: new Date(),
            updatedAt: new Date(),
          };

          set((state) => ({
            conversations: [...state.conversations, newConversation],
            activeConversationId: id,
            messages: [],
          }), false, 'createConversation');

          return id;
        },

        deleteConversation: (id: string) => {
          set((state) => ({
            conversations: state.conversations.filter(c => c.id !== id),
            activeConversationId: state.activeConversationId === id ? null : state.activeConversationId,
            messages: state.activeConversationId === id ? [] : state.messages,
          }), false, 'deleteConversation');
        },

        setActiveConversation: (id: string) => {
          const conversation = get().conversations.find(c => c.id === id);
          if (conversation) {
            set({
              activeConversationId: id,
              messages: conversation.messages,
            }, false, 'setActiveConversation');
          }
        },

        // Actions de message
        addMessage: (messageData) => {
          const message: SylvieMessage = {
            ...messageData,
            id: uuidv4(),
            timestamp: new Date(),
          };

          set((state) => {
            const newMessages = [...state.messages, message];
            
            // Mettre à jour la conversation active
            const updatedConversations = state.conversations.map(conv => 
              conv.id === state.activeConversationId 
                ? { ...conv, messages: newMessages, updatedAt: new Date() }
                : conv
            );

            return {
              messages: newMessages,
              conversations: updatedConversations,
            };
          }, false, 'addMessage');
        },

        updateMessage: (id: string, updates: Partial<SylvieMessage>) => {
          set((state) => {
            const newMessages = state.messages.map(msg => 
              msg.id === id ? { ...msg, ...updates } : msg
            );

            const updatedConversations = state.conversations.map(conv => 
              conv.id === state.activeConversationId 
                ? { ...conv, messages: newMessages, updatedAt: new Date() }
                : conv
            );

            return {
              messages: newMessages,
              conversations: updatedConversations,
            };
          }, false, 'updateMessage');
        },

        setThinking: (thinking: boolean) => {
          set({ isThinking: thinking }, false, 'setThinking');
        },

        // Actions de branche
        createBranch: (messageId: string, newMessage: string) => {
          const branchId = uuidv4();
          const messageIndex = get().messages.findIndex(m => m.id === messageId);
          
          if (messageIndex !== -1) {
            const branchMessages = get().messages.slice(0, messageIndex + 1);
            branchMessages.push({
              id: uuidv4(),
              type: 'user',
              content: newMessage,
              timestamp: new Date(),
              metadata: { branchId, parentId: messageId },
            });

            const newBranch: ConversationBranch = {
              id: branchId,
              parentId: get().activeConversationId || undefined,
              title: `Branche ${new Date().toLocaleTimeString('fr-FR')}`,
              messages: branchMessages,
              createdAt: new Date(),
              updatedAt: new Date(),
            };

            set((state) => ({
              conversations: [...state.conversations, newBranch],
              activeConversationId: branchId,
              messages: branchMessages,
            }), false, 'createBranch');
          }

          return branchId;
        },

        switchToBranch: (branchId: string) => {
          get().setActiveConversation(branchId);
        },

        // Actions UI
        toggleSidebar: () => {
          set((state) => ({ sidebarOpen: !state.sidebarOpen }), false, 'toggleSidebar');
        },

        openBranchModal: () => {
          set({ branchModalOpen: true }, false, 'openBranchModal');
        },

        closeBranchModal: () => {
          set({ branchModalOpen: false }, false, 'closeBranchModal');
        },

        openSettingsModal: () => {
          set({ settingsModalOpen: true }, false, 'openSettingsModal');
        },

        closeSettingsModal: () => {
          set({ settingsModalOpen: false }, false, 'closeSettingsModal');
        },

        // Actions de configuration
        updateConfig: (configUpdates: Partial<SylvieConfig>) => {
          set((state) => ({
            config: { ...state.config, ...configUpdates }
          }), false, 'updateConfig');
        },

        // Actions MCP
        connectMCPServer: async (serverConfig: MCPServerConfig) => {
          try {
            // TODO: Implémenter la connexion MCP réelle
            set((state) => ({
              mcpServers: [...state.mcpServers, { ...serverConfig, status: 'connected' }]
            }), false, 'connectMCPServer');
          } catch (error) {
            console.error('Erreur connexion MCP:', error);
            set((state) => ({
              mcpServers: [...state.mcpServers, { ...serverConfig, status: 'error' }]
            }), false, 'connectMCPServer');
          }
        },

        disconnectMCPServer: (name: string) => {
          set((state) => ({
            mcpServers: state.mcpServers.filter(server => server.name !== name)
          }), false, 'disconnectMCPServer');
        },

        executeAction: async (action: WorkspaceAction) => {
          try {
            // TODO: Implémenter l'exécution d'actions réelles
            console.log('Exécution action:', action);
          } catch (error) {
            console.error('Erreur exécution action:', error);
          }
        },
      }),
      {
        name: 'sylvie-store',
        partialize: (state) => ({
          user: state.user,
          conversations: state.conversations,
          config: state.config,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    ),
    {
      name: 'sylvie-store',
    }
  )
);
