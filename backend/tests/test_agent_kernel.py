import os
import pytest
import asyncio
from backend.services.agent_kernel import AgentKernel

# 设置测试所需的环境变量
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "your-deployment-name"
os.environ["AZURE_OPENAI_API_KEY"] = "your-api-key"
os.environ["AZURE_OPENAI_ENDPOINT"] = "your-endpoint"

@pytest.mark.asyncio
async def test_comfort_user_with_memory_mock_mode():
    """
    测试 mock 模式下的 comfort_user_with_memory 功能
    """
    # 创建 mock 模式的 AgentKernel 实例
    agent = AgentKernel(mode="mock")
    
    # 测试参数
    test_user_id = "test_user_123"
    test_emotion = "sadness"
    test_confidence = 0.91
    test_time_of_day = "晚上"
    
    try:
        # 调用 comfort_user_with_memory 方法
        messages = await agent.comfort_user_with_memory(
            user_id=test_user_id,
            emotion=test_emotion,
            confidence=test_confidence,
            time_of_day=test_time_of_day
        )
        
        # 验证返回结果
        assert isinstance(messages, list), "返回结果应该是列表"
        assert len(messages) >= 1, "至少应该返回一条消息"
        
        # 打印结果以便查看
        print("\n测试结果：")
        print(f"用户ID: {test_user_id}")
        print(f"情绪: {test_emotion}")
        print(f"置信度: {test_confidence}")
        print(f"时间段: {test_time_of_day}")
        print("\n生成的安慰消息：")
        for i, message in enumerate(messages, 1):
            print(f"消息 {i}: {message}")
            
    except Exception as e:
        pytest.fail(f"测试失败: {str(e)}")

if __name__ == "__main__":
    # 直接运行测试
    asyncio.run(test_comfort_user_with_memory_mock_mode()) 