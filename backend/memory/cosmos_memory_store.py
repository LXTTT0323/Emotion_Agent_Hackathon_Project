import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from azure.cosmos import CosmosClient, PartitionKey, exceptions

class CosmosMemoryStore:
    """
    使用 Azure Cosmos DB 管理情感代理的记忆系统。
    """
    
    def __init__(self):
        # 从环境变量获取 Cosmos DB 连接信息
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.key = os.getenv("COSMOS_KEY")
        self.database_name = os.getenv("COSMOS_DATABASE", "emotion_agent_db")
        
        # 初始化日志
        self.logger = logging.getLogger(__name__)
        
        # 检查环境变量是否存在
        if not self.endpoint or not self.key:
            self.logger.warning("Cosmos DB 环境变量未设置，将使用本地文件存储")
            self.client = None
            return
            
        try:
            # 初始化 Cosmos 客户端
            self.client = CosmosClient(self.endpoint, credential=self.key)
            self.database = self.client.get_database_client(self.database_name)
            
            # 获取容器引用
            self.profile_container = self.database.get_container_client("user_profiles")
            self.interaction_container = self.database.get_container_client("interactions")
            self.emotion_container = self.database.get_container_client("emotion_history")
            self.embedding_container = self.database.get_container_client("memory_embeddings")
            self.conversation_container = self.database.get_container_client("conversations")
            
            self.logger.info("成功连接到 Cosmos DB")
        except Exception as e:
            self.logger.error(f"连接 Cosmos DB 时出错: {str(e)}")
            self.client = None
        
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户配置文件"""
        try:
            if not self.client:
                return self._get_local_user_profile(user_id)
                
            query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
            items = list(self.profile_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if items:
                return items[0]
            else:
                # 如果用户不存在，创建新的用户配置文件
                profile = self._create_default_profile(user_id)
                return profile
        except Exception as e:
            self.logger.error(f"获取用户配置文件时出错: {str(e)}")
            return self._get_local_user_profile(user_id)
    
    async def add_interaction(self, user_id: str, text: str, emotion: str, 
                             suggestion: str, confidence: float = 0.8,
                             metadata: Dict[str, Any] = None) -> str:
        """记录新的用户交互"""
        timestamp = datetime.now().isoformat()
        interaction_id = f"int_{int(datetime.now().timestamp())}"
        
        # 创建交互文档
        interaction = {
            "id": interaction_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "text": text,
            "emotion": emotion,
            "confidence": confidence,
            "suggestion": suggestion,
            "metadata": metadata or {}
        }
        
        try:
            if not self.client:
                self._add_local_interaction(user_id, interaction)
                return interaction_id
                
            # 保存到 Cosmos DB
            self.interaction_container.create_item(body=interaction)
            
            # 同时保存到情绪历史
            emotion_id = f"emo_{int(datetime.now().timestamp())}"
            emotion_record = {
                "id": emotion_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "emotion": emotion,
                "confidence": confidence,
                "context_keywords": self._extract_keywords(text)
            }
            self.emotion_container.create_item(body=emotion_record)
            
            # 创建并保存嵌入
            await self._create_and_store_embedding(
                user_id, interaction_id, text, emotion, timestamp
            )
            
            return interaction_id
        except Exception as e:
            self.logger.error(f"添加交互记录时出错: {str(e)}")
            self._add_local_interaction(user_id, interaction)
            return interaction_id
        
    async def get_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取用户最近的情绪记录"""
        try:
            if not self.client:
                return self._get_local_recent_emotions(user_id, limit)
                
            query = f"""
                SELECT TOP {limit} * FROM c 
                WHERE c.user_id = '{user_id}' 
                ORDER BY c.timestamp DESC
            """
            
            items = list(self.emotion_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            return items
        except Exception as e:
            self.logger.error(f"获取最近情绪记录时出错: {str(e)}")
            return self._get_local_recent_emotions(user_id, limit)
    
    async def retrieve_relevant_memories(self, user_id: str, query: str, 
                                       top_k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """检索与查询相关的记忆"""
        try:
            if not self.client:
                return self._get_mock_memories()
                
            # 为查询生成嵌入向量 (在实际实现中)
            # query_embedding = await self._generate_embedding(query)
            
            # 使用简单的关键词匹配作为临时方案
            keywords = self._extract_keywords(query)
            keyword_conditions = " OR ".join([f"ARRAY_CONTAINS(c.keywords, '{kw}')" for kw in keywords])
            
            query_str = f"""
                SELECT TOP {top_k} c.id, c.user_id, c.timestamp, c.summary, 
                       c.source_type, c.source_id, c.memory_type  
                FROM c 
                WHERE c.user_id = '{user_id}' AND ({keyword_conditions})
                ORDER BY c.timestamp DESC
            """
            
            items = list(self.embedding_container.query_items(
                query=query_str,
                enable_cross_partition_query=True
            ))
            
            # 如果没有匹配项，返回最近的记忆
            if not items:
                recent_query = f"""
                    SELECT TOP {top_k} c.id, c.user_id, c.timestamp, c.summary, 
                           c.source_type, c.source_id, c.memory_type
                    FROM c 
                    WHERE c.user_id = '{user_id}'
                    ORDER BY c.timestamp DESC
                """
                items = list(self.embedding_container.query_items(
                    query=recent_query,
                    enable_cross_partition_query=True
                ))
            
            # 转换为客户端期望的格式
            memories = []
            for item in items:
                memories.append({
                    "summary": item.get("summary", "用户之前的互动"),
                    "embedding_source": f"{item.get('timestamp', datetime.now().isoformat())} {item.get('source_type', 'interaction')}",
                    "relevance": 0.9,  # 在实际实现中，这将是基于向量相似度的实际得分
                    "memory_type": item.get("memory_type", "general")
                })
                
            return {
                "memories": memories
            }
        except Exception as e:
            self.logger.error(f"检索记忆时出错: {str(e)}")
            return self._get_mock_memories()
    
    async def update_or_create_conversation(self, user_id: str, 
                                          message: Dict[str, Any], 
                                          is_new: bool = False) -> str:
        """更新或创建对话历史"""
        timestamp = datetime.now().isoformat()
        
        try:
            if not self.client:
                return "local_conversation_id"
                
            if is_new:
                # 创建新对话
                conversation_id = f"conv_{int(datetime.now().timestamp())}"
                conversation = {
                    "id": conversation_id,
                    "user_id": user_id,
                    "start_time": timestamp,
                    "last_updated": timestamp,
                    "messages": [message],
                    "metadata": {
                        "emotion_trend": [],
                        "active": True
                    }
                }
                self.conversation_container.create_item(body=conversation)
                return conversation_id
            else:
                # 更新现有对话
                query = f"""
                    SELECT TOP 1 * FROM c 
                    WHERE c.user_id = '{user_id}' AND c.metadata.active = true
                    ORDER BY c.last_updated DESC
                """
                
                conversations = list(self.conversation_container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                
                if conversations:
                    conversation = conversations[0]
                    conversation["messages"].append(message)
                    conversation["last_updated"] = timestamp
                    
                    # 更新情绪趋势
                    if message.get("role") == "user" and "emotion" in message:
                        conversation["metadata"]["emotion_trend"].append(message["emotion"])
                    
                    self.conversation_container.replace_item(
                        item=conversation["id"], 
                        body=conversation
                    )
                    return conversation["id"]
                else:
                    # 如果没有找到活跃对话，创建新对话
                    return await self.update_or_create_conversation(
                        user_id, message, is_new=True
                    )
        except Exception as e:
            self.logger.error(f"更新对话历史时出错: {str(e)}")
            return "local_conversation_id"
    
    async def get_conversation_history(self, user_id: str, 
                                     conversation_id: str = None) -> List[Dict[str, str]]:
        """获取对话历史"""
        try:
            if not self.client:
                return []
                
            if conversation_id:
                # 获取特定对话
                try:
                    conversation = self.conversation_container.read_item(
                        item=conversation_id,
                        partition_key=user_id
                    )
                    return conversation["messages"]
                except exceptions.CosmosResourceNotFoundError:
                    self.logger.warning(f"对话 {conversation_id} 未找到")
                    return []
                except Exception as e:
                    self.logger.error(f"获取对话历史时出错: {str(e)}")
                    return []
            else:
                # 获取最近的活跃对话
                query = f"""
                    SELECT TOP 1 * FROM c 
                    WHERE c.user_id = '{user_id}' AND c.metadata.active = true
                    ORDER BY c.last_updated DESC
                """
                
                conversations = list(self.conversation_container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
                
                if conversations:
                    return conversations[0]["messages"]
                return []
        except Exception as e:
            self.logger.error(f"获取对话历史时出错: {str(e)}")
            return []
    
    # 辅助方法
    def _create_default_profile(self, user_id: str) -> Dict[str, Any]:
        """创建默认用户配置文件"""
        profile = {
            "id": user_id,
            "user_id": user_id,
            "personality": {
                "mbti": "INFJ",
                "communication_style": "supportive"
            },
            "preferences": {
                "suggestion_tone": "gentle",
                "likes_creative_suggestions": True,
                "activity_preferences": ["meditation", "journaling", "breathing_exercises"],
                "notification_frequency": "medium"
            },
            "health_goals": {
                "reduce_stress": True,
                "improve_sleep": True,
                "track_mood": True
            },
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # 保存到数据库
        try:
            if self.client:
                self.profile_container.create_item(body=profile)
        except Exception as e:
            self.logger.error(f"创建默认配置文件时出错: {str(e)}")
        
        return profile
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单实现 - 在实际项目中应该使用 NLP 工具
        words = text.lower().split()
        # 移除常见停用词
        stopwords = {"i", "me", "my", "myself", "we", "our", "the", "a", "an", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once"}
        keywords = [word for word in words if len(word) > 3 and word not in stopwords]
        return keywords[:10]  # 限制关键词数量
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本的向量嵌入"""
        # 在实际项目中，这里应该调用 OpenAI API 或其他嵌入模型
        # 这里返回一个模拟嵌入
        import random
        return [random.random() for _ in range(1536)]  # OpenAI 嵌入维度
    
    async def _create_and_store_embedding(self, user_id: str, source_id: str, 
                                        text: str, emotion: str, timestamp: str) -> None:
        """创建并存储嵌入"""
        try:
            if not self.client:
                return
                
            embedding = await self._generate_embedding(text)
            
            # 生成简短摘要
            summary = f"用户表达了{emotion}情绪: " + (text[:50] + "..." if len(text) > 50 else text)
            
            # 提取关键词
            keywords = self._extract_keywords(text)
            
            # 创建嵌入文档
            embedding_id = f"emb_{int(datetime.now().timestamp())}"
            embedding_doc = {
                "id": embedding_id,
                "user_id": user_id,
                "source_type": "interaction",
                "source_id": source_id,
                "timestamp": timestamp,
                "text": text,
                "summary": summary,
                "embedding": embedding,
                "memory_type": "emotion" if emotion in ["happy", "sad", "angry", "anxious", "tired"] else "general",
                "keywords": keywords
            }
            
            # 保存到 Cosmos DB
            self.embedding_container.create_item(body=embedding_doc)
        except Exception as e:
            self.logger.error(f"保存嵌入时出错: {str(e)}")
    
    # 本地存储方法（当 Cosmos DB 不可用时使用）
    def _get_local_user_profile(self, user_id: str) -> Dict[str, Any]:
        """从本地文件获取用户配置文件"""
        try:
            # 确定配置文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            profile_path = os.path.join(current_dir, "user_profile.json")
            
            # 检查文件是否存在
            if not os.path.exists(profile_path):
                return self._create_default_profile(user_id)
                
            # 从文件加载配置文件
            with open(profile_path, "r") as f:
                profiles = json.load(f)
                
            # 查找特定用户的配置文件
            if user_id in profiles:
                return profiles[user_id]
            else:
                return self._create_default_profile(user_id)
        except Exception as e:
            self.logger.error(f"加载本地用户配置文件时出错: {str(e)}")
            return self._create_default_profile(user_id)
    
    def _add_local_interaction(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """将交互添加到本地文件"""
        try:
            # 确定记忆文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            memory_path = os.path.join(current_dir, "memory.json")
            
            # 加载现有记忆
            memory = {"users": {}}
            if os.path.exists(memory_path):
                with open(memory_path, "r") as f:
                    memory = json.load(f)
            
            # 确保用户存在
            if user_id not in memory["users"]:
                memory["users"][user_id] = {
                    "interactions": [],
                    "emotion_history": [],
                    "last_active": None
                }
            
            # 添加交互
            memory["users"][user_id]["interactions"].append({
                "timestamp": interaction["timestamp"],
                "text": interaction["text"],
                "emotion": interaction["emotion"],
                "suggestion": interaction["suggestion"]
            })
            
            # 添加情绪历史
            memory["users"][user_id]["emotion_history"].append({
                "timestamp": interaction["timestamp"],
                "emotion": interaction["emotion"]
            })
            
            # 更新最后活跃时间
            memory["users"][user_id]["last_active"] = interaction["timestamp"]
            
            # 保存记忆
            with open(memory_path, "w") as f:
                json.dump(memory, f, indent=2)
        except Exception as e:
            self.logger.error(f"添加本地交互时出错: {str(e)}")
    
    def _get_local_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """从本地文件获取最近情绪"""
        try:
            # 确定记忆文件路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            memory_path = os.path.join(current_dir, "memory.json")
            
            # 检查文件是否存在
            if not os.path.exists(memory_path):
                return []
                
            # 加载记忆
            with open(memory_path, "r") as f:
                memory = json.load(f)
            
            # 检查用户是否存在
            if user_id not in memory["users"]:
                return []
            
            # 获取情绪历史
            emotion_history = memory["users"][user_id].get("emotion_history", [])
            
            # 返回最近的n条记录
            recent_emotions = emotion_history[-limit:] if emotion_history else []
            
            # 确保每条记录都有置信度字段
            for emotion in recent_emotions:
                if "confidence" not in emotion:
                    emotion["confidence"] = 0.8  # 默认置信度
            
            return recent_emotions
        except Exception as e:
            self.logger.error(f"获取本地情绪历史时出错: {str(e)}")
            return []
    
    def _get_mock_memories(self) -> Dict[str, List[Dict[str, Any]]]:
        """返回模拟记忆数据"""
        mock_memories = {
            "memories": [
                {
                    "summary": "用户上周说他讨厌下雨天",
                    "embedding_source": "2024-04-12 19:22:31 Chat content",
                    "relevance": 0.93,
                    "memory_type": "preference"
                },
                {
                    "summary": "用户说压力大时希望有人陪着他",
                    "embedding_source": "2024-03-30",
                    "relevance": 0.89,
                    "memory_type": "emotion"
                },
                {
                    "summary": "用户最近工作很忙，经常加班到很晚",
                    "embedding_source": "2024-04-10 20:15:45 Chat content",
                    "relevance": 0.85,
                    "memory_type": "context"
                }
            ]
        }
        return mock_memories 