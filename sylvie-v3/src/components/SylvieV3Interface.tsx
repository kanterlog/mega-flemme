'use client';

import React, { useState } from 'react';
import { Layout, Input, Button, Avatar, Dropdown, Space, Card, Tag, Modal, Typography } from 'antd';
import { 
  SendOutlined, 
  SettingOutlined, 
  UserOutlined, 
  MenuOutlined,
  BranchesOutlined,
  MailOutlined,
  CalendarOutlined,
  FileTextOutlined,
  FolderOutlined,
  CheckSquareOutlined,
  LoadingOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { useSylvieStore } from '@/store/sylvieStore';

const { Header, Content, Sider } = Layout;
const { TextArea } = Input;
const { Text, Title } = Typography;

export function SylvieV3Interface() {
  const [inputValue, setInputValue] = useState('');
  const [showBranchModal, setShowBranchModal] = useState(false);
  
  const {
    messages,
    isThinking,
    sidebarOpen,
    conversations,
    activeConversationId,
    addMessage,
    setThinking,
    toggleSidebar,
    createConversation,
    setActiveConversation,
  } = useSylvieStore();

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Créer une conversation si aucune n'est active
    if (!activeConversationId) {
      createConversation();
    }

    // Ajouter le message utilisateur
    addMessage({
      type: 'user',
      content: inputValue,
    });

    setInputValue('');
    setThinking(true);

    // Simuler une réponse de l'IA
    setTimeout(() => {
      addMessage({
        type: 'assistant',
        content: `Bonjour ! J'ai reçu votre message : "${inputValue}". Je suis Sylvie, votre assistant IA pour Google Workspace. Comment puis-je vous aider aujourd'hui ?`,
        metadata: {
          actions: [
            {
              type: 'email',
              action: 'check_unread',
              description: 'Vérifier les emails non lus',
              status: 'success',
            },
          ],
        },
      });
      setThinking(false);
    }, 2000);
  };

  const workspaceActions = [
    { icon: <MailOutlined />, label: 'Gmail', color: '#ea4335' },
    { icon: <CalendarOutlined />, label: 'Calendar', color: '#4285f4' },
    { icon: <FolderOutlined />, label: 'Drive', color: '#0f9d58' },
    { icon: <FileTextOutlined />, label: 'Docs', color: '#4285f4' },
    { icon: <CheckSquareOutlined />, label: 'Tasks', color: '#f9ab00' },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      label: 'Profil',
      icon: <UserOutlined />,
    },
    {
      key: 'settings',
      label: 'Paramètres',
      icon: <SettingOutlined />,
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      label: 'Déconnexion',
      danger: true,
    },
  ];

  return (
    <Layout className="min-h-screen">
      <Header className="flex items-center justify-between px-6 bg-white/95 backdrop-blur-md border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={toggleSidebar}
            className="lg:hidden"
          />
          <div className="flex items-center space-x-2">
            <RobotOutlined className="text-2xl text-sylvie-600" />
            <Title level={3} className="m-0 text-gradient">
              Sylvie v3.0
            </Title>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <Space>
            {workspaceActions.map((action, index) => (
              <Button
                key={index}
                type="text"
                icon={action.icon}
                size="small"
                style={{ color: action.color }}
                title={action.label}
              />
            ))}
          </Space>
          
          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <Avatar 
              size="large" 
              icon={<UserOutlined />} 
              className="cursor-pointer bg-sylvie-500"
            />
          </Dropdown>
        </div>
      </Header>

      <Layout>
        <AnimatePresence>
          {sidebarOpen && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 280, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Sider 
                width={280} 
                className="bg-white/95 backdrop-blur-md border-r border-gray-200"
                style={{ height: 'calc(100vh - 64px)' }}
              >
                <div className="p-4 space-y-4">
                  <Button 
                    type="primary" 
                    block 
                    size="large"
                    onClick={() => createConversation()}
                    className="bg-sylvie-500 border-sylvie-500"
                  >
                    Nouvelle conversation
                  </Button>
                  
                  <div className="space-y-2">
                    <Text strong className="text-gray-600">
                      Conversations récentes
                    </Text>
                    {conversations.map((conv) => (
                      <Card
                        key={conv.id}
                        size="small"
                        hoverable
                        className={`cursor-pointer transition-all ${
                          activeConversationId === conv.id 
                            ? 'border-sylvie-500 bg-sylvie-50' 
                            : ''
                        }`}
                        onClick={() => setActiveConversation(conv.id)}
                      >
                        <div className="flex items-center justify-between">
                          <Text ellipsis className="flex-1">
                            {conv.title}
                          </Text>
                          <Text type="secondary" className="text-xs">
                            {conv.updatedAt.toLocaleDateString('fr-FR')}
                          </Text>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
              </Sider>
            </motion.div>
          )}
        </AnimatePresence>

        <Content className="flex flex-col h-screen">
          <div className="flex-1 overflow-auto p-6 space-y-4">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="sylvie-message"
                >
                  <Card
                    className={`max-w-3xl ${
                      message.type === 'user' 
                        ? 'ml-auto bg-sylvie-500 text-white' 
                        : 'mr-auto sylvie-chat-container'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <Avatar
                        size="small"
                        icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                        className={message.type === 'user' ? 'bg-white text-sylvie-500' : 'bg-sylvie-500'}
                      />
                      <div className="flex-1">
                        <Text className={message.type === 'user' ? 'text-white' : ''}>
                          {message.content}
                        </Text>
                        
                        {message.metadata?.actions && (
                          <div className="mt-3 space-y-2">
                            {message.metadata.actions.map((action, index) => (
                              <Tag
                                key={index}
                                color={action.status === 'success' ? 'green' : 'orange'}
                                className="flex items-center space-x-1"
                              >
                                <span>{action.description}</span>
                              </Tag>
                            ))}
                          </div>
                        )}
                      </div>
                      
                      <Button
                        type="text"
                        size="small"
                        icon={<BranchesOutlined />}
                        onClick={() => setShowBranchModal(true)}
                        title="Créer une branche"
                      />
                    </div>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>

            {isThinking && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mr-auto max-w-3xl"
              >
                <Card className="sylvie-chat-container">
                  <div className="flex items-center space-x-3">
                    <Avatar
                      size="small"
                      icon={<LoadingOutlined spin />}
                      className="bg-sylvie-500"
                    />
                    <div className="sylvie-thinking px-3 py-1 rounded-full">
                      <Text className="text-white text-sm">Sylvie réfléchit...</Text>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}
          </div>

          <div className="p-6 border-t border-gray-200 bg-white/95 backdrop-blur-md">
            <div className="max-w-4xl mx-auto">
              <div className="flex space-x-3">
                <TextArea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Décrivez ce que vous voulez faire avec votre Google Workspace..."
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  onPressEnter={(e) => {
                    if (e.shiftKey) return;
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex-1"
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isThinking}
                  className="bg-sylvie-500 border-sylvie-500"
                  size="large"
                />
              </div>
            </div>
          </div>
        </Content>
      </Layout>

      <Modal
        title="Créer une branche de conversation"
        open={showBranchModal}
        onCancel={() => setShowBranchModal(false)}
        footer={null}
      >
        <Text>
          Fonctionnalité de branchement en cours de développement...
        </Text>
      </Modal>
    </Layout>
  );
}
