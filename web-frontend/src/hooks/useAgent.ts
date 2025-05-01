import { useState } from 'react';
import apiService from '../api/apiService';

interface AgentResponse {
  emotion: string;
  response: string;
}

interface UseAgentReturn {
  sendMessage: (conversationId: string, message: string) => Promise<AgentResponse | null>;
  isProcessing: boolean;
  agentError: string | null;
  clearError: () => void;
}

export const useAgent = (): UseAgentReturn => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentError, setAgentError] = useState<string | null>(null);

  // 清除错误信息
  const clearError = () => {
    setAgentError(null);
  };

  const sendMessage = async (
    conversationId: string,
    message: string
  ): Promise<AgentResponse | null> => {
    try {
      setIsProcessing(true);
      setAgentError(null);
      
      // 发送消息到情绪分析智能体
      const response = await apiService.analyzeEmotion(conversationId, message);
      
      return response;
    } catch (error) {
      console.error('Agent处理消息失败', error);
      setAgentError('处理消息失败，请稍后再试');
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  return {
    sendMessage,
    isProcessing,
    agentError,
    clearError
  };
};

export default useAgent; 