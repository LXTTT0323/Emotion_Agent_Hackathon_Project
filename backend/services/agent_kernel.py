import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class AgentKernel:
    def __init__(self, mode: str = "default"):
        """
        初始化 AgentKernel
        
        Args:
            mode: 运行模式，'default'或'mock'
        """
        self.mode = mode
        self.kernel = Kernel()
        
        # 设置日志
        logging.basicConfig(
            format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.getLogger("kernel").setLevel(logging.DEBUG)
        
        # 从环境变量获取 Azure OpenAI 配置
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        # 打印配置信息（调试用）
        print(f"部署名称: {deployment_name}")
        print(f"端点: {endpoint}")
        print(f"API 密钥长度: {len(api_key) if api_key else 0}")
        print(f"API 版本: {api_version}")
        if not all([deployment_name, api_key, endpoint]):
            raise ValueError("请设置以下环境变量：AZURE_OPENAI_DEPLOYMENT_NAME, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT")
        
        # 添加 Azure OpenAI 服务
        self.chat_completion = AzureChatCompletion(
            deployment_name=deployment_name,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )

        
        self.kernel.add_service(self.chat_completion)
        
        # 设置执行配置
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        
        # 初始化聊天历史
        self.chat_history = ChatHistory()
    
    async def chat(self, user_input: str) -> str:
        """
        与 AI 进行对话
        
        Args:
            user_input: 用户输入的消息
            
        Returns:
            AI 的回复
        """
        # 添加用户消息到历史
        self.chat_history.add_user_message(user_input)
        
        # 获取 AI 回复
        result = await self.chat_completion.get_chat_message_content(
            chat_history=self.chat_history,
            settings=self.execution_settings,
            kernel=self.kernel,
        )
        
        # 添加 AI 回复到历史
        self.chat_history.add_message(result)
        
        return str(result)

# 示例用法
async def example_usage():
    """示例用法：展示如何使用 AgentKernel 进行对话"""
    # 初始化 AgentKernel
    agent = AgentKernel(mode="default")
    
    # 示例对话
    print("开始对话（输入 'exit' 退出）")
    while True:
        user_input = input("用户 > ")
        if user_input.lower() == "exit":
            break
            
        response = await agent.chat(user_input)
        print(f"AI > {response}")

if __name__ == "__main__":
    asyncio.run(example_usage())
