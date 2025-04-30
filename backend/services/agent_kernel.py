import os
import json
from openai import AzureOpenAI
from typing import List, Dict, Any, Tuple, Optional
import asyncio
import random
from dotenv import load_dotenv
from datetime import datetime
from ..memory.context_store import ContextStore

# 加载环境变量
load_dotenv()

# 从环境变量获取Azure OpenAI配置
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

class AgentKernel:
    def __init__(self, mode="default"):
        """
        初始化 AgentKernel
        
        Args:
            mode: 运行模式 (default 或 mock)
        """
        self.mode = mode
        self.client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=subscription_key,
        )
        # 存储用户对话历史的字典
        self.conversation_history = {}
        # 初始化 ContextStore
        self.context_store = ContextStore()
    
    def analyze_emotion(self, text: str) -> Tuple[str, float]:
        """
        分析文本的情绪状态
        
        Args:
            text: 需要分析的文本
            
        Returns:
            (emotion, confidence): 情绪状态和置信度
        """
        if self.mode == "mock":
            # 模拟情绪分析
            emotions = ["P", "N", "D"]  # Positive, Neutral, Depressed
            emotion = random.choice(emotions)
            confidence = random.uniform(0.4, 0.95)
            return emotion, confidence
        else:
            # TODO: 实现实际的情绪分析逻辑
            # 这里暂时使用模拟数据
            emotions = ["P", "N", "D"]
            emotion = random.choice(emotions)
            confidence = random.uniform(0.4, 0.95)
            return emotion, confidence
    
    async def add_interaction_to_store(self, user_id: str, text: str, suggestion: str):
        """
        记录交互数据到 ContextStore
        
        Args:
            user_id: 用户ID
            text: 用户消息
            suggestion: AI回复
        """
        emotion, confidence = self.analyze_emotion(text)
        await self.context_store.add_interaction(
            user_id=user_id,
            text=text,
            emotion=emotion,
            confidence=confidence,
            suggestion=suggestion
        )
    
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户上下文信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户上下文信息
        """
        return await self.context_store.get_user_context(user_id)
    
    async def get_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取用户最近的情绪记录
        
        Args:
            user_id: 用户ID
            limit: 返回的记录数量
            
        Returns:
            最近的情绪记录列表
        """
        return await self.context_store.get_recent_emotions(user_id, limit)
    
    def get_user_health_data(self, user_id: str, emotion: Optional[str] = None, confidence: Optional[float] = None) -> Dict[str, Any]:
        """
        获取用户健康数据
        
        Args:
            user_id: 用户ID
            emotion: 用户情绪（P=积极, N=中性, D=消极）
            confidence: 情绪置信度
            
        Returns:
            用户健康数据，包含情绪状态和置信度
        """
        if emotion and confidence:
            # 使用传入的情绪数据
            return {
                "user_id": user_id,
                "status": emotion,
                "confidence": confidence
            }
        elif self.mode == "mock":
            # 模拟健康数据
            statuses = ["P", "N", "D"]  # Positive, Neutral, Depressed
            status = random.choice(statuses)
            confidence = random.uniform(0.4, 0.95)
            
            return {
                "user_id": user_id,
                "status": status,
                "confidence": confidence
            }
        else:
            # 实际环境应当调用相关API获取数据
            # 这里暂时使用模拟数据
            statuses = ["P", "N", "D"]
            status = random.choice(statuses)
            confidence = random.uniform(0.4, 0.95)
            
            return {
                "user_id": user_id,
                "status": status,
                "confidence": confidence
            }
    
    def get_user_context_from_memory(self, user_id: str, query: str = "") -> List[Dict[str, Any]]:
        """
        从记忆系统中获取用户上下文
        
        Args:
            user_id: 用户ID
            query: 用户查询
            
        Returns:
            相关记忆列表
        """
        # 获取记忆数据
        memories = self.retrieve_memory(user_id, query)
        return memories["memories"]
    
    # 模拟记忆检索API
    def retrieve_memory(self, user_id: str, query: str = "", top_k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        模拟从记忆系统检索相关记忆
        
        Args:
            user_id: 用户ID
            query: 用户查询
            top_k: 返回的记忆数量
            
        Returns:
            包含相关记忆的字典
        """
        # 模拟记忆数据
        if self.mode == "mock":
            mock_memories = {
                "memories": [
                    {
                        "summary": "User said they dislike rainy days last week",
                        "embedding_source": "2024-04-12 19:22:31 Chat content",
                        "relevance": 0.93
                    },
                    {
                        "summary": "User mentioned they want someone to be with them when they're under pressure",
                        "embedding_source": "2024-03-30",
                        "relevance": 0.89
                    },
                    {
                        "summary": "User said they've been very busy at work recently, often working overtime until late",
                        "embedding_source": "2024-04-10 20:15:45 Chat content",
                        "relevance": 0.85
                    }
                ]
            }
            return mock_memories
        else:
            # 实际环境应当调用相关API获取数据
            # 这里暂时使用模拟数据
            mock_memories = {
                "memories": [
                    {
                        "summary": "User said they dislike rainy days last week",
                        "embedding_source": "2024-04-12 19:22:31 Chat content",
                        "relevance": 0.93
                    },
                    {
                        "summary": "User mentioned they want someone to be with them when they're under pressure",
                        "embedding_source": "2024-03-30",
                        "relevance": 0.89
                    },
                    {
                        "summary": "User said they've been very busy at work recently, often working overtime until late",
                        "embedding_source": "2024-04-10 20:15:45 Chat content",
                        "relevance": 0.85
                    }
                ]
            }
            return mock_memories
    
    async def build_prompt_with_memories_and_history(self, user_id: str, query: str = "", 
                                                   emotion: Optional[str] = None, 
                                                   confidence: Optional[float] = None,
                                                   time_of_day: Optional[str] = None,
                                                   reason: Optional[str] = None,
                                                   user_context: Optional[Dict[str, Any]] = None,
                                                   recent_emotions: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, str]]:
        """
        构建包含记忆上下文和对话历史的prompt
        
        Args:
            user_id: 用户ID
            query: 用户查询
            emotion: 用户情绪状态
            confidence: 情绪置信度
            time_of_day: 一天中的时间段
            reason: 特殊原因描述
            user_context: 用户上下文信息
            recent_emotions: 最近的情绪记录
            
        Returns:
            带有记忆上下文和对话历史的消息列表
        """
        # 获取用户健康数据
        health_data = self.get_user_health_data(user_id, emotion, confidence)
        
        # 获取用户上下文
        if user_context is None:
            user_context = await self.get_user_context(user_id)
        
        # 获取最近的情绪记录
        if recent_emotions is None:
            recent_emotions = await self.get_recent_emotions(user_id)
        
        # 构建系统提示，包含记忆信息
        system_content = "You are an emotional support assistant, providing warmth and understanding. Here is some relevant information about the user to consider in your response:"
        
        # 添加用户记忆信息
        for memory in user_context.get("memories", []):
            system_content += f"\n- {memory['summary']} ({memory['embedding_source']})"
        
        # 根据健康数据调整提示
        if health_data["confidence"] > 0.6:
            status = health_data["status"]
            if status == "P":
                system_content += "\n\nThe user seems to be in a positive mood. You can be cheerful and encouraging."
            elif status == "N":
                system_content += "\n\nThe user seems to be in a neutral mood. Be empathetic and provide support."
            elif status == "D":
                system_content += "\n\nThe user may be feeling depressed. Show extra care, be supportive, and suggest professional help if necessary."
        
        # 添加时间信息
        if time_of_day:
            system_content += f"\n\nThe current time of day is: {time_of_day}."
        
        # 添加特殊原因信息
        if reason:
            system_content += f"\n\nSpecial context: {reason}"
        
        system_content += "\n\nPlease provide personalized emotional support based on these memories and conversation history. Maintain consistency and coherence as if you're old friends."
        
        # 构建消息列表，包含系统消息
        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]
        
        # 添加历史对话（如果有）
        if user_id in self.conversation_history:
            messages.extend(self.conversation_history[user_id])
        
        # 添加当前用户查询（如果有）
        if query:
            messages.append({
                "role": "user",
                "content": query
            })
        
        # 添加用户上下文信息
        if user_context:
            for key, value in user_context.items():
                if key != "memories":  # 跳过已经添加的记忆信息
                    messages.append({
                        "role": "user",
                        "content": f"{key}: {value}"
                    })
        
        # 添加最近的情绪记录
        if recent_emotions:
            for emotion in recent_emotions:
                messages.append({
                    "role": "user",
                    "content": f"Recent emotion: {emotion['emotion']} (confidence: {emotion['confidence']})"
                })
        
        return messages
    
    async def chat(self, query: str, user_id: str = "default_user", 
                  emotion: Optional[str] = None, confidence: Optional[float] = None) -> str:
        """
        处理用户查询并返回带有记忆上下文和对话历史的回复
        
        Args:
            query: 用户查询
            user_id: 用户ID
            emotion: 用户情绪状态
            confidence: 情绪置信度
            
        Returns:
            助手的回复
        """
        # 确保用户在历史记录中有条目
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # 获取用户上下文
        user_context = await self.get_user_context(user_id)
        
        # 获取最近的情绪记录
        recent_emotions = await self.get_recent_emotions(user_id)
        
        # 构建包含记忆和历史的消息
        messages = await self.build_prompt_with_memories_and_history(
            user_id=user_id, 
            query=query,
            emotion=emotion,
            confidence=confidence,
            user_context=user_context,
            recent_emotions=recent_emotions
        )
        
        # 记录发送的消息
        print(f"向模型发送的消息: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        # 使用非流式响应
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            stream=False,
            messages=messages,
            max_tokens=4096,
            temperature=0.7,
            top_p=1.0,
            model=deployment
        )
        
        # 获取响应内容
        full_response = response.choices[0].message.content
        
        # 记录交互数据
        await self.add_interaction_to_store(user_id, query, full_response)
        
        # 更新对话历史
        if query:
            self.conversation_history[user_id].append({"role": "user", "content": query})
            self.conversation_history[user_id].append({"role": "assistant", "content": full_response})
            
            # 如果对话历史太长，可以进行截断
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
        
        return full_response
    
    async def followup(self, user_id: str = "default_user", 
                     emotion: Optional[str] = None, 
                     confidence: Optional[float] = None,
                     time_of_day: Optional[str] = None,
                     reason: Optional[str] = None) -> str:
        """
        处理没有用户查询的情况，主动发起对话
        
        Args:
            user_id: 用户ID
            emotion: 用户情绪状态
            confidence: 情绪置信度
            time_of_day: 一天中的时间段
            reason: 特殊原因描述
            
        Returns:
            助手的主动回复
        """
        # 确保用户在历史记录中有条目
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # 获取用户上下文
        user_context = await self.get_user_context(user_id)
        
        # 获取最近的情绪记录
        recent_emotions = await self.get_recent_emotions(user_id)
        
        # 构建包含记忆和历史的消息
        messages = await self.build_prompt_with_memories_and_history(
            user_id=user_id,
            emotion=emotion,
            confidence=confidence,
            time_of_day=time_of_day,
            reason=reason,
            user_context=user_context,
            recent_emotions=recent_emotions
        )
        
        # 添加一个指示性提示
        followup_instruction = {
            "role": "user",
            "content": "Please initiate a conversation with me based on the context provided. Be supportive and considerate."
        }
        messages.append(followup_instruction)
        
        # 记录发送的消息
        print(f"向模型发送的消息: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        # 使用非流式响应
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            stream=False,
            messages=messages,
            max_tokens=4096,
            temperature=0.7,
            top_p=1.0,
            model=deployment
        )
        
        # 获取响应内容
        full_response = response.choices[0].message.content
        
        # 记录交互数据（主动发起对话时，text 为空）
        await self.add_interaction_to_store(user_id, "", full_response)
        
        # 更新对话历史
        self.conversation_history[user_id].append({"role": "assistant", "content": full_response})
        
        # 如果对话历史太长，可以进行截断
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
        
        return full_response
    
    def start_conversation(self, user_id: str):
        """
        开始一个新的对话，清除之前的对话历史
        
        Args:
            user_id: 用户ID
        """
        self.conversation_history[user_id] = []
        print(f"已为用户 {user_id} 开始新对话")

    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """
        获取指定用户的对话历史
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户的对话历史
        """
        if user_id in self.conversation_history:
            return self.conversation_history[user_id]
        return []


# 示例用法
if __name__ == "__main__":
    async def test_agent():
        agent = AgentKernel(mode="mock")
        user_id = "user_123"
        
        # 清除之前的对话历史，开始新对话
        agent.start_conversation(user_id)
        
        # 测试 followup（主动发起）
        print("测试 followup：")
        followup_response = await agent.followup(
            user_id=user_id,
            emotion="D",
            confidence=0.85,
            time_of_day="evening",
            reason="User seems to be sleepy and has been silent for a while"
        )
        print(f"AI主动发起: {followup_response}")
        
        # 测试 chat（回复查询）
        print("\n测试 chat：")
        chat_response = await agent.chat(
            query="I'm feeling a bit down today",
            user_id=user_id,
            emotion="N",
            confidence=0.78
        )
        print(f"AI回复: {chat_response}")
    
    asyncio.run(test_agent())
