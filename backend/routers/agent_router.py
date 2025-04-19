from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.agent_kernel import AgentKernel

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)

# 输入模型
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    emotion: Optional[str] = None
    confidence: Optional[float] = None

class FollowupRequest(BaseModel):
    user_id: str = "default_user"
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    time_of_day: Optional[str] = None
    reason: Optional[str] = None

# 记忆检索请求模型
class MemoryRetrieveRequest(BaseModel):
    user_id: str
    query: str
    top_k: int = 3

# 开始对话请求模型
class StartConversationRequest(BaseModel):
    user_id: str

# 响应模型
class ChatResponse(BaseModel):
    response: str

class MemoryResponse(BaseModel):
    memories: List[Dict[str, Any]]

class HistoryResponse(BaseModel):
    history: List[Dict[str, str]]

class SimpleResponse(BaseModel):
    success: bool
    message: str

# 创建 AgentKernel 实例，使用mock模式
agent_kernel = AgentKernel(mode="mock")

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """
    与 AI 进行对话
    
    - 输入: 用户消息和用户ID，可选的情绪状态和置信度
    - 输出: AI 回复
    """
    try:
        response = await agent_kernel.chat(
            query=request.message, 
            user_id=request.user_id,
            emotion=request.emotion,
            confidence=request.confidence
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@router.post("/followup", response_model=ChatResponse)
async def followup_with_agent(request: FollowupRequest):
    """
    AI主动发起对话
    
    - 输入: 用户ID、情绪状态、时间和原因
    - 输出: AI 主动发起的回复
    """
    try:
        response = await agent_kernel.followup(
            user_id=request.user_id,
            emotion=request.emotion,
            confidence=request.confidence,
            time_of_day=request.time_of_day,
            reason=request.reason
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"主动对话失败: {str(e)}")

@router.post("/start_conversation", response_model=SimpleResponse)
async def start_new_conversation(request: StartConversationRequest):
    """
    开始新对话，清除之前的对话历史
    
    - 输入: 用户ID
    - 输出: 成功状态
    """
    try:
        agent_kernel.start_conversation(request.user_id)
        return {"success": True, "message": f"已为用户 {request.user_id} 开始新对话"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始对话失败: {str(e)}")

@router.get("/history/{user_id}", response_model=HistoryResponse)
async def get_chat_history(user_id: str):
    """
    获取指定用户的对话历史
    
    - 输入: 用户ID
    - 输出: 对话历史
    """
    try:
        history = agent_kernel.get_conversation_history(user_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")

@router.post("/memory/retrieve", response_model=MemoryResponse)
async def retrieve_memory(request: MemoryRetrieveRequest):
    """
    检索用户相关记忆
    
    - 输入: 用户ID和查询
    - 输出: 相关记忆
    """
    try:
        memories = agent_kernel.retrieve_memory(request.user_id, request.query, request.top_k)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记忆检索失败: {str(e)}") 