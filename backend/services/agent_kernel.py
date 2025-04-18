import os
import asyncio
from typing import Dict, Any, List
import json
import logging

# Semantic Kernel 导入
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

# Imports for tools
from backend.tools.fetch_emotion_context import analyze_emotion
from backend.tools.fetch_health_data import fetch_health_data
from backend.tools.user_profile_tool import get_user_profile
from backend.tools.intervene import generate_suggestion
from backend.memory.context_store import ContextStore
from backend.services.tool_registry import ToolRegistry

# Create emotion analysis plugin
class EmotionToolsPlugin:
    def __init__(self, context_store):
        self.context_store = context_store
    
    @kernel_function(
        name="analyze_emotion",
        description="分析文本识别用户情绪状态和置信度"
    )
    async def analyze_emotion_text(self, text: str) -> str:
        """分析用户文本中的情绪"""
        result = await analyze_emotion(text)
        return json.dumps(result)
    
    @kernel_function(
        name="fetch_health_data",
        description="获取用户健康数据，包括心率、HRV、睡眠等"
    )
    async def get_health_data(self, user_id: str) -> str:
        """获取用户健康数据"""
        result = await fetch_health_data(user_id)
        return json.dumps(result)
    
    @kernel_function(
        name="get_user_profile",
        description="获取用户档案信息，包括偏好和健康目标"
    )
    async def get_user_profile_data(self, user_id: str) -> str:
        """获取用户档案"""
        result = await get_user_profile(user_id)
        return json.dumps(result)
    
    @kernel_function(
        name="generate_suggestion",
        description="根据情绪和健康数据生成支持性建议"
    )
    async def create_suggestion(self, emotion: str, health_data: str) -> str:
        """生成个性化建议"""
        health_data_dict = json.loads(health_data) if isinstance(health_data, str) else health_data
        result = await generate_suggestion(
            emotion=emotion,
            confidence=0.9,
            health_data=health_data_dict,
            user_profile={}
        )
        return json.dumps(result)
    
    @kernel_function(
        name="save_context",
        description="保存用户互动到上下文存储"
    )
    async def save_to_context(self, user_id: str, text: str, emotion: str, suggestion: str) -> str:
        """保存互动到上下文存储"""
        await self.context_store.add_interaction(
            user_id=user_id,
            text=text,
            emotion=emotion,
            suggestion=suggestion
        )
        return "保存成功"

# In a real implementation, this would use Semantic Kernel
# For now, we'll create a class that demonstrates the structure
class AgentKernel:
    def __init__(self):
        """
        Initialize the agent with tools and memory.
        
        In a full implementation, this would:
        1. Load API keys from environment
        2. Initialize Semantic Kernel
        3. Register all tools from tool_registry
        4. Connect to memory/context store
        """
        self.context_store = ContextStore()
        self.tool_registry = ToolRegistry()
        self.tools = self.tool_registry.get_tools()
        self.prompt_templates = {}
        
        # Load prompt templates
        self._load_prompts()
        
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        
        # Initialize Semantic Kernel
        self.kernel = Kernel()
        
        # Add Azure OpenAI service (please replace with your API key and deployment name)
        deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        base_url = os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        # 确保所有必要的环境变量都已设置
        if not deployment_name or not api_key or not base_url:
            raise ValueError("请确保设置了AZURE_OPENAI_DEPLOYMENT_NAME、AZURE_OPENAI_API_KEY和AZURE_OPENAI_ENDPOINT环境变量")
        
        chat_completion = AzureChatCompletion(
            deployment_name=deployment_name,
            api_key=api_key,
            base_url=base_url,
        )
        self.kernel.add_service(chat_completion)
        
        # Register tool plugins
        self.kernel.add_plugin(
            EmotionToolsPlugin(self.context_store),
            plugin_name="EmotionTools"
        )
        
        # Set execution configuration
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
    def _load_prompts(self):
        """Load prompt templates from files"""
        try:
            # Determine the absolute path to the prompt template
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            prompt_path = os.path.join(project_root, "backend", "prompts", "empathy_prompt.txt")
            
            with open(prompt_path, "r") as f:
                self.prompt_templates["empathy"] = f.read()
        except FileNotFoundError:
            # Default template if file not found
            self.prompt_templates["empathy"] = """
            You are an empathetic AI assistant helping someone who is feeling {{emotion}}.
            Their physiological data shows {{health_context}}.
            Craft a gentle, supportive response that:
            - Acknowledges their feelings
            - Offers a suggestion based on their current state
            - Provides encouragement
            """
    
    async def analyze(self, user_id: str, text: str, health_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input through tool pipeline.
        
        1. Classify emotion in the text
        2. Retrieve health context from data
        3. Fetch user profile and preferences
        4. Generate a personalized suggestion
        5. Update memory/context with the interaction
        """
        # Step 1: Analyze emotion in the text
        emotion_result = await analyze_emotion(text)
        
        # Step 2: Get health data if not provided
        if health_data is None:
            health_data = await fetch_health_data(user_id)
        
        # Step 3: Get user profile
        user_profile = await get_user_profile(user_id)
        
        # Step 4: Get user context from memory
        user_context = await self.context_store.get_user_context(user_id)
        
        # Step 5: Generate suggestion based on emotion, health data, and user profile
        suggestion_result = await generate_suggestion(
            emotion=emotion_result["emotion"],
            confidence=emotion_result["confidence"],
            health_data=health_data,
            user_profile=user_profile
        )
        
        # Step 6: Store interaction in memory
        await self.context_store.add_interaction(
            user_id=user_id,
            text=text,
            emotion=emotion_result["emotion"],
            suggestion=suggestion_result["suggestion"]
        )
        
        # Return result
        return {
            "suggestion": suggestion_result["suggestion"],
            "emotion": emotion_result["emotion"],
            "confidence": emotion_result["confidence"]
        } 