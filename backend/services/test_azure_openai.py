import os
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 从环境变量获取配置
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

# 创建客户端
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

# 测试连接
try:
    # 获取可用的模型列表
    models = client.models.list()
    print("可用的模型：")
    for model in models:
        print(f"- {model.id}")
    
    # 测试聊天功能
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 使用您的部署名称
        messages=[
            {"role": "system", "content": "你是一个有用的助手。"},
            {"role": "user", "content": "你好！"}
        ]
    )
    print("\n聊天测试结果：")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"发生错误：{str(e)}") 