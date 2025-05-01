import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App component', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // 由于App组件使用了路由，它最初应该会加载偏好设置页面
    // 我们可以检查它是否包含特定的文本内容
    expect(screen.getByTestId('app-container')).toBeInTheDocument();
  });
}); 