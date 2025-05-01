from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..memory.cosmos_memory_store import CosmosMemoryStore

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# 创建数据库客户端
cosmos_client = CosmosMemoryStore()

# 用户偏好设置模型
class UserPreferences(BaseModel):
    username: str
    mbti: Optional[str] = None
    tone: Optional[str] = "supportive"
    age: Optional[int] = None
    star_sign: Optional[str] = None

# 用户偏好响应模型
class UserPreferencesResponse(BaseModel):
    username: str
    preferences: Dict[str, Any]

@router.post("/preferences", status_code=201)
async def save_user_preferences(
    preferences: UserPreferences,
    x_user_id: Optional[str] = Header(None)
):
    """
    保存用户偏好设置
    
    - 输入: 用户名和偏好设置
    - 输出: 成功状态
    """
    try:
        # 如果提供了用户名，使用它来查找或创建用户ID
        if preferences.username:
            user_id = await cosmos_client.get_user_id_by_username(preferences.username)
        elif x_user_id:
            user_id = x_user_id
        else:
            raise HTTPException(status_code=400, detail="必须提供用户名")
        
        # 准备偏好设置字典
        prefs_dict = {
            "mbti": preferences.mbti,
            "tone": preferences.tone,
            "age": preferences.age,
            "star_sign": preferences.star_sign
        }
        
        # 过滤掉None值
        prefs_dict = {k: v for k, v in prefs_dict.items() if v is not None}
        
        # 更新用户偏好设置
        await cosmos_client.update_user_preferences(user_id, prefs_dict)
        
        return {"success": True, "message": "用户偏好设置已保存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存偏好设置失败: {str(e)}")

@router.get("/{username}/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    username: str,
    x_user_id: Optional[str] = Header(None)
):
    """
    获取用户偏好设置
    
    - 输入: 用户名
    - 输出: 用户偏好设置
    """
    try:
        # 使用用户名查找用户ID
        user_id = await cosmos_client.get_user_id_by_username(username)
        
        # 获取用户配置文件
        profile = await cosmos_client.get_user_profile(user_id)
        
        return {
            "username": profile.get("username", username),
            "preferences": profile.get("preferences", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户偏好设置失败: {str(e)}") 