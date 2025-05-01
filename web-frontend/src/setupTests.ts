import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock for BrowserRouter
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    // @ts-ignore -- 忽略扩展对象的typescript错误
    ...actual,
    BrowserRouter: ({ children }: { children: React.ReactNode }) => children,
    useNavigate: () => vi.fn(),
    useParams: () => ({}),
  }
}); 