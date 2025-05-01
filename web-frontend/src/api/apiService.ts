import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

// 创建axios实例
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器，添加用户ID
api.interceptors.request.use(
  (config) => {
    const username = localStorage.getItem('username');
    if (username) {
      config.headers['x-user-id'] = username;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 定义API接口
export interface Message {
  message_id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  emotion_label?: string;
}

export interface UserPreferences {
  username: string;
  mbti?: string;
  tone?: string;
  age?: number;
  star_sign?: string;
}

export interface ConversationSummary {
  conversation_id: string;
  summary: string;
  last_updated: string;
  message_count: number;
  is_active: boolean;
}

// API函数
const apiService = {
  // 用户相关
  saveUserPreferences: async (preferences: UserPreferences): Promise<void> => {
    await api.post('/users/preferences', preferences);
  },

  getUserPreferences: async (username: string): Promise<UserPreferences> => {
    const response = await api.get(`/users/${username}/preferences`);
    return response.data;
  },

  updatePreferences: async (preferences: Omit<UserPreferences, 'username'>): Promise<{ success: boolean, message: string }> => {
    const response = await api.post('/agent/preferences', preferences);
    return response.data;
  },

  // 健康数据上传
  uploadHealthData: async (file: File): Promise<{ success: boolean, message: string }> => {
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    
    // 使用不同的配置发送multipart/form-data请求
    const response = await axios.post(`${BASE_URL}/agent/upload_health_data`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'x-user-id': localStorage.getItem('username') || ''
      },
    });
    
    return response.data;
  },

  // 对话相关
  startNewConversation: async (): Promise<string> => {
    const response = await api.post('/agent/start_conversation', {});
    return response.data.conversation_id || 'new';
  },

  getConversationSummaries: async (): Promise<ConversationSummary[]> => {
    const response = await api.get('/agent/conversations');
    return response.data.summaries || [];
  },

  // 消息相关
  getMessages: async (conversationId: string): Promise<Message[]> => {
    if (conversationId === 'new') return [];
    const response = await api.get(`/agent/history/${conversationId}`);
    return response.data.history || [];
  },

  sendMessage: async (conversationId: string, content: string): Promise<Message> => {
    const response = await api.post(`/agent/chat`, { 
      message: content,
      conversation_id: conversationId
    });
    return {
      message_id: `msg_${Date.now()}`,
      conversation_id: conversationId,
      role: 'assistant',
      content: response.data.response,
      timestamp: new Date().toISOString()
    };
  },

  // 智能体相关
  analyzeEmotion: async (conversationId: string, message: string): Promise<{
    emotion: string;
    response: string;
  }> => {
    const response = await api.post('/agent/analyze', {
      conversation_id: conversationId,
      message
    });
    return response.data;
  },
};

export default apiService; 