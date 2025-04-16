#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from typing import Dict, Any, List

class PromptService:
    """
    管理提示模板的服务类。
    负责加载、格式化和管理提示模板。
    """
    
    def __init__(self, prompts_dir: str = None):
        self.logger = logging.getLogger(__name__)
        
        # 设置提示模板目录
        if prompts_dir is None:
            # 默认使用backend/prompts目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            self.prompts_dir = os.path.join(backend_dir, "prompts")
        else:
            self.prompts_dir = prompts_dir
            
        self.prompts = {}
        self._load_prompts()
        
    def _load_prompts(self):
        """加载所有提示模板文件"""
        try:
            # 确保目录存在
            if not os.path.exists(self.prompts_dir):
                self.logger.warning(f"Prompts directory not found: {self.prompts_dir}")
                return
                
            # 遍历目录加载所有.txt和.prompt文件
            for filename in os.listdir(self.prompts_dir):
                if filename.endswith(('.txt', '.prompt')):
                    prompt_name = os.path.splitext(filename)[0]
                    prompt_path = os.path.join(self.prompts_dir, filename)
                    
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        self.prompts[prompt_name] = f.read()
                        
                    self.logger.info(f"Loaded prompt template: {prompt_name}")
                    
        except Exception as e:
            self.logger.error(f"Error loading prompts: {str(e)}")
            raise
            
    def get_prompt(self, name: str) -> str:
        """
        获取指定名称的提示模板
        
        Args:
            name: 提示模板名称
            
        Returns:
            提示模板文本
        """
        if name not in self.prompts:
            raise ValueError(f"Prompt template not found: {name}")
            
        return self.prompts[name]
        
    def format_prompt_for_semantic_kernel(self, prompt_text: str) -> str:
        """
        将提示模板格式化为Semantic Kernel可用的格式
        
        Args:
            prompt_text: 原始提示模板文本
            
        Returns:
            格式化后的提示模板
        """
        # 将Jinja2风格的模板转换为Semantic Kernel格式
        # 例如：{{ variable }} -> {{$variable}}
        import re
        
        # 替换Jinja变量格式
        sk_prompt = re.sub(r'{{\s*([^}]+)\s*}}', r'{{$\1}}', prompt_text)
        
        # 替换Jinja条件和循环格式为注释
        sk_prompt = re.sub(r'{%.*?%}', '', sk_prompt)
        
        return sk_prompt
        
    def get_formatted_prompt(self, name: str) -> str:
        """
        获取格式化后的提示模板
        
        Args:
            name: 提示模板名称
            
        Returns:
            格式化后的提示模板文本
        """
        prompt_text = self.get_prompt(name)
        return self.format_prompt_for_semantic_kernel(prompt_text) 