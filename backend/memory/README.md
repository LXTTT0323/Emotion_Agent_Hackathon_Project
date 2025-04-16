# 情感代理上下文存储系统

这个系统实现了一个用于情感代理应用的记忆和上下文存储管理类。系统可以跟踪用户的交互历史、情绪状态，并提供分析功能。

## 核心文件

- `context_store.py` - 主要的 `ContextStore` 类定义，处理用户交互和情绪记忆的管理
- `test_context_store.py` - 演示和测试 `ContextStore` 功能的脚本
- `memory.json` - 存储用户交互和情绪数据的JSON文件

## 使用方法

### 基本流程

1. 创建一个 `ContextStore` 实例
2. 添加用户交互
3. 添加用户反馈
4. 使用分析方法获取用户情绪趋势和上下文
5. 保存内存到文件

### 运行测试脚本

```bash
python test_context_store.py
```

这个脚本将演示 `ContextStore` 类的各种功能，包括：
- 创建和加载内存
- 添加和获取用户交互
- 分析情绪趋势
- 查找相关的用户交互
- 获取用户活跃日和情绪分布

### 代码示例

```python
# 创建上下文存储
context_store = ContextStore("memory.json")

# 添加用户交互
timestamp = context_store.add_interaction(
    user_id="user123",
    text="我今天感觉很开心",
    emotion="happy",
    confidence=0.92,
    suggestion="很高兴听到你今天心情不错，继续保持！",
    metadata={"time_of_day": "morning"}
)

# 获取用户的最近情绪
recent_emotions = context_store.get_recent_emotions("user123", limit=5)

# 添加反馈
context_store.add_feedback(
    user_id="user123",
    interaction_timestamp=timestamp,
    rating=5,
    text="这个建议对我很有帮助！"
)

# 保存记忆到文件
context_store.save_memory()
```

## 主要功能

1. **用户交互管理**
   - 添加新的用户交互记录
   - 为交互添加用户反馈

2. **情绪分析**
   - 获取用户最近的情绪记录
   - 分析情绪趋势
   - 计算情绪分布

3. **上下文分析**
   - 提取用户交互中频繁出现的上下文关键词
   - 基于关键词搜索相关交互

4. **用户统计**
   - 跟踪用户活跃天数
   - 计算反馈评分平均值
   - 确定用户最常见情绪

## 记忆结构

系统使用的JSON记忆结构如下：

```json
{
  "version": "2.0",
  "last_updated": "ISO时间戳",
  "users": {
    "user_id": {
      "interactions": [
        {
          "timestamp": "ISO时间戳",
          "text": "用户文本",
          "emotion": "情绪标签",
          "confidence": 0.95,
          "suggestion": "给用户的建议",
          "metadata": {},
          "feedback": {
            "timestamp": "ISO时间戳",
            "rating": 5,
            "text": "用户反馈"
          }
        }
      ],
      "emotional_history": [
        {
          "timestamp": "ISO时间戳",
          "emotion": "情绪标签",
          "confidence": 0.95,
          "context": "上下文文本"
        }
      ],
      "last_active": "ISO时间戳",
      "created_at": "ISO时间戳",
      "stats": {
        "total_interactions": 10,
        "most_frequent_emotion": "happy",
        "average_feedback": 4.5
      }
    }
  }
}
``` 