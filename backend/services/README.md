# Memory 模块

Memory 模块负责管理情感 AI 助手的记忆和上下文存储系统。它实现了用户交互历史的持久化存储，情绪状态的跟踪，以及上下文信息的检索功能。

## 核心功能

- **用户交互历史管理**：记录和存储用户的对话历史
- **情绪状态跟踪**：维护用户情绪变化的时间线
- **上下文信息存储**：保存用户相关的上下文信息
- **数据持久化**：将数据保存到本地文件系统

## 文件结构

- `context_store.py`: 上下文存储的核心实现
- `memory.json`: 存储用户数据的 JSON 文件（自动生成）

## ContextStore 类

`ContextStore` 类提供了以下主要功能：

### 初始化

```python
def __init__(self, memory_path: str = None)
```

- 初始化存储系统
- 设置内存文件路径
- 加载现有数据

### 数据管理

```python
async def add_interaction(self, user_id: str, text: str, emotion: str, confidence: (小数), suggestion: str)
```

- 记录新的用户交互
- 更新情绪历史
- 维护最后活动时间戳

### 数据查询

```python
async def get_user_context(self, user_id: str) -> Dict[str, Any]
```

- 获取用户的完整上下文信息
- 返回交互历史和情绪历史

```python
async def get_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]
```

- 获取用户最近的情绪记录
- 支持自定义返回记录数量

## 数据格式

### 内存文件结构

```json
{
  "users": {
    "user_id": {
      "interactions": [
        {
          "timestamp": "ISO格式时间戳",
          "text": "用户消息",
          "emotion": "情绪状态",
          "suggestion": "AI建议"
        }
      ],
      "emotion_history": [
        {
          "timestamp": "ISO格式时间戳",
          "emotion": "情绪状态"
        }
      ],
      "last_active": "最后活动时间戳"
    }
  }
}
```

## 使用限制

- 每个用户的交互历史最多保存 20 条记录
- 情绪历史记录默认返回最近 5 条
- 所有时间戳使用 ISO 格式存储

## 错误处理

- 文件读写错误会被捕获并记录
- 用户不存在时返回空数据
- 数据格式错误时返回默认值

## 注意事项

1. 确保有足够的磁盘空间用于存储数据
2. 定期备份 `memory.json` 文件
3. 在生产环境中考虑使用数据库替代文件存储

## AgentKernel 调用方法

AgentKernel 是情感 AI 助手的核心组件，负责处理用户交互和情绪分析。以下是其主要调用流程：

### 对话流程

1. **初始化对话**

```python
agent = AgentKernel(mode="default")  # 或 "mock" 用于测试
```

2. **开始新对话**

```python
agent.start_conversation(user_id)
```

3. **处理用户消息**

```python
response = await agent.chat(
    query="用户消息",
    user_id="用户ID",
    emotion="当前情绪",  # P=积极, N=中性, D=消极
    confidence=0.85  # 情绪置信度
)
```

4. **主动发起对话**

```python
response = await agent.followup(
    user_id="用户ID",
    emotion="当前情绪",
    confidence=0.85,
    time_of_day="时间段",  # morning, afternoon, evening, night
    reason="特殊原因"
)
```

### 数据交互流程

1. **对话前获取上下文**

```python
context = agent.get_user_context_from_memory(user_id, query)
```

2. **获取最近情绪记录**

```python
recent_emotions = agent.get_recent_emotions(user_id, limit=5)
```

3. **记录交互数据**

```python
await context_store.add_interaction(
    user_id="用户ID",
    text="用户消息",
    emotion="情绪状态",
    confidence=0.85,
    suggestion="AI回复"
)
```

### 数据格式

#### 交互记录格式

```json
{
  "user_id": "用户ID",
  "text": "用户消息",
  "emotion": "情绪状态",
  "confidence": 0.85,
  "suggestion": "AI回复"
}
```

#### 情绪历史格式

```json
{
  "timestamp": "ISO格式时间戳",
  "emotion": "情绪状态",
  "confidence": 0.85
}
```

### 注意事项

1. 每次对话后都会自动分析情绪状态
2. 所有交互都会被记录到 ContextStore
3. 对话历史最多保存 20 条记录
4. 情绪历史默认返回最近 5 条记录
5. 确保在每次对话前获取用户上下文
6. 在生成回复前获取最近的情绪记录
