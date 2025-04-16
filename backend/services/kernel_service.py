#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from typing import Dict, Any

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.template_engine.prompt_template_engine import PromptTemplateEngine

from backend.services.ai_config import AIConfig

class KernelService:
    """
    管理Semantic Kernel服务的类。
    负责初始化Kernel、注册AI服务和插件。
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_config = AIConfig()
        self.ai_config.validate()
        
        # 初始化Semantic Kernel
        self.kernel = sk.Kernel()
        self._setup_kernel()
        
    def _setup_kernel(self):
        """设置Semantic Kernel并注册服务"""
        try:
            # 获取配置
            config = self.ai_config.get_chat_completion_config()
            
            # 添加AI聊天服务
            self.kernel.add_chat_service(
                "default", 
                OpenAIChatCompletion(
                    service_id="default",
                    ai_model_id=config["ai_model_id"],
                    api_key=config["api_key"]
                )
            )
            
            self.logger.info(f"Semantic Kernel initialized with model: {config['ai_model_id']}")
        
        except Exception as e:
            self.logger.error(f"Error setting up Semantic Kernel: {str(e)}")
            raise
            
    def register_semantic_function(self, plugin_name: str, function_name: str, prompt_template: str):
        """
        注册语义函数到Kernel
        
        Args:
            plugin_name: 插件名称
            function_name: 函数名称
            prompt_template: 提示模板文本
        
        Returns:
            注册的函数
        """
        try:
            # 创建语义函数
            return self.kernel.create_semantic_function(
                prompt_template, 
                plugin_name=plugin_name,
                function_name=function_name
            )
        except Exception as e:
            self.logger.error(f"Error registering semantic function {plugin_name}.{function_name}: {str(e)}")
            raise
            
    def register_native_function(self, plugin_name: str, function):
        """
        注册原生函数到Kernel
        
        Args:
            plugin_name: 插件名称
            function: 要注册的函数
        """
        try:
            # 将函数注册为Kernel的原生函数
            self.kernel.add_plugin(function, plugin_name)
            self.logger.info(f"Registered native function: {plugin_name}.{function.__name__}")
        except Exception as e:
            self.logger.error(f"Error registering native function {function.__name__}: {str(e)}")
            raise
    
    async def execute_function(self, plugin_name: str, function_name: str, variables: Dict[str, Any] = None):
        """
        执行注册在Kernel中的函数
        
        Args:
            plugin_name: 插件名称
            function_name: 函数名称
            variables: 变量字典
            
        Returns:
            执行结果
        """
        try:
            # 创建变量集合
            context = self.kernel.create_new_context()
            
            if variables:
                for key, value in variables.items():
                    context[key] = str(value)
            
            # 获取并执行函数
            function = self.kernel.plugins[plugin_name][function_name]
            result = await self.kernel.run_async(function, input_vars=context.variables)
            
            return result
        except Exception as e:
            self.logger.error(f"Error executing function {plugin_name}.{function_name}: {str(e)}")
            raise 