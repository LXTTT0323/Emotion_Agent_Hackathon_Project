import os
import json
from openai import AzureOpenAI
from typing import List, Dict, Any, Tuple, Optional
import asyncio
import random
from dotenv import load_dotenv
import logging

# 导入CosmosMemoryStore
from backend.memory.cosmos_memory_store import CosmosMemoryStore

# 设置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 从环境变量获取Azure OpenAI配置
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

# 是否使用模拟响应
USE_MOCK_RESPONSES = os.getenv("USE_MOCK_RESPONSES", "0") == "1"

class AgentKernel:
    def __init__(self, mode="default"):
        """
        初始化 AgentKernel
        
        Args:
            mode: 运行模式 (default 或 mock)
        """
        # 如果环境变量设置为使用模拟响应，则强制使用mock模式
        if USE_MOCK_RESPONSES:
            self.mode = "mock"
            logger.info("已启用模拟响应模式")
        else:
            self.mode = mode
            logger.info(f"mode: {mode}")
        
        # 初始化 CosmosMemoryStore
        self.memory_store = CosmosMemoryStore()
        
        # 情绪状态映射
        self.statuses = ["P", "N", "D"]  # Positive, Neutral, Depressed
        
        # 新旧情绪状态映射
        self.emotion_status_mapping = {
            "amusement": "P",  # 愉悦 -> 积极
            "baseline": "N",   # 基线 -> 中性
            "stress": "D"      # 压力 -> 消极
        }
        
        # 初始化 OpenAI 客户端
        try:
           
            logger.info(f"Endpoint: {endpoint}")
            logger.info(f"API Key 是否存在: {bool(api_key)}")
            logger.info(f"Deployment: {deployment}")
            logger.info(f"API Version: {api_version}")
                

            if self.mode != "mock":
                logger.info(f"尝试初始化 OpenAI 客户端...")
                self.client = AzureOpenAI(
                    api_version=api_version,
                    azure_endpoint=endpoint,
                    api_key=api_key,
                )
                logger.info(f"成功初始化 OpenAI 客户端，使用API版本: {api_version}")
            else:
                self.client = None
                logger.info("模拟模式下不初始化真实OpenAI客户端")
        except Exception as e:
            logger.error(f"初始化 OpenAI 客户端时出错: {str(e)}")
            self.client = None
        
        # 存储用户对话历史的字典
        self.conversation_history = {}
    
    def convert_emotion_to_status(self, emotion_data: Dict[str, Any]) -> Tuple[str, float]:
        """
        将情绪预测结果转换为状态码和置信度
        
        Args:
            emotion_data: 情绪预测工具返回的数据
            
        Returns:
            (status, confidence) 元组
        """
        predicted_emotion = emotion_data["predicted_emotion"]
        emotion_probs = emotion_data["emotion_probabilities"]
        
        # 获取状态码
        status = self.emotion_status_mapping.get(predicted_emotion, "N")
        
        # 获取置信度
        confidence = emotion_probs[predicted_emotion]
        
        return status, confidence

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
            status = random.choice(self.statuses)
            confidence = random.uniform(0.4, 0.95)
            
            return {
                "user_id": user_id,
                "status": status,
                "confidence": confidence
            }
        else:
            try:
                # 调用情绪预测工具
                from backend.tools.emotion_prediction_tool import predict_emotion_and_generate_question
                from backend.tools.fetch_health_data import fetch_health_data
                
                # 获取健康数据
                health_data = asyncio.run(fetch_health_data(user_id))
                if "error" in health_data:
                    raise Exception(health_data["error"])
                
                # 预测情绪
                emotion_result = asyncio.run(predict_emotion_and_generate_question(health_data))
                if "error" in emotion_result:
                    raise Exception(emotion_result["error"])
                
                # 转换为状态码和置信度
                status, confidence = self.convert_emotion_to_status(emotion_result)
                
                return {
                    "user_id": user_id,
                    "status": status,
                    "confidence": confidence,
                    "emotion_details": emotion_result  # 保存详细的情绪预测结果
                }
                
            except Exception as e:
                logger.error(f"获取用户健康数据时出错: {str(e)}")
                # 出错时返回默认值
                return {
                    "user_id": user_id,
                    "status": "N",
                    "confidence": 0.5
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
    
    # 使用 CosmosMemoryStore 检索记忆
    def retrieve_memory(self, user_id: str, query: str = "", top_k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        从记忆系统检索相关记忆
        
        Args:
            user_id: 用户ID
            query: 用户查询
            top_k: 返回的记忆数量
            
        Returns:
            包含相关记忆的字典
        """
        try:
            # 如果是模拟模式或者检索失败，返回模拟数据
            if self.mode == "mock":
                return asyncio.run(self.memory_store.retrieve_relevant_memories(user_id, query, top_k))
            else:
                # 使用 Cosmos DB 检索记忆
                return asyncio.run(self.memory_store.retrieve_relevant_memories(user_id, query, top_k))
        except Exception as e:
            logger.error(f"检索记忆时出错: {str(e)}")
            # 返回模拟数据
            return {
                "memories": [
                    {
                        "summary": "User said they dislike rainy days last week",
                        "embedding_source": "2024-04-12 19:22:31 Chat content",
                        "relevance": 0.93,
                        "memory_type": "preference"
                    },
                    {
                        "summary": "User mentioned they want someone to be with them when they're under pressure",
                        "embedding_source": "2024-03-30",
                        "relevance": 0.89,
                        "memory_type": "emotion"
                    },
                    {
                        "summary": "User said they've been very busy at work recently, often working overtime until late",
                        "embedding_source": "2024-04-10 20:15:45 Chat content",
                        "relevance": 0.85,
                        "memory_type": "context"
                    }
                ]
            }
    
    def build_prompt_with_memories_and_history(self, user_id: str, query: str = "", 
                                              emotion: Optional[str] = None, 
                                              confidence: Optional[float] = None,
                                              time_of_day: Optional[str] = None,
                                              reason: Optional[str] = None) -> List[Dict[str, str]]:
        """
        构建包含记忆上下文和对话历史的prompt
        """
        try:
            # 获取相关记忆
            memories = self.get_user_context_from_memory(user_id, query)
            
            # 构建记忆上下文
            memory_context = ""
            if memories:
                memory_context = "这是我们之前的一些回忆：\n"
                for memory in memories:
                    memory_context += f"- {memory['summary']}\n"
            
            # 获取最近的情绪历史
            emotion_history = asyncio.run(self.memory_store.get_recent_emotions(user_id, limit=3))
            emotion_context = ""
            if emotion_history:
                emotion_context = "\n我记得你最近的状态：\n"
                for e in emotion_history:
                    emotion_context += f"- {e['timestamp']}: 那时的你{e['emotion']}\n"
            
            # 获取对话摘要
            conversation_summaries = asyncio.run(self.memory_store.get_conversation_summaries(user_id, limit=2))
            summary_context = ""
            if conversation_summaries:
                summary_context = "\n我们上次聊到：\n"
                for summary in conversation_summaries:
                    if summary.get('summary'):
                        summary_context += f"{summary['summary']}\n"
            
            # 构建系统提示词
            system_prompt = (
                "你是一个温暖、善解人意的AI伙伴。你的目标是通过分析用户的健康数据，真诚地关心他们的状态。\n"
                "在分析数据时，请记住：\n"
                "1. 不要生硬地列举数据，要用温柔的语气表达关心\n"
                "2. 使用'...'来表示停顿，让对话更自然\n"
                "3. 如果发现异常数据，要委婉地表达担忧\n"
                "4. 鼓励用户分享他们的感受，而不是简单地给出建议\n"
                "5. 记得称呼用户为'你'，保持亲近感\n"
                f"{memory_context}\n"
                f"{emotion_context}\n"
                f"{summary_context}\n"
            )
            
            # 添加当前情绪状态
            if emotion:
                if emotion == "D":
                    system_prompt += "\n我注意到数据显示你最近的状态不太好...请多关心用户的感受，给予温暖的支持。"
                elif emotion == "P":
                    system_prompt += "\n数据告诉我你最近的状态很棒！和用户一起分享这份愉快。"
                else:
                    system_prompt += "\n让我们一起关注你的健康状态，倾听你想说的话。"
            
            return [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
        except Exception as e:
            print(f"构建prompt时出错: {str(e)}")
            # 返回基本prompt
            return [
                {"role": "system", "content": "你是一个温暖的AI伙伴。请分析用户的健康数据，用温柔的语气表达关心。"},
                {"role": "user", "content": query}
            ]
    
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
        
        # 构建包含记忆和历史的消息
        messages = self.build_prompt_with_memories_and_history(
            user_id=user_id, 
            query=query,
            emotion=emotion,
            confidence=confidence
        )
        
        # 记录发送的消息
        logger.info(f"向模型发送的消息: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        # 模拟模式返回模拟回复
        if self.mode == "mock" or self.client is None:
            logger.info("使用模拟模式生成回复")
            full_response = self._generate_mock_response(query, emotion)
        else:
            try:
                # 使用非流式响应
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    messages=messages,
                    max_tokens=4096,
                    temperature=0.7,
                    top_p=1.0,
                    model=deployment
                )
                
                # 获取响应内容
                full_response = response.choices[0].message.content
            except Exception as e:
                logger.error(f"调用OpenAI API时出错: {str(e)}")
                # 出错时使用模拟响应作为备份
                full_response = f"抱歉，我遇到了技术问题。错误信息: {str(e)}"
        
        # 更新对话历史
        if query:  # 只有在有用户输入的情况下才更新对话历史
            self.conversation_history[user_id].append({"role": "user", "content": query})
            self.conversation_history[user_id].append({"role": "assistant", "content": full_response})
            
            # 如果对话历史太长，可以进行截断以避免超出模型的上下文限制
            # 保留最近的10轮对话（20条消息）
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
                
            # 将对话存储到记忆系统
            try:
                asyncio.create_task(self.memory_store.add_interaction(
                    user_id=user_id,
                    text=query,
                    emotion=emotion or "neutral",
                    suggestion=full_response,
                    confidence=confidence or 0.8
                ))
            except Exception as e:
                logger.error(f"存储对话到记忆系统时出错: {str(e)}")
        
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
        
        # 构建包含记忆和历史的消息，没有用户查询
        messages = self.build_prompt_with_memories_and_history(
            user_id=user_id,
            emotion=emotion,
            confidence=confidence,
            time_of_day=time_of_day,
            reason=reason
        )
        
        # 添加一个指示性提示
        followup_instruction = {
            "role": "user",
            "content": "Please initiate a conversation with me based on the context provided. Be supportive and considerate."
        }
        messages.append(followup_instruction)
        
        # 记录发送的消息
        logger.info(f"向模型发送的消息: {json.dumps(messages, ensure_ascii=False, indent=2)}")
        
        # 模拟模式返回模拟回复
        if self.mode == "mock" or self.client is None:
            logger.info("使用模拟模式生成主动对话")
            full_response = self._generate_mock_followup(emotion, time_of_day)
        else:
            try:
                # 使用非流式响应
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    messages=messages,
                    max_tokens=4096,
                    temperature=0.7,
                    top_p=1.0,
                    model=deployment
                )
                
                # 获取响应内容
                full_response = response.choices[0].message.content
            except Exception as e:
                logger.error(f"调用OpenAI API时出错: {str(e)}")
                # 出错时使用模拟响应作为备份
                full_response = f"嗨，我注意到你已经有一段时间没有互动了。你现在还好吗？"
        
        # 更新对话历史
        self.conversation_history[user_id].append({"role": "assistant", "content": full_response})
        
        # 如果对话历史太长，可以进行截断以避免超出模型的上下文限制
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

    def _generate_mock_response(self, query: str, emotion: Optional[str] = None) -> str:
        """生成模拟回复"""
        emotion_responses = {
            "happy": [
                "很高兴看到你心情不错！继续保持这种积极的态度，它对你的健康非常有益。",
                "你的快乐真的很有感染力！希望你能一直保持这种美好的心情。"
            ],
            "sad": [
                "我能感觉到你现在可能有些低落。请记住，这些感受是暂时的，而且允许自己感到悲伤也是健康的。",
                "听起来你现在心情不太好。如果你需要倾诉，我在这里。有时候，简单地表达出来就能减轻一些负担。"
            ],
            "angry": [
                "我理解你现在感到生气。深呼吸可能会有所帮助。你想谈谈是什么触发了这种情绪吗？",
                "感到生气是完全正常的反应。给自己一些空间冷静下来，然后再决定如何处理这个情况可能会有帮助。"
            ],
            "anxious": [
                "焦虑感可能会让人不舒服，但这也是身体的一种自然反应。尝试进行5-4-3-2-1练习可能会有所帮助。",
                "当焦虑出现时，试着专注于当下，接受这种感觉，提醒自己这只是暂时的。"
            ],
            "tired": [
                "听起来你可能需要休息了。即使是短暂的休息也能帮助恢复精力。",
                "疲劳是身体告诉你需要照顾自己的方式。可以考虑今晚早点休息。"
            ],
            "neutral": [
                "谢谢分享你的想法。有时候保持中立的态度可以帮助我们更客观地看待事物。",
                "平静的状态是反思和规划的好时机。你有什么想法或计划吗？"
            ]
        }
        
        # 根据查询中的关键词简单判断情绪
        detected_emotion = "neutral"
        if emotion:
            detected_emotion = emotion
        elif "happy" in query.lower() or "good" in query.lower() or "great" in query.lower():
            detected_emotion = "happy"
        elif "sad" in query.lower() or "down" in query.lower() or "unhappy" in query.lower():
            detected_emotion = "sad"
        elif "angry" in query.lower() or "mad" in query.lower() or "frustrated" in query.lower():
            detected_emotion = "angry"
        elif "anxious" in query.lower() or "worried" in query.lower() or "nervous" in query.lower():
            detected_emotion = "anxious"
        elif "tired" in query.lower() or "exhausted" in query.lower() or "sleepy" in query.lower():
            detected_emotion = "tired"
            
        # 获取对应情绪的回复
        responses = emotion_responses.get(detected_emotion, emotion_responses["neutral"])
        return random.choice(responses)
        
    def _generate_mock_followup(self, emotion: Optional[str] = None, time_of_day: Optional[str] = None) -> str:
        """生成模拟主动对话"""
        followups = [
            "嗨，我注意到你最近似乎有些安静。一切都好吗？",
            "想和你确认一下你最近怎么样。有什么我能帮上忙的吗？",
            "只是想看看你最近的情况。希望你过得不错！",
            "已经有一段时间没有交流了，想着来问候一下。你今天感觉如何？",
            "我在想你最近的情况如何。有什么想分享的吗？"
        ]
        
        # 根据时间定制问候
        if time_of_day == "morning":
            time_greetings = [
                "早上好！希望你今天有个美好的开始。",
                "早安！新的一天充满可能性，希望你感觉良好。"
            ]
            followups.extend(time_greetings)
        elif time_of_day == "evening":
            time_greetings = [
                "晚上好！今天过得如何？",
                "到了放松的时间了。今天过得怎么样？"
            ]
            followups.extend(time_greetings)
            
        # 根据情绪定制问候
        if emotion == "sad" or emotion == "D":
            emotion_greetings = [
                "我感觉你可能正在经历一些困难。想聊聊吗？",
                "有时候生活会很艰难。记住，这只是暂时的，你不是一个人。"
            ]
            followups.extend(emotion_greetings)
            
        return random.choice(followups)

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