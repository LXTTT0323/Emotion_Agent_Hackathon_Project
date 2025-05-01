import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import TextInput from '../components/TextInput';
import Select, { SelectOption } from '../components/Select';
import { useUser } from '../context/UserContext';
import apiService from '../api/apiService';

// 定义选项
const mbtiOptions: SelectOption[] = [
  { value: 'INTJ', label: 'INTJ - 建筑师' },
  { value: 'INTP', label: 'INTP - 逻辑学家' },
  { value: 'ENTJ', label: 'ENTJ - 指挥官' },
  { value: 'ENTP', label: 'ENTP - 辩论家' },
  { value: 'INFJ', label: 'INFJ - 提倡者' },
  { value: 'INFP', label: 'INFP - 调停者' },
  { value: 'ENFJ', label: 'ENFJ - 主人公' },
  { value: 'ENFP', label: 'ENFP - campaigner' },
  { value: 'ISTJ', label: 'ISTJ - 物流师' },
  { value: 'ISFJ', label: 'ISFJ - 守卫者' },
  { value: 'ESTJ', label: 'ESTJ - 总经理' },
  { value: 'ESFJ', label: 'ESFJ - 执政官' },
  { value: 'ISTP', label: 'ISTP - 鉴赏家' },
  { value: 'ISFP', label: 'ISFP - 探险家' },
  { value: 'ESTP', label: 'ESTP - 企业家' },
  { value: 'ESFP', label: 'ESFP - 表演者' },
];

const toneOptions: SelectOption[] = [
  { value: 'supportive', label: '支持型 - 温暖鼓励' },
  { value: 'analytical', label: '分析型 - 理性客观' },
  { value: 'cheerful', label: '愉快型 - 积极轻松' },
  { value: 'professional', label: '专业型 - 正式专业' },
];

const starSignOptions: SelectOption[] = [
  { value: 'aries', label: '白羊座 (3.21-4.19)' },
  { value: 'taurus', label: '金牛座 (4.20-5.20)' },
  { value: 'gemini', label: '双子座 (5.21-6.21)' },
  { value: 'cancer', label: '巨蟹座 (6.22-7.22)' },
  { value: 'leo', label: '狮子座 (7.23-8.22)' },
  { value: 'virgo', label: '处女座 (8.23-9.22)' },
  { value: 'libra', label: '天秤座 (9.23-10.23)' },
  { value: 'scorpio', label: '天蝎座 (10.24-11.22)' },
  { value: 'sagittarius', label: '射手座 (11.23-12.21)' },
  { value: 'capricorn', label: '摩羯座 (12.22-1.19)' },
  { value: 'aquarius', label: '水瓶座 (1.20-2.18)' },
  { value: 'pisces', label: '双鱼座 (2.19-3.20)' },
];

const PreferencePage: React.FC = () => {
  const navigate = useNavigate();
  const { username, setUsername, preferences, setPreferences } = useUser();
  
  const [formState, setFormState] = useState({
    username: username || '',
    mbti: preferences.mbti || '',
    tone: preferences.tone || 'supportive',
    age: preferences.age?.toString() || '',
    star_sign: preferences.star_sign || '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prev => ({ ...prev, [name]: value }));
    
    // Clear error when field is modified
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };
  
  const validate = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formState.username.trim()) {
      newErrors.username = '请输入用户名';
    }
    
    if (formState.age && (isNaN(Number(formState.age)) || Number(formState.age) < 1 || Number(formState.age) > 120)) {
      newErrors.age = '请输入有效年龄 (1-120)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    try {
      setIsLoading(true);
      
      // 保存到本地状态
      setUsername(formState.username);
      setPreferences({
        mbti: formState.mbti || undefined,
        tone: formState.tone,
        age: formState.age ? parseInt(formState.age) : undefined,
        star_sign: formState.star_sign || undefined,
      });
      
      // 保存到后端
      await apiService.updatePreferences({
        mbti: formState.mbti || undefined,
        tone: formState.tone,
        age: formState.age ? parseInt(formState.age) : undefined,
        star_sign: formState.star_sign || undefined,
      });
      
      // 重定向到聊天页面
      navigate('/chat');
    } catch (error) {
      console.error('保存偏好设置失败', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-background flex justify-center items-center p-4">
      <div className="bg-white rounded-xl shadow-lg p-6 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">设置您的偏好</h1>
        
        <form onSubmit={handleSubmit}>
          <TextInput
            label="用户名"
            name="username"
            value={formState.username}
            onChange={handleChange}
            placeholder="请输入用户名"
            error={errors.username}
            required
          />
          
          <Select
            label="MBTI 性格类型"
            name="mbti"
            value={formState.mbti}
            onChange={handleChange}
            options={mbtiOptions}
          />
          
          <Select
            label="对话风格"
            name="tone"
            value={formState.tone}
            onChange={handleChange}
            options={toneOptions}
            required
          />
          
          <TextInput
            label="年龄"
            name="age"
            type="number"
            value={formState.age}
            onChange={handleChange}
            placeholder="可选"
            error={errors.age}
          />
          
          <Select
            label="星座"
            name="star_sign"
            value={formState.star_sign}
            onChange={handleChange}
            options={starSignOptions}
          />
          
          <div className="mt-8">
            <Button
              type="submit"
              fullWidth
              isLoading={isLoading}
            >
              保存并开始聊天
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PreferencePage; 