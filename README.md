# Emotion Agent Hackathon Project

基于生理数据的情感分析与共情互动AI助手

[![Backend CI](https://github.com/LXTTT0323/Emotion_Agent_Hackathon_Project/actions/workflows/backend.yml/badge.svg)](https://github.com/LXTTT0323/Emotion_Agent_Hackathon_Project/actions/workflows/backend.yml)
[![Frontend CI](https://github.com/LXTTT0323/Emotion_Agent_Hackathon_Project/actions/workflows/frontend.yml/badge.svg)](https://github.com/LXTTT0323/Emotion_Agent_Hackathon_Project/actions/workflows/frontend.yml)
[![E2E Tests](https://github.com/LXTTT0323/Emotion_Agent_Hackathon_Project/actions/workflows/e2e.yml/badge.svg)](https://github.com/LXTTT0323/Emotion_Agent_Hackathon_Project/actions/workflows/e2e.yml)

## 项目概述

情感智能代理旨在提供基于实时情感分析的个性化支持和互动体验。该项目针对22-40岁的用户，分析用户输入的文本，识别情绪状态，并通过共情回应提供情感支持。

- **前端**: React + TypeScript + Tailwind CSS 构建的响应式Web应用
- **后端**: Python FastAPI + Semantic Kernel 构建的智能代理服务
- **核心功能**: 情感分类、个性化建议、上下文记忆

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- npm 8+

### 一键安装依赖

```bash
# 克隆仓库
git clone https://github.com/LXTTT0323/Emotion_Agent_Hackathon_Project
cd Emotion_Agent_Hackathon_Project

# 安装依赖
make bootstrap   # 安装Python和Node.js依赖
```

### 运行开发环境

```bash
# 启动后端和前端开发服务器
make dev

# 或者分别启动
make backend    # 仅启动后端服务器 (http://localhost:8000)
make frontend   # 仅启动前端开发服务器 (http://localhost:3000)
```

## 项目结构

```
Emotion_Agent_Hackathon_Project/
├── backend/                 # FastAPI后端
│   ├── memory/              # 数据存储和检索
│   ├── routers/             # API路由
│   ├── services/            # 核心服务逻辑
│   │   ├── agent_kernel.py  # 智能体核心
│   │   └── summarizer.py    # 会话摘要服务
│   ├── tools/               # 专用工具函数
│   └── main.py              # 应用入口
│
├── web-frontend/            # React前端
│   ├── src/                 # 源代码
│   │   ├── api/             # API服务
│   │   ├── components/      # UI组件
│   │   ├── context/         # React上下文
│   │   ├── hooks/           # 自定义钩子
│   │   └── pages/           # 页面组件
│   ├── cypress/             # E2E测试
│   ├── public/              # 静态资源
│   └── package.json         # 依赖配置
│
├── .github/workflows/       # CI/CD配置
├── requirements.txt         # Python依赖
└── Makefile                 # 项目命令
```

## 核心功能

### 前端功能

1. **用户偏好设置**:
   - MBTI性格设置
   - 对话风格偏好
   - 年龄和星座选项

2. **聊天界面**:
   - 实时对话流
   - 情绪状态显示
   - 消息历史浏览

3. **会话管理**:
   - 历史会话列表
   - 会话摘要展示
   - 新会话创建

### 后端功能

1. **情感分析**:
   - 文本情感分类 (积极/中性/消极)
   - 情感变化跟踪
   - 情绪状态驱动的回应

2. **上下文记忆**:
   - 用户历史交互记录
   - 每10条消息生成摘要
   - 智能检索相关记忆

3. **个性化互动**:
   - 基于用户偏好调整回应
   - 情感共情机制
   - 主动提问策略

## API文档

应用启动后，可以通过以下地址访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发者文档

### 分支策略

- **main**: 始终可部署的主分支
- **merge/all-\<date\>**: 集成分支，用于解决冲突
- **feat/\<area\>-\<date\>**: 功能分支
- **fix/\<brief\>**: 修复分支

### 编码规范

- **Python**: Black + Ruff; 类型标注; 通过pydantic.BaseSettings使用环境变量
- **React**: 函数组件; TypeScript; Tailwind CSS
- **提交**: 遵循Conventional Commits规范

### 测试

```bash
# 运行所有测试
make test

# 运行端到端测试
make test-e2e
```

## 贡献指南

1. Fork此仓库
2. 创建功能分支: `git checkout -b feat/feature-name-date`
3. 提交更改: `git commit -m 'feat: add some feature'`
4. 推送到分支: `git push origin feat/feature-name-date`
5. 提交Pull Request到集成分支

## 许可证

本项目采用MIT许可证
