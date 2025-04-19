# 情感 AI 助手 API 使用文档

本文档介绍如何使用情感 AI 助手的 API，特别是情感支持和长对话功能。

## 基本信息

- **Base URL**: `http://localhost:8000`（本地开发环境）
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **API 演示页面**: `http://localhost:8000/static/demo.html`

## API 端点

### 1. AI 主动发起对话 (Followup)

**端点**: `POST /agent/followup`

**功能**: 当用户没有主动查询时，AI 根据上下文主动发起对话。

**请求体**:

```json
{
  "user_id": "user123",
  "emotion": "D",
  "confidence": 0.91,
  "time_of_day": "evening",
  "reason": "User seems to be sleepy and hasn't responded for a while"
}
```

**参数说明**:

- `user_id`: 用户 ID，用于识别用户及其对话历史
- `emotion`: 用户情绪状态 (P=积极, N=中性, D=消极)
- `confidence`: 情绪检测的置信度 (0.0 - 1.0)
- `time_of_day`: 一天中的时间段 (morning, afternoon, evening, night)
- `reason`: 特殊原因描述，直接作为提示输入

**响应**:

```json
{
  "response": "Hey there, I noticed you've been quiet for a while. It's getting late in the evening and you seem tired. Is everything okay? I'm here if you need to talk about anything that's on your mind."
}
```

### 2. 用户查询对话 (Chat)

**端点**: `POST /agent/chat`

**功能**: 处理用户的主动查询，AI 根据查询、历史对话和用户情绪提供个性化回复。

**请求体**:

```json
{
  "message": "I'm feeling a bit down today",
  "user_id": "user123",
  "emotion": "N",
  "confidence": 0.78
}
```

**参数说明**:

- `message`: 用户的查询消息
- `user_id`: 用户 ID，用于识别用户及其对话历史
- `emotion`: 用户情绪状态 (P=积极, N=中性, D=消极) [可选]
- `confidence`: 情绪检测的置信度 (0.0 - 1.0) [可选]

**响应**:

```json
{
  "response": "I'm sorry to hear you're feeling down today. It's completely understandable to have those moments. Would you like to talk about what's bothering you? Or maybe we could think of something that might help lift your spirits a bit? I remember you mentioned before that you enjoy taking walks when you're feeling stressed - would something like that help today?"
}
```

### 3. 开始新对话 (Start Conversation)

**端点**: `POST /agent/start_conversation`

**功能**: 清除之前的对话历史，开始一个新的对话。

**请求体**:

```json
{
  "user_id": "user123"
}
```

**响应**:

```json
{
  "success": true,
  "message": "已为用户 user123 开始新对话"
}
```

### 4. 获取对话历史 (Get History)

**端点**: `GET /agent/history/{user_id}`

**功能**: 获取指定用户的对话历史。

**响应**:

```json
{
  "history": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    },
    {
      "role": "assistant",
      "content": "I'm doing well, thank you for asking! How are you feeling today?"
    }
  ]
}
```

### 5. 检索用户记忆 (Retrieve Memory)

**端点**: `POST /agent/memory/retrieve`

**功能**: 检索与用户相关的记忆。

**请求体**:

```json
{
  "user_id": "user123",
  "query": "work stress",
  "top_k": 3
}
```

**响应**:

```json
{
  "memories": [
    {
      "summary": "User said they've been very busy at work recently, often working overtime until late",
      "embedding_source": "2024-04-10 20:15:45 Chat content",
      "relevance": 0.93
    },
    {
      "summary": "User mentioned they want someone to be with them when they're under pressure",
      "embedding_source": "2024-03-30",
      "relevance": 0.89
    }
  ]
}
```

## 使用模式

API 支持两种主要的运行模式：

1. **默认模式 (Default)**:

   - 使用真实的 Azure OpenAI 服务
   - 调用真实的分析工具和数据获取工具
   - 需要配置正确的环境变量（API 密钥等）

2. **模拟模式 (Mock)**:
   - 使用预定义的示例数据
   - 不需要实际的 API 调用（除了 AI 模型调用）
   - 适合开发和测试时使用

## 示例代码

### JavaScript (前端)

```javascript
// 与AI对话示例
async function chatWithAgent() {
  try {
    const response = await fetch("http://localhost:8000/agent/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "I'm feeling a bit stressed about work",
        user_id: "user123",
        emotion: "N",
        confidence: 0.78,
      }),
    });

    const data = await response.json();
    return data.response; // 返回AI回复
  } catch (error) {
    console.error("Error:", error);
    return "";
  }
}

// AI主动发起对话示例
async function getFollowupFromAgent() {
  try {
    const response = await fetch("http://localhost:8000/agent/followup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: "user123",
        emotion: "D",
        confidence: 0.85,
        time_of_day: "evening",
        reason: "User seems to be sleepy and hasn't responded for a while",
      }),
    });

    const data = await response.json();
    return data.response; // 返回AI回复
  } catch (error) {
    console.error("Error:", error);
    return "";
  }
}
```

### Python (后端)

```python
import requests
import json

# 对话示例
def chat_with_agent():
    url = "http://localhost:8000/agent/chat"
    payload = {
        "message": "I'm feeling a bit down today",
        "user_id": "user123",
        "emotion": "N",
        "confidence": 0.78
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# AI主动发起对话示例
def get_followup():
    url = "http://localhost:8000/agent/followup"
    payload = {
        "user_id": "user123",
        "emotion": "D",
        "confidence": 0.91,
        "time_of_day": "evening",
        "reason": "User seems tired after a long day at work"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

## 添加到 iOS 应用

要在 iOS 应用中集成这些 API，您可以使用 Swift 的 URLSession：

```swift
import Foundation

class EmotionAPI {
    private let baseURL = "http://localhost:8000"

    func chatWithAgent(message: String, userId: String, emotion: String? = nil, confidence: Float? = nil, completion: @escaping (String?, Error?) -> Void) {
        let url = URL(string: "\(baseURL)/agent/chat")!

        var parameters: [String: Any] = [
            "message": message,
            "user_id": userId
        ]

        if let emotion = emotion {
            parameters["emotion"] = emotion
        }

        if let confidence = confidence {
            parameters["confidence"] = confidence
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: parameters)

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(nil, error)
                return
            }

            guard let data = data else {
                completion(nil, NSError(domain: "EmotionAPI", code: 1, userInfo: [NSLocalizedDescriptionKey: "No data"]))
                return
            }

            do {
                if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                   let response = json["response"] as? String {
                    completion(response, nil)
                } else {
                    completion(nil, NSError(domain: "EmotionAPI", code: 2, userInfo: [NSLocalizedDescriptionKey: "Invalid response format"]))
                }
            } catch {
                completion(nil, error)
            }
        }.resume()
    }
}
```
