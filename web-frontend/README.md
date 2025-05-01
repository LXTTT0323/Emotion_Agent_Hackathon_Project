# 情绪共情机器人前端

这个项目是情绪共情机器人的Web前端实现，使用React + TypeScript + Tailwind CSS构建。

## 功能特性

- 用户偏好设置：设置MBTI、语气、年龄、星座等个人偏好
- 对话列表：查看历史对话和摘要
- 聊天界面：与情绪共情机器人进行实时对话
- 情绪分析：自动分析用户情绪并给予共情回复

## 技术栈

- React 18
- TypeScript
- Tailwind CSS
- React Router
- Axios
- Vite

## 项目结构

```
web-frontend/
├── public/              # 静态资源
├── src/                 # 源代码
│   ├── api/             # API服务和接口定义
│   ├── components/      # UI组件
│   ├── context/         # React Context
│   ├── hooks/           # 自定义Hooks
│   ├── pages/           # 页面组件
│   ├── styles/          # 样式文件
│   ├── App.tsx          # 主应用组件
│   └── main.tsx         # 入口文件
├── index.html           # HTML模板
├── package.json         # 项目依赖
├── tsconfig.json        # TypeScript配置
├── tailwind.config.js   # Tailwind配置
└── vite.config.ts       # Vite配置
```

## 开发指南

### 环境准备

确保您已安装:
- Node.js 16+
- npm 8+

### 安装依赖

```bash
cd web-frontend
npm install
```

### 开发模式

```bash
npm run dev
```

这将启动开发服务器，默认访问地址为 http://localhost:5173

### 构建项目

```bash
npm run build
```

构建产物将输出到 `dist` 目录

### 运行测试

```bash
npm run test
```

## API接口

前端通过以下主要API与后端通信：

- `/users/preferences` - 用户偏好设置
- `/conversations` - 对话管理
- `/conversations/:id/messages` - 消息管理
- `/agent/analyze` - 情绪分析和回复

## 页面路由

- `/` - 偏好设置页面
- `/chat` - 对话列表页面
- `/chat/:conversationId` - 聊天室页面

## 状态管理

使用React Context API管理全局状态：
- `UserContext` - 管理用户信息和认证状态

## 贡献指南

1. Fork此仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个Pull Request

## 许可证

MIT License 