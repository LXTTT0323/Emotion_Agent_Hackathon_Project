import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import PreferencePage from './pages/PreferencePage';
import ChatPage from './pages/ChatPage';

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);

  // 模拟加载过程
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background" data-testid="app-container">
      <UserProvider>
        <Routes>
          <Route path="/" element={<PreferencePage />} />
          <Route path="/chat/:conversationId" element={<ChatPage />} />
          <Route path="/chat" element={<Navigate to="/chat/new" replace />} />
        </Routes>
      </UserProvider>
    </div>
  );
};

export default App; 