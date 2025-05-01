from fastapi import APIRouter, HTTPException, Header, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.agent_kernel import AgentKernel
from ..memory.cosmos_memory_store import CosmosMemoryStore
from datetime import datetime
import os
import shutil
from pathlib import Path

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)

# 创建 AgentKernel 实例，使用默认模式
agent_kernel = AgentKernel(mode="default")

# 创建数据库客户端
cosmos_client = CosmosMemoryStore()

# 输入模型
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    emotion: Optional[str] = None
    confidence: Optional[float] = None

class FollowupRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    time_of_day: Optional[str] = None
    reason: Optional[str] = None

# 记忆检索请求模型
class MemoryRetrieveRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    query: str
    top_k: int = 3

# 开始对话请求模型
class StartConversationRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None

# 情绪分析请求模型
class EmotionAnalyzeRequest(BaseModel):
    conversation_id: str
    message: str

# 用户偏好设置模型
class UserPreferences(BaseModel):
    mbti: Optional[str] = None
    tone: Optional[str] = None
    age: Optional[int] = None
    star_sign: Optional[str] = None

# 响应模型
class ChatResponse(BaseModel):
    response: str

class EmotionAnalyzeResponse(BaseModel):
    emotion: str
    response: str

class MemoryResponse(BaseModel):
    memories: List[Dict[str, Any]]

class HistoryResponse(BaseModel):
    history: List[Dict[str, str]]

class SimpleResponse(BaseModel):
    success: bool
    message: str

class SummaryResponse(BaseModel):
    summaries: List[Dict[str, Any]]

