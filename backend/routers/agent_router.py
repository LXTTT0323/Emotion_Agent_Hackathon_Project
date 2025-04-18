from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..services.agent_kernel import AgentKernel

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)

# 输入模型
class ChatRequest(BaseModel):
    message: str

# 响应模型
class ChatResponse(BaseModel):
    response: str

# 创建 AgentKernel 实例
agent_kernel = AgentKernel(mode="default")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    与 AI 进行对话
    
    - 输入: 用户消息
    - 输出: AI 回复
    """
    try:
        response = await agent_kernel.chat(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}") 