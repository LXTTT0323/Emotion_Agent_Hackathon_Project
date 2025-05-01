import { createContext, useState, useContext, ReactNode, useEffect } from 'react';

interface UserPreferences {
  mbti?: string;
  tone?: string;
  age?: number;
  star_sign?: string;
}

interface UserContextType {
  userId: string;
  username: string;
  preferences: UserPreferences;
  setUserId: (id: string) => void;
  setUsername: (name: string) => void;
  setPreferences: (prefs: UserPreferences) => void;
  isAuthenticated: boolean;
}

const defaultUserContext: UserContextType = {
  userId: '',
  username: '',
  preferences: {
    mbti: undefined,
    tone: 'supportive',
    age: undefined,
    star_sign: undefined
  },
  setUserId: () => {},
  setUsername: () => {},
  setPreferences: () => {},
  isAuthenticated: false
};

const UserContext = createContext<UserContextType>(defaultUserContext);

export const useUser = () => useContext(UserContext);

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider = ({ children }: UserProviderProps) => {
  const [userId, setUserIdState] = useState<string>('');
  const [username, setUsernameState] = useState<string>('');
  const [preferences, setPreferencesState] = useState<UserPreferences>(defaultUserContext.preferences);
  
  // 从localStorage获取用户信息
  useEffect(() => {
    const storedUserId = localStorage.getItem('userId');
    const storedUsername = localStorage.getItem('username');
    const storedPreferences = localStorage.getItem('preferences');
    
    if (storedUserId) setUserIdState(storedUserId);
    if (storedUsername) setUsernameState(storedUsername);
    if (storedPreferences) {
      try {
        setPreferencesState(JSON.parse(storedPreferences));
      } catch (e) {
        console.error('Failed to parse stored preferences', e);
      }
    }
  }, []);
  
  // 更新localStorage当状态改变
  useEffect(() => {
    if (userId) localStorage.setItem('userId', userId);
    if (username) localStorage.setItem('username', username);
    if (Object.keys(preferences).length > 0) {
      localStorage.setItem('preferences', JSON.stringify(preferences));
    }
  }, [userId, username, preferences]);
  
  const setUserId = (id: string) => {
    setUserIdState(id);
  };
  
  const setUsername = (name: string) => {
    setUsernameState(name);
  };
  
  const setPreferences = (prefs: UserPreferences) => {
    setPreferencesState({ ...preferences, ...prefs });
  };
  
  const isAuthenticated = Boolean(userId || username);
  
  return (
    <UserContext.Provider value={{
      userId,
      username,
      preferences,
      setUserId,
      setUsername,
      setPreferences,
      isAuthenticated
    }}>
      {children}
    </UserContext.Provider>
  );
}; 