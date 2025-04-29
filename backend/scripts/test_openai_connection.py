"""
测试Azure OpenAI连接的脚本
运行方法: python -m backend.scripts.test_openai_connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# 加载.env文件
env_path = os.path.join(os.path.dirname(current_dir), '.env')
load_dotenv(env_path)

def test_openai_connection():
    """测试Azure OpenAI连接"""
    
    # 获取环境变量
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # 打印配置信息
    print(f"Azure OpenAI配置:")
    print(f"- Endpoint: {endpoint}")
    print(f"- API Version: {api_version}")
    print(f"- Deployment: {deployment}")
    print(f"- API密钥是否存在: {'是' if api_key else '否'}")
    
    try:
        # 创建Azure OpenAI客户端
        client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=api_key,
        )
        
        # 测试调用
        print("\n正在测试Azure OpenAI连接...")
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": "你好，今天天气怎么样？"}
            ],
            model=deployment,
            max_tokens=100,
        )
        
        # 打印结果
        print("\n✅ 连接成功!")
        print(f"\n回复内容:")
        print(f"{response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {str(e)}")
        print("\n详细错误信息:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_openai_connection() 