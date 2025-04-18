# 情感 AI 助手 API 使用文档

本文档介绍如何使用情感 AI 助手的 API，特别是新添加的男朋友模式和安慰功能。

## 基本信息

- **Base URL**: `http://localhost:8000`（本地开发环境）
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **API 演示页面**: `http://localhost:8000/static/demo.html`

## API 端点

### 1. 分析用户输入 (Analyze)

**端点**: `POST /agent/analyze`

**功能**: 分析用户文本输入，识别情绪，生成建议。

**请求体**:

```json
{
  "user_id": "user123",
  "text": "I'm feeling really down today, nothing seems to be going right.",
  "health_data": null
}
```

**响应**:

```json
{
  "suggestion": "I understand you're feeling down today. It's important to acknowledge these feelings. Consider taking some time for self-care, like a short walk or talking to a friend.",
  "emotion": "sadness",
  "confidence": 0.91
}
```

### 2. 生成回复 (Generate Response)

**端点**: `POST /agent/generate_response`

**功能**: 根据指定的提示类型和上下文生成 AI 回复。

**查询参数**:

- `use_mock` (boolean): 是否使用模拟数据（默认为 false）

**请求体**:

```json
{
  "user_id": "user123",
  "prompt_type": "boyfriend",
  "emotion": "sadness",
  "confidence": 0.91,
  "time_of_day": "evening",
  "special_instruction": "User hasn't responded for a while",
  "send_multiple": false
}
```

**响应**:

```json
{
  "response": "Hey sweetheart, I noticed you've been feeling a bit down today. I wish I could be there to give you a hug. Just know that whatever you're going through, you don't have to face it alone. I'm here for you. ❤️"
}
```

### 3. 安慰消息 (Comfort)

**端点**: `POST /agent/comfort`

**功能**: 生成连续的安慰消息（通常是两条），特别适用于男朋友模式。

**查询参数**:

- `use_mock` (boolean): 是否使用模拟数据（默认为 false）

**请求体**:

```json
{
  "user_id": "user123",
  "prompt_type": "boyfriend",
  "emotion": "sadness",
  "confidence": 0.91
}
```

**响应**:

```json
{
  "messages": [
    "Hey sweetheart, I noticed you're feeling a bit down tonight. I wish I could be there to give you a hug. Just know that whatever you're going through, you don't have to face it alone. ❤️",
    "I'm thinking about you and wondering if there's anything I can do to brighten your evening? Maybe we could chat about your favorite book or I could send you some music that might lift your spirits. I'm here for you, always."
  ]
}
```

### 4. 模拟安慰消息 (Mock Comfort)

**端点**: `GET /agent/mock_comfort/{user_id}`

**功能**: 获取预设的示例安慰消息，用于前端开发和测试。

**响应**:

```json
{
  "messages": [
    "Hey sweetheart, I noticed you're feeling a bit down tonight. I wish I could be there to give you a hug. Just know that whatever you're going through, you don't have to face it alone. ❤️",
    "I'm thinking about you and wondering if there's anything I can do to brighten your evening? Maybe we could chat about your favorite book or I could send you some music that might lift your spirits. I'm here for you, always."
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
   - 不需要实际的 API 调用
   - 适合开发和测试时使用

## 示例代码

### JavaScript (前端)

```javascript
// 获取安慰消息示例
async function getComfortMessages() {
  try {
    const response = await fetch("http://localhost:8000/agent/comfort", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: "user123",
        prompt_type: "boyfriend",
        emotion: "sadness",
        confidence: 0.91,
      }),
    });

    const data = await response.json();
    return data.messages; // 返回消息数组
  } catch (error) {
    console.error("Error:", error);
    return [];
  }
}
```

### Python (后端)

```python
import requests
import json

# 生成回复示例
def generate_response():
    url = "http://localhost:8000/agent/generate_response"
    payload = {
        "user_id": "user123",
        "prompt_type": "boyfriend",
        "emotion": "sadness",
        "confidence": 0.91,
        "time_of_day": "evening"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

## 添加到 iOS 应用

要在 iOS 应用中集成这些 API，您可以使用 Swift 的 URLSession 或第三方库如 Alamofire：

```swift
import Foundation

class EmotionAPI {
    private let baseURL = "http://localhost:8000"

    func getComfortMessages(userId: String, completion: @escaping ([String]?, Error?) -> Void) {
        let url = URL(string: "\(baseURL)/agent/mock_comfort/\(userId)")!

        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(nil, error)
                return
            }

            guard let data = data else {
                completion(nil, NSError(domain: "EmotionAPI", code: 1, userInfo: [NSLocalizedDescriptionKey: "No data"]))
                return
            }

            do {
                let decoder = JSONDecoder()
                let result = try decoder.decode(ComfortResponse.self, from: data)
                completion(result.messages, nil)
            } catch {
                completion(nil, error)
            }
        }.resume()
    }
}

struct ComfortResponse: Decodable {
    let messages: [String]
}
```
