#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from typing import Dict, Any, Optional, List
import random
import json
from datetime import datetime

from backend.tools.fetch_emotion_context import analyze_emotion
from backend.tools.fetch_health_data import fetch_health_data
from backend.tools.user_profile_tool import get_user_profile
from backend.tools.intervene import generate_suggestion

class MockAgentKernel:
    """
    AgentKernel的模拟实现，用于测试和演示
    不依赖于Semantic Kernel，完全使用模拟数据
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化模拟 AgentKernel - 不使用真实的 Semantic Kernel")
    
    async def analyze(self, user_id: str, text: str, health_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分析用户输入和健康数据
        
        Args:
            user_id: 用户ID
            text: 用户输入文本
            health_data: 可选的健康数据
            
        Returns:
            分析结果，包含建议和情绪
        """
        try:
            self.logger.info(f"分析用户 {user_id} 的输入: '{text}'")
            
            # 步骤1：分析情绪
            emotion_result = await analyze_emotion(text)
            emotion = emotion_result["emotion"]
            confidence = emotion_result["confidence"]
            
            # 步骤2：如果没有提供健康数据，尝试获取
            if not health_data:
                health_data = await fetch_health_data(user_id)
            
            # 步骤3：获取用户资料
            user_profile = await get_user_profile(user_id)
            
            # 步骤4：生成建议
            suggestion_result = await generate_suggestion(
                emotion=emotion,
                confidence=confidence,
                health_data=health_data,
                user_profile=user_profile
            )
            
            # 返回结果
            return {
                "suggestion": suggestion_result["suggestion"],
                "emotion": emotion,
                "confidence": confidence,
                "context_used": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"分析过程中出错: {str(e)}", exc_info=True)
            # 提供一个后备响应
            return {
                "suggestion": "我无法完全理解您的情绪。您能告诉我更多关于您现在的感受吗？",
                "emotion": "uncertain",
                "confidence": 0.3,
                "context_used": False,
                "error": str(e)
            } 