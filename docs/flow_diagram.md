# Emotion Agent - Flow Diagram

## System Architecture and Data Flow

```
+------------------+     +-----------------+     +-------------------+
|                  |     |                 |     |                   |
|  iOS App (Swift) | --> | Backend (FastAPI) --> | Semantic Kernel   |
|                  |     |                 |     |                   |
+------------------+     +-----------------+     +-------------------+
        |                        |                        |
        v                        v                        v
+------------------+     +-----------------+     +-------------------+
|                  |     |                 |     |                   |
|  Apple HealthKit | --> | Memory/Context  | <-- | Tools & Plugins   |
|                  |     |                 |     |                   |
+------------------+     +-----------------+     +-------------------+
```

## Updated Architecture with Semantic Kernel Integration

```
+------------------+     +-----------------+     +-------------------+
|                  |     |                 |     |                   |
|  iOS App (Swift) | --> | Backend (FastAPI) --> | Agent Kernel     |
|                  |     |                 |     |                   |
+------------------+     +-----------------+     +-------------------+
        |                        |                    |       |
        v                        v                    |       |
+------------------+     +-----------------+          |       |
|                  |     |                 |          v       v
|  Apple HealthKit | --> | Memory System   |    +----------+  +----------+
|                  |     |                 |    |          |  |          |
+------------------+     +-----------------+    | Kernel   |  | Prompt   |
                               |                | Service  |  | Service  |
                               v                |          |  |          |
                         +-----------------+    +----------+  +----------+
                         |                 |          |       |
                         | Tool Registry   | <--------+       |
                         |                 |                  |
                         +-----------------+                  v
                                 |                     +----------+
                                 v                     |          |
                         +-----------------+           | AI       |
                         |                 |           | Config   |
                         | Analysis Tools  |           |          |
                         |                 |           +----------+
                         +-----------------+
```

## Data Flow Sequence

1. **User Input**
   ```
   [User] ---> [Text Input] ---> [iOS App]
   ```

2. **Health Data Collection**
   ```
   [Apple Watch] ---> [HealthKit] ---> [iOS App]
   ```

3. **Request to Backend**
   ```
   [iOS App] ---> { userId, text, healthData } ---> [FastAPI]
   ```

4. **Agent Kernel Processing**
   ```
   [Request] ---> [Agent Kernel] ---> [Emotion Analysis] ---> [Health Context] ---> [User Profile]
   ```

5. **Semantic Kernel Operation**
   ```
   [Analysis Results] ---> [Kernel Service] ---> [AI Service] ---> [Language Model] ---> [Response]
   ```

6. **Context Retrieval and Update**
   ```
   [Memory System] <--- [Get Recent Emotions] --- [Agent Kernel]
                    <--- [Store Interaction] ---- [Agent Kernel]
   ```

7. **Response to Frontend**
   ```
   [Generated Response] ---> [iOS App] ---> [User Interface]
   ```

## Semantic Kernel Components Interaction

```
+-------------+       +------------------+       +-----------------+
|             |       |                  |       |                 |
| AgentKernel | <---> | KernelService    | <---> | OpenAI API      |
|             |       |                  |       |                 |
+-------------+       +------------------+       +-----------------+
       ^                       ^                          ^
       |                       |                          |
       v                       v                          v
+-------------+       +------------------+       +-----------------+
|             |       |                  |       |                 |
| ToolRegistry| <---> | PromptService    | <---> | AIConfig        |
|             |       |                  |       |                 |
+-------------+       +------------------+       +-----------------+
       ^                       ^                          
       |                       |                          
       v                       v                          
+-------------+       +------------------+       
|             |       |                  |       
| Analysis    | <---> | Memory System    |       
| Tools       |       |                  |       
+-------------+       +------------------+       
```

## Environment and Configuration Flow

```
+---------------+     +----------------+     +-------------------+
|               |     |                |     |                   |
| .env File     | --> | AIConfig       | --> | Kernel Service    |
|               |     |                |     |                   |
+---------------+     +----------------+     +-------------------+
       |                     |                        |
       |                     v                        v
       |              +----------------+     +-------------------+
       |              |                |     |                   |
       +------------> | Logging Config | --> | Application       |
                      |                |     |                   |
                      +----------------+     +-------------------+
```

## Key API Endpoints

```
/agent/analyze (POST)
  |
  +---> AgentKernel.analyze()
          |
          +---> analyze_emotion()
          |
          +---> fetch_health_data()
          |
          +---> get_user_profile()
          |
          +---> get_recent_emotions()
          |
          +---> KernelService.execute_function()
          |
          +---> add_interaction()
``` 