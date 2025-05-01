import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import MessageInput from '../components/MessageInput';
import ChatMessage, { TypingIndicator } from '../components/ChatMessage';
import FileUpload from '../components/FileUpload';
import Button from '../components/Button';
import { useUser } from '../context/UserContext';
import { useAgent } from '../hooks/useAgent';
import apiService, { Message } from '../api/apiService';

const ChatPage: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, username } = useUser();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUpload, setShowUpload] = useState(true);
  const [isInitializing, setIsInitializing] = useState(true);
  
  // 使用agent Hook
  const { sendMessage, isProcessing, agentError } = useAgent();
  
  // 处理新对话请求
  const handleStartNewConversation = async () => {
    try {
      setIsLoading(true);
      // 调用后端API开始新对话
      await apiService.startNewConversation();
      
      // 立即重置界面状态
      setMessages([]);
      setShowUpload(true);
      setError(null);
      
      // 如果当前已经在/chat/new路径，则只重置状态，不需要导航
      if (conversationId === 'new') {
        // 已经在新对话页面，触发一个状态更新确保UI刷新
        setIsInitializing(true);
        setTimeout(() => setIsInitializing(false), 10);
      } else {
        // 导航到新对话路由
        navigate('/chat/new');
      }
    } catch (err) {
      console.error('开始新对话失败', err);
      setError('开始新对话失败，请稍后再试');
    } finally {
      setIsLoading(false);
    }
  };
  
  // 如果未认证，重定向到偏好设置页面
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);
  
  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  // 当消息更新时，滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // 加载对话历史
  useEffect(() => {
    const fetchMessages = async () => {
      if (!conversationId || conversationId === 'new') {
        // 当是新对话时，彻底重置状态
        setMessages([]);
        setShowUpload(true);
        setError(null);
        setIsInitializing(false);
        return;
      }
      
      try {
        setIsLoading(true);
        const fetchedMessages = await apiService.getMessages(conversationId);
        setMessages(fetchedMessages);
        
        // 如果已经有消息了，不显示上传组件
        if (fetchedMessages && fetchedMessages.length > 0) {
          setShowUpload(false);
        }
      } catch (err) {
        console.error('获取消息失败', err);
        setError('获取消息失败，请稍后再试');
      } finally {
        setIsLoading(false);
        setIsInitializing(false);
      }
    };
    
    if (isAuthenticated) {
      fetchMessages();
    }
  }, [conversationId, isAuthenticated]);
  
  // 处理健康数据上传
  const handleUploadHealthData = async (file: File) => {
    try {
      setIsLoading(true);
      const response = await apiService.uploadHealthData(file);
      
      if (response.success) {
        setShowUpload(false);
        
        // 直接使用上传API返回的分析结果作为消息
        const assistantMessage: Message = {
          message_id: `analysis-${Date.now()}`,
          conversation_id: conversationId || 'new',
          role: 'assistant',
          content: response.message, // 使用API返回的问题作为消息内容
          timestamp: new Date().toISOString(),
        };
        
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error(response.message);
      }
    } catch (err) {
      console.error('上传健康数据失败', err);
      const errorMessage = err instanceof Error ? err.message : '上传失败，请重试';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };
  
  // 处理发送消息
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;
    
    try {
      // 显示用户消息
      const userMessage: Message = {
        message_id: `temp-${Date.now()}`,
        conversation_id: conversationId || 'new',
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };
      
      setMessages(prev => [...prev, userMessage]);
      setIsTyping(true);
      
      // 创建新对话或使用现有对话
      let currentConversationId = conversationId;
      if (!conversationId || conversationId === 'new') {
        try {
          currentConversationId = await apiService.startNewConversation();
          window.history.replaceState(null, '', `/chat/${currentConversationId}`);
          // 发送了第一条消息，关闭上传组件
          setShowUpload(false);
        } catch (err) {
          console.error('创建新对话失败', err);
          setError('创建新对话失败，请稍后再试');
          setIsTyping(false);
          return;
        }
      }
      
      // 发送消息到后端
      const response = await sendMessage(currentConversationId!, content);
      
      if (response) {
        const assistantMessage: Message = {
          message_id: `temp-response-${Date.now()}`,
          conversation_id: currentConversationId!,
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString(),
          emotion_label: response.emotion,
        };
        
        setMessages(prev => [...prev, assistantMessage]);
        // 确保一旦有消息交流，上传组件不再显示
        if (showUpload) {
          setShowUpload(false);
        }
      }
    } catch (err) {
      console.error('发送消息失败', err);
      setError('发送消息失败，请稍后再试');
    } finally {
      setIsTyping(false);
    }
  };

  // 渲染加载状态
  if (isInitializing) {
    return (
      <div className="flex flex-col h-screen bg-background">
        <header className="bg-white shadow-sm p-4">
          <h1 className="text-xl font-semibold">初始化聊天...</h1>
        </header>
        <div className="flex-1 flex items-center justify-center">
          <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* 标题栏 */}
      <header className="bg-white shadow-sm p-4 flex justify-between items-center">
        <div className="flex items-center">
          <Button
            onClick={() => navigate('/')}
            variant="ghost"
            className="mr-2 text-gray-900"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
          </Button>
          <h1 className="text-xl font-semibold text-gray-900">情绪共情对话</h1>
        </div>
        <Button
          onClick={() => handleStartNewConversation()}
          variant="outline"
          className="text-gray-900 border-gray-300 hover:bg-gray-50"
          disabled={isLoading}
        >
          {isLoading ? '加载中...' : '新对话'}
        </Button>
      </header>
      
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {error || agentError ? (
          <div className="bg-red-50 text-error p-4 rounded-lg">
            {error || agentError}
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-12">
            <h2 className="text-xl font-medium text-gray-900 mb-4">开始一个新对话</h2>
            <p className="text-gray-700 mb-8">
              首先上传您的健康数据文件，然后我们可以开始对话
            </p>
            
            {/* 健康数据上传组件 */}
            {showUpload && (
              <div className="max-w-md mx-auto mb-8 p-6 bg-white rounded-lg shadow-sm">
                <FileUpload
                  onUpload={handleUploadHealthData}
                  label="上传心率变异性数据"
                  buttonText="上传CSV文件"
                  acceptedFileTypes=".csv"
                  isLoading={isLoading}
                />
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <ChatMessage
                key={message.message_id}
                message={message}
              />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* 输入框 */}
      <div className="bg-white p-4 border-t border-gray-200">
        <MessageInput
          onSendMessage={handleSendMessage}
          disabled={isProcessing || isTyping || (showUpload && messages.length === 0)}
          placeholder={showUpload && messages.length === 0 ? "请先上传健康数据..." : "输入消息..."}
        />
      </div>
    </div>
  );
};

export default ChatPage; 