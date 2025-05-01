import React from 'react';
import { Message } from '../api/apiService';

interface ChatMessageProps {
  message: Message;
  isLatest?: boolean;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex w-full my-2 message-animation ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div 
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser 
            ? 'bg-primary text-white rounded-tr-none' 
            : 'bg-white border border-gray-200 rounded-tl-none'
        }`}
      >
        {message.content}
      </div>
    </div>
  );
};

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex w-full my-2 justify-start">
      <div className="bg-white border border-gray-200 rounded-lg rounded-tl-none max-w-[80%] px-4 py-2">
        <span className="typing-indicator">AI正在思考中</span>
      </div>
    </div>
  );
};

export default ChatMessage; 