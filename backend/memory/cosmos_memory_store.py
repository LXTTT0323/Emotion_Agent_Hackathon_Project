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
    
    async def get_user_id_by_username(self, username: str) -> Optional[str]:
        """通过用户名获取用户ID"""
        try:
            if not self.client:
                return username  # 在本地模式下，直接使用username作为user_id
                
            query = f"SELECT c.id, c.user_id FROM c WHERE c.username = '{username}'"
            items = list(self.profile_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if items:
                return items[0]["user_id"]
            else:
                # 如果用户名不存在，则创建新用户并返回ID
                new_profile = await self.create_user_profile(username=username)
                return new_profile["user_id"]
                
        except Exception as e:
            self.logger.error(f"通过用户名获取用户ID时出错: {str(e)}")
            return username  # 出错时返回用户名作为ID
    
    async def create_user_profile(self, username: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建新用户配置文件"""
        # 生成唯一用户ID
        user_id = f"user_{int(datetime.now().timestamp())}"
        
        profile = {
            "id": user_id,
            "user_id": user_id,
            "username": username,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "preferences": {
                "mbti": None,
                "tone": "supportive",
                "age": None,
                "star_sign": None
            },
            "metadata": metadata or {}
        }
        
        try:
            if not self.client:
                self._save_local_user_profile(profile)
                return profile
                
            # 保存到 Cosmos DB
            self.profile_container.create_item(body=profile)
            self.logger.info(f"创建新用户配置文件: {username} (ID: {user_id})")
            return profile
            
        except Exception as e:
            self.logger.error(f"创建用户配置文件时出错: {str(e)}")
            self._save_local_user_profile(profile)
            return profile
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户偏好设置"""
        try:
            if not self.client:
                return self._update_local_user_preferences(user_id, preferences)
                
            # 查询现有配置
            query = f"SELECT * FROM c WHERE c.user_id = '{user_id}'"
            items = list(self.profile_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if not items:
                raise Exception(f"用户 {user_id} 不存在")
                
            profile = items[0]
            
            # 更新偏好设置
            profile["preferences"].update(preferences)
            profile["last_active"] = datetime.now().isoformat()
            
            # 保存更新
            self.profile_container.replace_item(
                item=profile["id"],
                body=profile
            )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"更新用户偏好设置时出错: {str(e)}")
            return self._update_local_user_preferences(user_id, preferences)
    
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
                    "summary": [],  # 初始化摘要列表
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
                    
                    # 检查是否需要生成摘要
                    if len(conversation["messages"]) % 10 == 0:
                        # 导入摘要器
                        from backend.services.summarizer import summarizer
                        
                        # 获取最近10条消息
                        recent_messages = conversation["messages"][-10:]
                        
                        # 生成摘要
                        summary_text = await summarizer.summarize(recent_messages)
                        
                        # 将摘要添加到数组
                        if "summary" not in conversation:
                            conversation["summary"] = []
                            
                        conversation["summary"].append({
                            "text": summary_text,
                            "timestamp": timestamp,
                            "message_range": [len(conversation["messages"])-10, len(conversation["messages"])-1]
                        })
                    
                    self.conversation_container.replace_item(
                        item=conversation["id"], 
                        body=conversation
                    )
                    return conversation["id"]
                else:
                    # 如果没有活跃对话，创建新对话
                    return await self.update_or_create_conversation(user_id, message, True)
        except Exception as e:
            self.logger.error(f"更新对话历史时出错: {str(e)}")
            return "local_conversation_id"
    
    async def get_conversation_history(self, user_id: str, 
                                     conversation_id: str = None) -> List[Dict[str, str]]:
        """获取对话历史"""
        try:
            if not self.client:
                return [
                    {"role": "user", "content": "模拟本地历史消息1"},
                    {"role": "assistant", "content": "这是一条模拟的助手回复"}
                ]
                
            # 构建查询
            if conversation_id:
                query = f"SELECT c.messages FROM c WHERE c.id = '{conversation_id}'"
            else:
                query = f"""
                    SELECT TOP 1 c.messages FROM c 
                    WHERE c.user_id = '{user_id}' AND c.metadata.active = true
                    ORDER BY c.last_updated DESC
                """
                
            # 执行查询
            conversations = list(self.conversation_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if conversations and "messages" in conversations[0]:
                return conversations[0]["messages"]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"获取对话历史时出错: {str(e)}")
            return [
                {"role": "user", "content": "模拟消息 (获取历史出错)"},
                {"role": "assistant", "content": "这是一条模拟的助手回复"}
            ]
    
    async def get_conversation_summaries(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取用户的对话摘要列表"""
        try:
            if not self.client:
                return self._get_mock_conversation_summaries(limit)
                
            query = f"""
                SELECT c.id, c.start_time, c.last_updated, c.metadata, 
                       ARRAY_LENGTH(c.messages) as message_count,
                       c.summary
                FROM c 
                WHERE c.user_id = '{user_id}'
                ORDER BY c.last_updated DESC
                OFFSET 0 LIMIT {limit}
            """
            
            conversations = list(self.conversation_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # 处理结果
            results = []
            for conv in conversations:
                # 获取最新的摘要文本，如果有
                latest_summary = ""
                if "summary" in conv and conv["summary"]:
                    # 提取最后一条摘要
                    latest_summary = conv["summary"][-1]["text"] if len(conv["summary"]) > 0 else ""
                
                # 构建结果对象
                results.append({
                    "conversation_id": conv["id"],
                    "start_time": conv["start_time"],
                    "last_updated": conv["last_updated"],
                    "message_count": conv.get("message_count", 0),
                    "is_active": conv["metadata"].get("active", False),
                    "summary": latest_summary
                })
            
            return results
                
        except Exception as e:
            self.logger.error(f"获取对话摘要列表时出错: {str(e)}")
            return self._get_mock_conversation_summaries(limit)
    
    def _create_default_profile(self, user_id: str) -> Dict[str, Any]:
        """创建默认用户配置文件"""
        profile = {
            "id": user_id,
            "user_id": user_id,
            "username": f"user_{user_id[-6:]}",  # 生成一个默认用户名
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "preferences": {
                "mbti": None,
                "tone": "supportive",
                "age": None,
                "star_sign": None
            }
        }
        
        try:
            if self.client:
                self.profile_container.create_item(body=profile)
            else:
                self._save_local_user_profile(profile)
        except Exception as e:
            self.logger.error(f"创建默认用户配置文件时出错: {str(e)}")
            self._save_local_user_profile(profile)
            
        return profile
    
    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单实现：按空格分割并过滤短词
        words = text.lower().split()
        return [word for word in words if len(word) > 3]
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        # 在实际实现中，这将调用嵌入API
        # 目前返回一个假的嵌入向量
        return [0.1] * 10
    
    async def _create_and_store_embedding(self, user_id: str, source_id: str, 
                                        text: str, emotion: str, timestamp: str) -> None:
        """创建并存储记忆嵌入"""
        try:
            # 生成一个唯一ID
            memory_id = f"mem_{int(datetime.now().timestamp())}"
            
            # 创建一个简单的摘要
            summary = text[:100] + "..." if len(text) > 100 else text
            
            # 提取关键词
            keywords = self._extract_keywords(text)
            
            # 确定记忆类型
            memory_type = "interaction"
            
            # 创建记忆文档
            memory = {
                "id": memory_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "source_id": source_id,
                "source_type": "interaction",
                "summary": summary,
                "keywords": keywords,
                "emotion": emotion,
                "memory_type": memory_type,
                "embedding": await self._generate_embedding(text)  # 在实际实现中，这将是真实的嵌入向量
            }
            
            # 存储到 Cosmos DB
            if self.client:
                self.embedding_container.create_item(body=memory)
                
        except Exception as e:
            self.logger.error(f"创建记忆嵌入时出错: {str(e)}")
    
    def _get_local_user_profile(self, user_id: str) -> Dict[str, Any]:
        """从本地获取用户配置文件"""
        try:
            cache_dir = os.path.join(os.path.dirname(__file__), "_local_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            profile_path = os.path.join(cache_dir, f"profile_{user_id}.json")
            
            if os.path.exists(profile_path):
                with open(profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                profile = self._create_default_profile(user_id)
                self._save_local_user_profile(profile)
                return profile
                
        except Exception as e:
            self.logger.error(f"从本地获取用户配置文件时出错: {str(e)}")
            
            # 返回默认配置文件
            return {
                "id": user_id,
                "user_id": user_id,
                "username": f"user_{user_id[-6:]}",
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "preferences": {
                    "mbti": None,
                    "tone": "supportive",
                    "age": None,
                    "star_sign": None
                }
            }
    
    def _save_local_user_profile(self, profile: Dict[str, Any]) -> None:
        """保存用户配置文件到本地"""
        try:
            cache_dir = os.path.join(os.path.dirname(__file__), "_local_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            profile_path = os.path.join(cache_dir, f"profile_{profile['user_id']}.json")
            
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(profile, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"保存用户配置文件到本地时出错: {str(e)}")
    
    def _update_local_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """更新本地用户偏好设置"""
        try:
            # 获取现有配置文件
            profile = self._get_local_user_profile(user_id)
            
            # 更新偏好设置
            profile["preferences"].update(preferences)
            profile["last_active"] = datetime.now().isoformat()
            
            # 保存更新
            self._save_local_user_profile(profile)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"更新本地用户偏好设置时出错: {str(e)}")
            return {
                "id": user_id,
                "user_id": user_id,
                "error": str(e)
            }
    
    def _add_local_interaction(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """添加交互记录到本地存储"""
        try:
            cache_dir = os.path.join(os.path.dirname(__file__), "_local_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            interactions_path = os.path.join(cache_dir, f"interactions_{user_id}.json")
            
            # 读取现有交互
            interactions = []
            if os.path.exists(interactions_path):
                with open(interactions_path, "r", encoding="utf-8") as f:
                    interactions = json.load(f)
            
            # 添加新交互
            interactions.append(interaction)
            
            # 保存更新
            with open(interactions_path, "w", encoding="utf-8") as f:
                json.dump(interactions, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"添加交互记录到本地存储时出错: {str(e)}")
    
    def _get_local_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """从本地获取最近情绪记录"""
        try:
            cache_dir = os.path.join(os.path.dirname(__file__), "_local_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            emotions_path = os.path.join(cache_dir, f"emotions_{user_id}.json")
            
            if os.path.exists(emotions_path):
                with open(emotions_path, "r", encoding="utf-8") as f:
                    emotions = json.load(f)
                    
                # 返回最近的记录
                return emotions[-limit:] if len(emotions) > limit else emotions
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"从本地获取最近情绪记录时出错: {str(e)}")
            
            # 返回模拟数据
            return [
                {
                    "id": f"mock_emo_{i}",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "emotion": "N" if i % 2 == 0 else "P",
                    "confidence": 0.8,
                    "context_keywords": ["mock", "data"]
                }
                for i in range(limit)
            ]
    
    def _get_mock_memories(self) -> Dict[str, List[Dict[str, Any]]]:
        """返回模拟记忆数据"""
        return {
            "memories": [
                {
                    "summary": "用户说他们不喜欢下雨天",
                    "embedding_source": "2024-04-12 19:22:31 对话内容",
                    "relevance": 0.93,
                    "memory_type": "preference"
                },
                {
                    "summary": "用户提到他们希望有人在他们压力大时陪伴他们",
                    "embedding_source": "2024-03-30",
                    "relevance": 0.89,
                    "memory_type": "emotion"
                },
                {
                    "summary": "用户说他们最近工作很忙，经常加班到很晚",
                    "embedding_source": "2024-04-10 20:15:45 对话内容",
                    "relevance": 0.85,
                    "memory_type": "context"
                }
            ]
        }
        
    def _get_mock_conversation_summaries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """返回模拟对话摘要列表"""
        return [
            {
                "conversation_id": f"mock_conv_{i}",
                "start_time": (datetime.now().replace(day=datetime.now().day - i)).isoformat(),
                "last_updated": (datetime.now().replace(hour=datetime.now().hour - i)).isoformat(),
                "message_count": 10 + i * 5,
                "is_active": i == 0,
                "summary": f"这是第 {i+1} 个模拟对话的摘要，用户讨论了他们的日常生活和情绪状态。"
            }
            for i in range(limit)
        ] 