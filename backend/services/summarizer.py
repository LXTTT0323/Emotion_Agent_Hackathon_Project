import os
import logging
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 从环境变量获取Azure OpenAI配置
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

class ConversationSummarizer:
    """
    对话摘要生成器
    
    提供对话摘要功能：
    1. 每10条消息生成一次摘要
    2. 摘要长度控制在80个中文字以内
    3. 提供检索历史摘要功能
    """
    
    def __init__(self, mock_mode: bool = False):
        """
        初始化摘要生成器
        
        Args:
            mock_mode: 是否使用模拟模式
        """
        self.mock_mode = mock_mode or os.getenv("USE_MOCK_RESPONSES", "0") == "1"
        
        # 初始化 OpenAI 客户端
        if not self.mock_mode:
            try:
                self.client = AzureOpenAI(
                    api_version=api_version,
                    azure_endpoint=endpoint,
                    api_key=api_key,
                )
                logger.info("成功初始化 OpenAI 客户端用于摘要生成")
            except Exception as e:
                logger.error(f"初始化 OpenAI 客户端时出错: {str(e)}")
                self.client = None
                self.mock_mode = True
        else:
            self.client = None
            logger.info("摘要生成器使用模拟模式")
    
    async def summarize(self, messages: List[Dict[str, Any]]) -> str:
        """
        对会话消息生成摘要
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user/assistant", "content": "消息内容", "emotion": "情绪标签"}]
            
        Returns:
            摘要文本，限制在80个中文字符以内
        """
        if self.mock_mode or not self.client:
            return self._generate_mock_summary(messages)
        
        try:
            # 构造摘要请求
            conversation_text = ""
            emotions = []
            
            for msg in messages:
                role = "用户" if msg['role'] == "user" else "助手"
                content = msg['content']
                emotion = msg.get('emotion_label', '')  # 获取情绪标签
                if emotion:
                    emotions.append(emotion)
                conversation_text += f"{role}: {content}\n"
            
            # 分析情绪变化
            emotion_trend = ""
            if emotions:
                emotion_counts = {}
                for e in emotions:
                    emotion_counts[e] = emotion_counts.get(e, 0) + 1
                main_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
                emotion_trend = f"\n用户主要情绪状态: {main_emotion}"
            
            system_prompt = (
                "你是一个专业的对话摘要生成器。你的任务是将一段对话总结成简短的摘要。"
                "摘要必须：\n"
                "1. 不超过80个中文字符\n"
                "2. 包含对话中最重要的情绪和内容要点\n"
                "3. 使用第三人称客观描述\n"
                "4. 重点关注用户的情绪变化和关键诉求"
            )
            
            user_prompt = f"请对以下对话生成简短摘要（不超过80个中文字符）：\n\n{conversation_text}{emotion_trend}"
            
            # 调用API生成摘要
            response = self.client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=256,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            # 确保摘要不超过80个中文字符
            if len(summary) > 80:
                summary = summary[:77] + "..."
                
            logger.info(f"生成摘要成功: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要时出错: {str(e)}")
            return self._generate_mock_summary(messages)
    
    def _generate_mock_summary(self, messages: List[Dict[str, Any]]) -> str:
        """
        生成模拟摘要（在无法连接API时使用）
        
        Args:
            messages: 对话消息列表
            
        Returns:
            模拟的摘要文本
        """
        # 计算用户和助手的消息数
        user_msgs = [msg for msg in messages if msg["role"] == "user"]
        
        # 提取情绪信息
        emotions = []
        for msg in messages:
            if msg.get('emotion_label'):
                emotions.append(msg['emotion_label'])
        
        # 生成情绪趋势描述
        emotion_trend = ""
        if emotions:
            emotion_counts = {}
            for e in emotions:
                emotion_counts[e] = emotion_counts.get(e, 0) + 1
            main_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
            emotion_trend = f"，情绪状态主要为{main_emotion}"
        
        # 提取第一条和最后一条用户消息的关键词
        first_user_msg = user_msgs[0]["content"] if user_msgs else ""
        last_user_msg = user_msgs[-1]["content"] if user_msgs else ""
        
        first_words = first_user_msg[:10] + "..." if len(first_user_msg) > 10 else first_user_msg
        last_words = last_user_msg[:10] + "..." if len(last_user_msg) > 10 else last_user_msg
        
        # 生成摘要
        summary = f"用户从「{first_words}」开始聊天{emotion_trend}，期间讨论了{len(messages)}个话题，最后谈到「{last_words}」。"
        
        return summary
    
    async def get_relevant_history(self, user_id: str, 
                                  cosmos_client, 
                                  current_messages: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        获取相关历史摘要和当前窗口文本，提供给SK prompt
        
        Args:
            user_id: 用户ID
            cosmos_client: CosmosDB客户端
            current_messages: 当前窗口消息列表
            
        Returns:
            格式化的历史摘要文本
        """
        try:
            # 获取最近一条对话摘要
            container = cosmos_client.conversation_container
            query = f"""
                SELECT TOP 1 c.summary
                FROM c 
                WHERE c.user_id = '{user_id}' AND IS_DEFINED(c.summary)
                ORDER BY c.last_updated DESC
            """
            
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # 构建返回的文本
            history_text = ""
            
            # 添加历史摘要
            if items and 'summary' in items[0]:
                history_text += f"上次对话摘要: {items[0]['summary']}\n\n"
            
            # 添加当前窗口文本
            if current_messages:
                history_text += "当前对话:\n"
                for msg in current_messages:
                    role = "用户" if msg["role"] == "user" else "助手"
                    history_text += f"{role}: {msg['content']}\n"
            
            return history_text.strip()
            
        except Exception as e:
            logger.error(f"获取历史摘要时出错: {str(e)}")
            
            # 出错时返回简单的默认文本
            default_text = ""
            if current_messages:
                default_text = "当前对话:\n"
                for msg in current_messages[-3:]:  # 只取最近3条
                    role = "用户" if msg["role"] == "user" else "助手"
                    default_text += f"{role}: {msg['content']}\n"
            
            return default_text.strip()


# 创建单例实例
summarizer = ConversationSummarizer()

# 测试代码
if __name__ == "__main__":
    import asyncio
    
    # 测试消息
    test_messages = [
        {"role": "user", "content": "最近工作压力很大，感觉很累"},
        {"role": "assistant", "content": "听上去你最近遇到了很多挑战。能具体说说是什么让你感到压力吗？"},
        {"role": "user", "content": "项目截止日期很紧，我感觉自己可能完不成"},
        {"role": "assistant", "content": "面对紧张的截止日期确实很有压力。你尝试过把任务分解成小部分来完成吗？"},
        {"role": "user", "content": "试过了，但感觉还是很难全部完成"},
        {"role": "assistant", "content": "这种情况下，与项目经理沟通延期的可能性也是一个选择。你有考虑过吗？"},
        {"role": "user", "content": "我不敢提出来，怕被认为能力不足"},
        {"role": "assistant", "content": "理解你的顾虑。但专业地表达困难和寻求支持实际上是一种负责任的表现。"},
        {"role": "user", "content": "你说得对，也许我应该尝试沟通一下"},
        {"role": "assistant", "content": "这是个好主意。清晰地表达你已完成的工作和面临的挑战，提出可行的解决方案。"}
    ]
    
    # 测试摘要生成
    summary = asyncio.run(summarizer.summarize(test_messages))
    print(f"生成的摘要: {summary}") 