import json
import os
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

class ContextStore:
    """
    Manages contextual memory for the agent.
    
    In a full implementation, this would:
    1. Maintain a history of user interactions and emotions
    2. Store contextual information about user state
    3. Provide retrieval mechanisms for relevant context
    """
    
    def __init__(self, memory_path: str = None):
        if memory_path is None:
            # Determine the absolute path to the memory file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            memory_path = os.path.join(project_root, "backend", "memory", "memory.json")
            
        self.memory_path = Path(memory_path)
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file or initialize if doesn't exist"""
        if not self.memory_path.exists():
            return {"users": {}}
            
        try:
            with open(self.memory_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {str(e)}")
            return {"users": {}}
    
    def _save_memory(self):
        """Save memory to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            with open(self.memory_path, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {str(e)}")
    
    async def add_interaction(self, user_id: str, text: str, emotion: str, suggestion: str):
        """Record a new interaction with a user"""
        if user_id not in self.memory["users"]:
            self.memory["users"][user_id] = {
                "interactions": [],
                "emotion_history": [],
                "last_active": None
            }
            
        # Add new interaction
        self.memory["users"][user_id]["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "emotion": emotion,
            "suggestion": suggestion
        })
        
        # Update emotion history
        self.memory["users"][user_id]["emotion_history"].append({
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion
        })
        
        # Limit history size (keep last 20 interactions)
        if len(self.memory["users"][user_id]["interactions"]) > 20:
            self.memory["users"][user_id]["interactions"] = self.memory["users"][user_id]["interactions"][-20:]
            
        # Update last active timestamp
        self.memory["users"][user_id]["last_active"] = datetime.now().isoformat()
        
        # Save changes
        self._save_memory()
        
    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get contextual information for a user"""
        if user_id not in self.memory["users"]:
            return {
                "interactions": [],
                "emotion_history": [],
                "last_active": None,
                "has_context": False
            }
            
        return {
            **self.memory["users"][user_id],
            "has_context": True
        }
        
    async def get_recent_emotions(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取用户最近的情绪记录
        
        Args:
            user_id: 用户ID
            limit: 返回的记录数量限制
            
        Returns:
            包含时间戳、情绪和置信度的记录列表
        """
        if user_id not in self.memory["users"]:
            return []
            
        # 获取情绪历史
        emotion_history = self.memory["users"][user_id].get("emotion_history", [])
        
        # 返回最近的n条记录
        recent_emotions = emotion_history[-limit:] if emotion_history else []
        
        # 确保每条记录都有置信度字段
        for emotion in recent_emotions:
            if "confidence" not in emotion:
                emotion["confidence"] = 0.8  # 默认置信度
                
        return recent_emotions 