async def get_user_id(user_id: Optional[str] = None, username: Optional[str] = None, x_user_id: Optional[str] = None):
    """统一获取用户ID的辅助函数"""
    # 优先使用请求体中的user_id
    if user_id:
        return user_id
    
    # 其次使用请求头中的x-user-id
    if x_user_id:
        return x_user_id
    
    # 最后使用用户名查找或创建用户ID
    if username:
        return await cosmos_client.get_user_id_by_username(username)
    
    # 如果都没有提供，使用默认用户ID
    return "default_user"

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    x_user_id: Optional[str] = Header(None)
):
    """
    与 AI 进行对话
    
    - 输入: 用户消息和用户ID/用户名，可选的情绪状态和置信度
    - 输出: AI 回复
    """
    try:
        # 获取用户ID
        user_id = await get_user_id(request.user_id, request.username, x_user_id)
        
        response = await agent_kernel.chat(
            query=request.message, 
            user_id=user_id,
            emotion=request.emotion,
            confidence=request.confidence
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@router.post("/analyze", response_model=EmotionAnalyzeResponse)
async def analyze_emotion(
    request: EmotionAnalyzeRequest,
    x_user_id: Optional[str] = Header(None)
):
    """
    分析消息情绪并返回回复
    
    - 输入: 用户消息和对话ID
    - 输出: 情绪分析和AI回复
    """
    try:
        # 获取用户ID
        user_id = x_user_id or "default_user"
        
        # 构造模拟健康数据
        # 这里我们基于消息长度和内容来生成一些模拟的健康指标
        message_length = len(request.message)
        
        mock_health_data = {
            "heart_rate": {"avg": 75 + (message_length % 20), "min": 62, "max": 110},
            "hrv": {"rmssd": 45.2, "sdnn": 52.8 - (message_length % 10)},
            "sleep": {"deep_sleep_minutes": 90, "total_minutes": 420},
            "steps": 8500,
            "menstrual_cycle": {"phase": "follicular", "day": 8},
            "timestamp": str(datetime.now())
        }
        
        # 预测情绪
        from ..tools.emotion_prediction_tool import predict_emotion_and_generate_question
        emotion_data = await predict_emotion_and_generate_question(mock_health_data)
        
        # 转换情绪状态和置信度
        status, confidence = agent_kernel.convert_emotion_to_status(emotion_data)
        
        # 使用情绪数据与Agent交谈
        response = await agent_kernel.chat(
            query=request.message, 
            user_id=user_id,
            emotion=status,
            confidence=confidence
        )
        
        # 记录到数据库
        if request.conversation_id != "new":
            # 添加对话
            message = {
                "role": "user",
                "content": request.message,
                "emotion": status,
                "confidence": confidence,
                "timestamp": str(datetime.now())
            }
            await cosmos_client.update_or_create_conversation(
                user_id=user_id, 
                message=message,
                is_new=request.conversation_id == "new"
            )
            
            # 添加助手回复
            assistant_message = {
                "role": "assistant",
                "content": response,
                "timestamp": str(datetime.now())
            }
            await cosmos_client.update_or_create_conversation(
                user_id=user_id, 
                message=assistant_message,
                is_new=False
            )
            
        return {
            "emotion": status,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情绪分析失败: {str(e)}")

@router.post("/followup", response_model=ChatResponse)
async def followup_with_agent(
    request: FollowupRequest,
    x_user_id: Optional[str] = Header(None)
):
    """
    AI主动发起对话
    
    - 输入: 用户ID/用户名、情绪状态、时间和原因
    - 输出: AI 主动发起的回复
    """
    try:
        # 获取用户ID
        user_id = await get_user_id(request.user_id, request.username, x_user_id)
        
        response = await agent_kernel.followup(
            user_id=user_id,
            emotion=request.emotion,
            confidence=request.confidence,
            time_of_day=request.time_of_day,
            reason=request.reason
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"主动对话失败: {str(e)}")

@router.post("/start_conversation", response_model=SimpleResponse)
async def start_new_conversation(
    request: StartConversationRequest,
    x_user_id: Optional[str] = Header(None)
):
    """
    开始新对话，清除之前的对话历史
    
    - 输入: 用户ID/用户名
    - 输出: 成功状态
    """
    try:
        # 获取用户ID
        user_id = await get_user_id(request.user_id, request.username, x_user_id)
        
        agent_kernel.start_conversation(user_id)
        return {"success": True, "message": f"已为用户 {user_id} 开始新对话"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始对话失败: {str(e)}")

@router.get("/history/{user_id}", response_model=HistoryResponse)
async def get_chat_history(
    user_id: str,
    x_user_id: Optional[str] = Header(None)
):
    """
    获取指定用户的对话历史
    
    - 输入: 用户ID
    - 输出: 对话历史
    """
    try:
        # 使用提供的用户ID或头部用户ID
        effective_user_id = x_user_id if x_user_id else user_id
        
        history = agent_kernel.get_conversation_history(effective_user_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")

@router.post("/memory/retrieve", response_model=MemoryResponse)
async def retrieve_memory(
    request: MemoryRetrieveRequest,
    x_user_id: Optional[str] = Header(None)
):
    """
    检索用户相关记忆
    
    - 输入: 用户ID/用户名和查询
    - 输出: 相关记忆
    """
    try:
        # 获取用户ID
        user_id = await get_user_id(request.user_id, request.username, x_user_id)
        
        memories = agent_kernel.retrieve_memory(user_id, request.query, request.top_k)
        return memories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记忆检索失败: {str(e)}")

@router.get("/conversations", response_model=SummaryResponse)
async def get_conversation_summaries(
    limit: int = 5,
    x_user_id: Optional[str] = Header(None),
    user_id: Optional[str] = None,
    username: Optional[str] = None
):
    """
    获取用户的对话摘要列表
    
    - 输入: 用户ID/用户名，摘要数量限制
    - 输出: 对话摘要列表
    """
    try:
        # 获取用户ID
        effective_user_id = await get_user_id(user_id, username, x_user_id)
        
        summaries = await cosmos_client.get_conversation_summaries(effective_user_id, limit)
        return {"summaries": summaries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话摘要失败: {str(e)}")

@router.post("/preferences", response_model=SimpleResponse)
async def update_user_preferences(
    preferences: UserPreferences,
    x_user_id: Optional[str] = Header(None),
    user_id: Optional[str] = None,
    username: Optional[str] = None
):
    """
    更新用户偏好设置
    
    - 输入: 用户ID/用户名，偏好设置
    - 输出: 成功状态
    """
    try:
        # 获取用户ID
        effective_user_id = await get_user_id(user_id, username, x_user_id)
        
        # 过滤掉None值，只更新有值的字段
        preferences_dict = {k: v for k, v in preferences.dict().items() if v is not None}
        
        if not preferences_dict:
            return {"success": False, "message": "未提供任何有效的偏好设置"}
        
        await cosmos_client.update_user_preferences(effective_user_id, preferences_dict)
        return {"success": True, "message": "用户偏好设置已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户偏好设置失败: {str(e)}")

@router.post("/upload_health_data", response_model=SimpleResponse)
async def upload_health_data(
    file: UploadFile = File(...),
    x_user_id: Optional[str] = Header(None),
    user_id: Optional[str] = None,
    username: Optional[str] = None
):
    """
    上传健康数据文件
    
    - 输入: CSV格式的心率变异性数据文件
    - 输出: 成功状态和情绪预测结果
    """
    try:
        # 获取用户ID
        effective_user_id = await get_user_id(user_id, username, x_user_id)
        
        # 验证文件类型
        if not file.filename.endswith('.csv'):
            return {"success": False, "message": "请上传CSV格式的文件"}
        
        # 创建model目录（如果不存在）
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_dir = os.path.join(current_dir, "model")
        os.makedirs(model_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(model_dir, "HeartRateVariabilitySDNN.csv")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 构造健康数据用于分析
        mock_health_data = {
            "heart_rate": {"avg": 75, "min": 62, "max": 110},
            "hrv": {"rmssd": 45.2, "sdnn": 52.8},
            "sleep": {"deep_sleep_minutes": 90, "total_minutes": 420},
            "steps": 8500,
            "timestamp": str(datetime.now())
        }
        
        # 调用情绪预测工具进行分析
        from ..tools.emotion_prediction_tool import predict_emotion_and_generate_question
        emotion_result = await predict_emotion_and_generate_question(mock_health_data)
        
        # 获取生成的问题并直接返回
        generated_question = emotion_result.get("generated_question", "")
        
        # 如果没有生成问题，使用默认的关心问题
        if not generated_question:
            predicted_emotion = emotion_result.get("predicted_emotion", "baseline")
            if predicted_emotion == "stress":
                generated_question = "你的心率数据告诉我，最近是不是压力有点大？要不要和我说说看..."
            elif predicted_emotion == "amusement":
                generated_question = "看到你的身体状态这么好，我也跟着开心起来了...最近是遇到什么好事了吗？"
            else:
                generated_question = "我看到你的心率和心率变异性都很平稳...不过，最近是不是有什么事在困扰你？"
        
        return {
            "success": True, 
            "message": generated_question
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传健康数据失败: {str(e)}") 