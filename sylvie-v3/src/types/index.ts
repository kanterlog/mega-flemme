// Types globaux pour l'application Sylvie
export interface SylvieMessage {
  id: string;
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    thinking?: boolean;
    branchId?: string;
    parentId?: string;
    sources?: string[];
    actions?: WorkspaceAction[];
  };
}

export interface WorkspaceAction {
  type: 'email' | 'calendar' | 'drive' | 'docs' | 'sheets' | 'tasks';
  action: string;
  description: string;
  status: 'pending' | 'success' | 'error';
  result?: any;
}

export interface ConversationBranch {
  id: string;
  parentId?: string;
  title: string;
  messages: SylvieMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface GoogleWorkspaceConfig {
  services: {
    gmail: boolean;
    calendar: boolean;
    drive: boolean;
    docs: boolean;
    sheets: boolean;
    slides: boolean;
    tasks: boolean;
  };
  scopes: string[];
  cacheEnabled: boolean;
  cacheTtl: number;
}

export interface MCPServerConfig {
  name: string;
  endpoint: string;
  version: string;
  capabilities: string[];
  status: 'connected' | 'disconnected' | 'error';
}

export interface SylvieConfig {
  theme: 'light' | 'dark' | 'auto';
  language: 'fr' | 'en';
  workspace: GoogleWorkspaceConfig;
  mcpServers: MCPServerConfig[];
  ai: {
    provider: string;
    model: string;
    temperature: number;
    maxTokens: number;
  };
}

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: Date;
}

export interface SylvieState {
  // User & Auth
  user: User | null;
  isAuthenticated: boolean;
  
  // Conversations
  conversations: ConversationBranch[];
  activeConversationId: string | null;
  
  // Messages
  messages: SylvieMessage[];
  isThinking: boolean;
  
  // Configuration
  config: SylvieConfig;
  
  // UI State
  sidebarOpen: boolean;
  branchModalOpen: boolean;
  settingsModalOpen: boolean;
  
  // MCP
  mcpServers: MCPServerConfig[];
  availableActions: WorkspaceAction[];
}

// Actions types pour Zustand
export interface SylvieActions {
  // Auth actions
  setUser: (user: User | null) => void;
  logout: () => void;
  
  // Conversation actions
  createConversation: (title?: string) => string;
  deleteConversation: (id: string) => void;
  setActiveConversation: (id: string) => void;
  
  // Message actions
  addMessage: (message: Omit<SylvieMessage, 'id' | 'timestamp'>) => void;
  updateMessage: (id: string, updates: Partial<SylvieMessage>) => void;
  setThinking: (thinking: boolean) => void;
  
  // Branch actions
  createBranch: (messageId: string, newMessage: string) => string;
  switchToBranch: (branchId: string) => void;
  
  // UI actions
  toggleSidebar: () => void;
  openBranchModal: () => void;
  closeBranchModal: () => void;
  openSettingsModal: () => void;
  closeSettingsModal: () => void;
  
  // Config actions
  updateConfig: (config: Partial<SylvieConfig>) => void;
  
  // MCP actions
  connectMCPServer: (config: MCPServerConfig) => Promise<void>;
  disconnectMCPServer: (name: string) => void;
  executeAction: (action: WorkspaceAction) => Promise<void>;
}
