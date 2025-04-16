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

4. **Emotion Analysis**

   ```
   [User Text] ---> [Emotion Analysis Tool] ---> [Detected Emotion + Confidence]
   ```

5. **Context Retrieval**

   ```
   [userId] ---> [Memory System] ---> [User History + Preferences]
   ```

6. **Suggestion Generation**

   ```
   [Emotion] + [Health Data] + [User Profile] ---> [Template] ---> [Personalized Suggestion]
   ```

7. **Response to Frontend**

   ```
   [Suggestion + Emotion Label] ---> [iOS App] ---> [User Interface]
   ```

8. **Memory Update**
   ```
   [Interaction Data] ---> [Memory Store] ---> [Updated Context]
   ```

## Key Components Interaction

```
+-------------+       +------------------+       +-----------------+
|             |       |                  |       |                 |
| ContentView | <---> | AgentClient API  | <---> | Agent Router    |
|             |       |                  |       |                 |
+-------------+       +------------------+       +-----------------+
       ^                       ^                          ^
       |                       |                          |
       v                       v                          v
+-------------+       +------------------+       +-----------------+
|             |       |                  |       |                 |
|HealthManager| <---> | Health Data API  | <---> | Agent Kernel    |
|             |       |                  |       |                 |
+-------------+       +------------------+       +-----------------+
                                                        ^
                                                        |
                                                        v
                                                 +-----------------+
                                                 |                 |
                                                 | Tool Registry   |
                                                 |                 |
                                                 +-----------------+
                                                        ^
                                                        |
                                                        v
                                              +---------------------+
                                              |                     |
                                              | Individual Tools    |
                                              |                     |
                                              +---------------------+
```
