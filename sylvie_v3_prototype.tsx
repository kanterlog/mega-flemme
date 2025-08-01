/*
🎨 Sylvie v3.0 - Prototype UI Component inspiré LobeChat
Architecture moderne avec Next.js 15 + Ant Design + TypeScript
*/

import React, { useState } from 'react';
import { 
  Layout, 
  Input, 
  Button, 
  List, 
  Avatar, 
  Card, 
  Typography, 
  Space,
  Tag,
  Tooltip,
  Dropdown,
  Modal
} from 'antd';
import { 
  SendOutlined, 
  GoogleOutlined,
  MailOutlined,
  CalendarOutlined,
  FileOutlined,
  BranchesOutlined,
  ThunderboltOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';

const { Content, Sider } = Layout;
const { Text, Title } = Typography;
const { TextArea } = Input;

// Types Sylvie v3.0
interface SylvieMessage {
  id: string;
  content: string;
  type: 'user' | 'assistant' | 'system';
  timestamp: Date;
  thinking?: ThinkingStep[];
  actions?: WorkspaceAction[];
}

interface ThinkingStep {
  id: string;
  title: string;
  content: string;
  type: 'analysis' | 'action' | 'result';
  duration: number;
}

interface WorkspaceAction {
  type: 'email' | 'calendar' | 'drive';
  action: string;
  result: any;
}

interface Conversation {
  id: string;
  title: string;
  messages: SylvieMessage[];
  branches: string[];
  context: 'google-workspace' | 'general';
  created: Date;
}

// Composant principal Sylvie v3.0
export const SylvieV3Interface: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      title: 'Gestion emails marketing Q4',
      messages: [],
      branches: [],
      context: 'google-workspace',
      created: new Date()
    }
  ]);
  
  const [currentMessage, setCurrentMessage] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [showBranching, setShowBranching] = useState(false);
  
  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;
    
    const newMessage: SylvieMessage = {
      id: Date.now().toString(),
      content: currentMessage,
      type: 'user',
      timestamp: new Date()
    };
    
    setCurrentMessage('');
    setIsThinking(true);
    
    // Simulate AI thinking process
    setTimeout(() => {
      const aiResponse: SylvieMessage = {
        id: (Date.now() + 1).toString(),
        content: `J'ai analysé votre demande "${currentMessage}". Voici ce que je peux faire pour vous aider avec Google Workspace.`,
        type: 'assistant',
        timestamp: new Date(),
        thinking: [
          {
            id: '1',
            title: 'Analyse de la demande',
            content: 'Je comprends que vous voulez travailler avec vos emails et votre calendrier.',
            type: 'analysis',
            duration: 500
          },
          {
            id: '2',
            title: 'Connexion Gmail API',
            content: 'Accès aux derniers emails et événements du calendrier.',
            type: 'action',
            duration: 800
          },
          {
            id: '3',
            title: 'Génération de la réponse',
            content: 'Préparation des options d\'action disponibles.',
            type: 'result',
            duration: 300
          }
        ],
        actions: [
          {
            type: 'email',
            action: 'search_recent',
            result: { count: 15, unread: 5 }
          }
        ]
      };
      
      setIsThinking(false);
      // Update conversations would go here
    }, 2000);
  };
  
  return (
    <Layout style={{ height: '100vh', backgroundColor: '#f5f7fa' }}>
      {/* Sidebar - Liste des conversations */}
      <Sider 
        width={320} 
        theme="light"
        style={{ 
          borderRight: '1px solid #e8eaed',
          boxShadow: '2px 0 8px rgba(0,0,0,0.1)'
        }}
      >
        <div style={{ padding: '20px 16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
            <Avatar 
              size={40} 
              style={{ backgroundColor: '#4285f4', marginRight: '12px' }}
              icon={<RobotOutlined />}
            />
            <div>
              <Title level={4} style={{ margin: 0 }}>Sylvie v3.0</Title>
              <Text type="secondary">Assistant Google Workspace</Text>
            </div>
          </div>
          
          <Button 
            type="primary" 
            block 
            size="large"
            icon={<GoogleOutlined />}
            style={{ 
              marginBottom: '20px',
              background: 'linear-gradient(135deg, #4285f4 0%, #34a853 100%)',
              border: 'none',
              borderRadius: '8px'
            }}
          >
            Nouvelle conversation
          </Button>
          
          <List
            size="small"
            dataSource={conversations}
            renderItem={(conv) => (
              <List.Item 
                style={{ 
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '8px',
                  cursor: 'pointer',
                  backgroundColor: '#fff',
                  border: '1px solid #e8eaed'
                }}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar 
                      size={32}
                      style={{ backgroundColor: '#ea4335' }}
                      icon={conv.context === 'google-workspace' ? <MailOutlined /> : <RobotOutlined />}
                    />
                  }
                  title={
                    <Text strong style={{ fontSize: '14px' }}>
                      {conv.title}
                    </Text>
                  }
                  description={
                    <div>
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {conv.created.toLocaleDateString()}
                      </Text>
                      <Tag 
                        size="small" 
                        color={conv.context === 'google-workspace' ? 'blue' : 'default'}
                        style={{ marginLeft: '8px' }}
                      >
                        {conv.context}
                      </Tag>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </div>
      </Sider>
      
      {/* Zone de chat principale */}
      <Layout>
        <Content style={{ display: 'flex', flexDirection: 'column' }}>
          {/* Header */}
          <div 
            style={{ 
              padding: '16px 24px',
              borderBottom: '1px solid #e8eaed',
              backgroundColor: '#fff',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div>
              <Title level={3} style={{ margin: 0 }}>
                Gestion emails marketing Q4
              </Title>
              <Text type="secondary">
                Conversation avec intégration Google Workspace
              </Text>
            </div>
            
            <Space>
              <Tooltip title="Créer une branche de conversation">
                <Button 
                  icon={<BranchesOutlined />}
                  onClick={() => setShowBranching(true)}
                >
                  Brancher
                </Button>
              </Tooltip>
              
              <Tooltip title="Actions Google Workspace">
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: 'gmail',
                        icon: <MailOutlined />,
                        label: 'Ouvrir Gmail'
                      },
                      {
                        key: 'calendar',
                        icon: <CalendarOutlined />,
                        label: 'Voir Calendar'
                      },
                      {
                        key: 'drive',
                        icon: <FileOutlined />,
                        label: 'Accéder Drive'
                      }
                    ]
                  }}
                >
                  <Button icon={<GoogleOutlined />}>
                    Workspace
                  </Button>
                </Dropdown>
              </Tooltip>
            </Space>
          </div>
          
          {/* Zone de messages */}
          <div 
            style={{ 
              flex: 1, 
              padding: '24px',
              overflow: 'auto',
              backgroundColor: '#fafbfc'
            }}
          >
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              {/* Message d'accueil */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Card 
                  style={{ 
                    marginBottom: '16px',
                    border: '1px solid #4285f4',
                    borderRadius: '12px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                    <Avatar 
                      size={40}
                      style={{ backgroundColor: '#4285f4', marginRight: '16px' }}
                      icon={<RobotOutlined />}
                    />
                    <div style={{ flex: 1 }}>
                      <Text strong>Sylvie v3.0</Text>
                      <div style={{ marginTop: '8px' }}>
                        <Text>
                          Bonjour ! Je suis votre assistant Google Workspace nouvelle génération. 
                          Je peux vous aider avec vos emails, votre calendrier, vos documents et bien plus encore.
                        </Text>
                        
                        <div style={{ marginTop: '16px' }}>
                          <Space wrap>
                            <Tag icon={<MailOutlined />} color="blue">Gmail</Tag>
                            <Tag icon={<CalendarOutlined />} color="green">Calendar</Tag>
                            <Tag icon={<FileOutlined />} color="orange">Drive</Tag>
                            <Tag icon={<ThunderboltOutlined />} color="purple">IA Avancée</Tag>
                          </Space>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              </motion.div>
              
              {/* Indicateur de réflexion */}
              <AnimatePresence>
                {isThinking && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                  >
                    <Card 
                      style={{ 
                        marginBottom: '16px',
                        borderRadius: '12px',
                        backgroundColor: '#f8f9fa'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar 
                          size={32}
                          style={{ backgroundColor: '#34a853', marginRight: '12px' }}
                          icon={<ThunderboltOutlined />}
                        />
                        <div>
                          <Text strong>Sylvie réfléchit...</Text>
                          <div style={{ marginTop: '4px' }}>
                            <motion.div
                              style={{ 
                                width: '100px',
                                height: '4px',
                                backgroundColor: '#e8eaed',
                                borderRadius: '2px',
                                overflow: 'hidden'
                              }}
                            >
                              <motion.div
                                style={{
                                  height: '100%',
                                  background: 'linear-gradient(90deg, #4285f4, #34a853)',
                                  borderRadius: '2px'
                                }}
                                animate={{ x: ['-100%', '100%'] }}
                                transition={{ 
                                  repeat: Infinity, 
                                  duration: 1.5,
                                  ease: 'easeInOut'
                                }}
                              />
                            </motion.div>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
          
          {/* Zone de saisie */}
          <div 
            style={{ 
              padding: '20px 24px',
              backgroundColor: '#fff',
              borderTop: '1px solid #e8eaed'
            }}
          >
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
              <Space.Compact style={{ width: '100%' }}>
                <TextArea
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  placeholder="Que puis-je faire pour vous aider avec Google Workspace ?"
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  style={{ 
                    borderRadius: '12px 0 0 12px',
                    fontSize: '16px',
                    padding: '12px 16px'
                  }}
                  onPressEnter={(e) => {
                    if (!e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
                <Button
                  type="primary"
                  size="large"
                  icon={<SendOutlined />}
                  onClick={handleSendMessage}
                  loading={isThinking}
                  style={{
                    borderRadius: '0 12px 12px 0',
                    background: 'linear-gradient(135deg, #4285f4 0%, #34a853 100%)',
                    border: 'none',
                    padding: '0 20px'
                  }}
                />
              </Space.Compact>
              
              <div style={{ marginTop: '8px', textAlign: 'center' }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  Propulsé par l'IA avancée • Intégration Google Workspace native
                </Text>
              </div>
            </div>
          </div>
        </Content>
      </Layout>
      
      {/* Modal Branching */}
      <Modal
        title="Créer une branche de conversation"
        open={showBranching}
        onCancel={() => setShowBranching(false)}
        footer={null}
        width={600}
      >
        <div style={{ padding: '20px 0' }}>
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card 
              hoverable
              onClick={() => {/* Handle continuation */}}
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <Avatar 
                  size={48}
                  style={{ backgroundColor: '#4285f4', marginRight: '16px' }}
                  icon={<BranchesOutlined />}
                />
                <div>
                  <Title level={4} style={{ margin: 0 }}>
                    Continuer la conversation
                  </Title>
                  <Text type="secondary">
                    Garder le contexte actuel et continuer sur le même sujet
                  </Text>
                </div>
              </div>
            </Card>
            
            <Card 
              hoverable
              onClick={() => {/* Handle new direction */}}
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <Avatar 
                  size={48}
                  style={{ backgroundColor: '#34a853', marginRight: '16px' }}
                  icon={<ThunderboltOutlined />}
                />
                <div>
                  <Title level={4} style={{ margin: 0 }}>
                    Nouvelle direction
                  </Title>
                  <Text type="secondary">
                    Partir dans une direction différente avec un contexte frais
                  </Text>
                </div>
              </div>
            </Card>
          </Space>
        </div>
      </Modal>
    </Layout>
  );
};

export default SylvieV3Interface;
