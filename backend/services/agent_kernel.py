#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from typing import Dict, Any, List
import json

# 导入工具和服务
from backend.tools.fetch_emotion_context import analyze_emotion
from backend.tools.fetch_health_data import fetch_health_data
from backend.tools.user_profile_tool import get_user_profile
from backend.tools.intervene import generate_suggestion
from backend.memory.context_store import ContextStore
from backend.services.tool_registry import ToolRegistry
from backend.services.kernel_service import KernelService
from backend.services.prompt_service import PromptService

class AgentKernel:
    def __init__(self):
        """
        初始化代理，集成工具、记忆和Semantic Kernel。
        
        1. 加载环境变量和API密钥
        2. 初始化Semantic Kernel
        3. 注册所有工具
        4. 连接到记忆/上下文存储
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化服务和工具
        self.context_store = ContextStore()
        self.tool_registry = ToolRegistry()
        self.kernel_service = KernelService()
        self.prompt_service = PromptService()
        
        # 注册工具和语义函数
        self._register_tools()
        self._register_semantic_functions()
        
    def _register_tools(self):
        """将工具注册到Semantic Kernel"""
        self.logger.info("注册工具到Semantic Kernel...")
        tools = self.tool_registry.get_tools()
        
        for name, tool_info in tools.items():
            self.kernel_service.register_native_function(
                plugin_name="tools",
                function=tool_info["function"]
            )
    
    def _register_semantic_functions(self):
        """注册语义函数到Semantic Kernel"""
        self.logger.info("注册语义函数到Semantic Kernel...")
        
        # 注册情感支持提示
        try:
            empathy_prompt = self.prompt_service.get_formatted_prompt("empathy_prompt")
            self.kernel_service.register_semantic_function(
                plugin_name="agent",
                function_name="generate_empathic_response",
                prompt_template=empathy_prompt
            )
            self.logger.info("成功注册情感支持提示模板")
        except Exception as e:
            self.logger.warning(f"无法注册情感支持提示模板: {str(e)}")
            # 使用备用提示
            fallback_prompt = """
            你是一位富有同理心的AI助手，正在帮助一位感到{{$emotion}}的人。
            
            他们的文字: "{{$user_text}}"
            
            他们的生理数据显示:
            - 心率: {{$heart_rate}} bpm
            - 心率变异性: {{$hrv}} ms
            - 睡眠时间: {{$sleep_minutes}} 分钟
            
            请写一个温和、支持性的回应，要:
            1. 理解他们的感受，不加评判
            2. 根据他们的情绪状态和生理数据提出建议
            3. 提供鼓励，同时尊重他们的自主性
            
            你的回应应该温暖、对话式，并且简洁(2-3句话)。
            """
            self.kernel_service.register_semantic_function(
                plugin_name="agent",
                function_name="generate_empathic_response",
                prompt_template=fallback_prompt
            )
            self.logger.info("已使用备用情感支持提示模板")
    
    async def analyze(self, user_id: str, text: str, health_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        通过工具管道处理用户输入。
        
        1. 对文本进行情感分类
        2. 从数据中检索健康上下文
        3. 获取用户资料和偏好
        4. 生成个性化建议
        5. 用交互更新记忆/上下文
        """
        try:
            # 步骤1: 分析文本中的情感
            emotion_result = await analyze_emotion(text)
            
            # 步骤2: 如果未提供健康数据，则获取
            if health_data is None:
                health_data = await fetch_health_data(user_id)
            
            # 步骤3: 获取用户资料
            user_profile = await get_user_profile(user_id)
            
            # 步骤4: 从记忆中获取用户上下文
            user_context = await self.context_store.get_recent_emotions(user_id)
            
            # 步骤5: 通过Semantic Kernel生成建议
            variables = {
                "user_id": user_id,
                "user_text": text,
                "emotion": emotion_result["emotion"],
                "confidence": str(emotion_result["confidence"]),
                "heart_rate": str(health_data.get("heart_rate", {}).get("avg", 0)),
                "hrv": str(health_data.get("hrv", {}).get("rmssd", 0)),
                "sleep_minutes": str(health_data.get("sleep", {}).get("total_minutes", 0)),
                "user_profile": json.dumps(user_profile, ensure_ascii=False)
            }
            
            # 添加情绪历史上下文
            if user_context:
                emotion_history = [
                    {
                        "timestamp": entry["timestamp"],
                        "emotion": entry["emotion"]
                    } for entry in user_context
                ]
                variables["emotion_history"] = json.dumps(emotion_history, ensure_ascii=False)
            
            # 使用Semantic Kernel执行情感支持功能
            result = await self.kernel_service.execute_function(
                plugin_name="agent",
                function_name="generate_empathic_response",
                variables=variables
            )
            
            suggestion = str(result).strip()
            
            # 步骤6: 将交互存储在记忆中
            await self.context_store.add_interaction(
                user_id=user_id,
                text=text,
                emotion=emotion_result["emotion"],
                suggestion=suggestion,
                confidence=emotion_result["confidence"]
            )
            
            # 返回结果
            return {
                "suggestion": suggestion,
                "emotion": emotion_result["emotion"],
                "confidence": emotion_result["confidence"]
            }
        
        except Exception as e:
            self.logger.error(f"分析过程中出错: {str(e)}")
            
            # 返回简单回退响应
            return {
                "suggestion": "我现在无法准确分析您的情绪。请告诉我更多关于您感受的信息，以便我能更好地帮助您。",
                "emotion": "neutral",
                "confidence": 0.5
            } 