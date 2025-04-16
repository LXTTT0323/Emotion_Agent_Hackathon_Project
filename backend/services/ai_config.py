#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

class AIConfig:
    """
    管理AI服务配置的类。
    负责加载环境变量并提供AI服务的配置参数。
    """
    
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 设置默认值
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1024"))
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
    def validate(self):
        """
        验证配置是否有效。
        如果缺少必要的配置，则抛出异常。
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in a .env file.")
            
    def get_chat_completion_config(self):
        """
        获取用于ChatCompletion的配置字典
        """
        return {
            "api_key": self.openai_api_key,
            "ai_model_id": self.openai_model,
            "temperature": self.openai_temperature,
            "max_tokens": self.openai_max_tokens
        }
        
    def __str__(self):
        """返回配置的字符串表示（不包含API密钥）"""
        return f"AIConfig(model={self.openai_model}, max_tokens={self.openai_max_tokens}, temperature={self.openai_temperature})" 