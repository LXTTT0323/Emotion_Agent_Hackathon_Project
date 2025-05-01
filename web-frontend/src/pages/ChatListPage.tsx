import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import { useUser } from '../context/UserContext';
import apiService from '../api/apiService';

const ChatListPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useUser();
  
  // 如果未认证，重定向到偏好设置页面
  React.useEffect(() => {
    if (!isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);
  
  // 处理开始新对话
  const handleStartNewConversation = async () => {
    try {
      await apiService.startNewConversation();
      // 重定向到新对话
      navigate('/chat/new');
    } catch (err) {
      console.error('开始新对话失败', err);
    }
  };
  
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="text-center max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-medium text-gray-800 mb-6">开始一个新对话</h2>
        <p className="text-gray-600 mb-8">
          与情绪共情机器人开始对话，探索AI如何理解和回应您的情绪状态
        </p>
        <Button
          onClick={handleStartNewConversation}
          fullWidth
        >
          开始对话
        </Button>
      </div>
    </div>
  );
};

export default ChatListPage; 