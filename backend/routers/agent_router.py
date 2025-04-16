#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from backend.services.agent_kernel import AgentKernel

# 设置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)

# Input model for analyze endpoint
class AnalysisRequest(BaseModel):
    user_id: str = Field(..., description="用户唯一标识符")
    text: str = Field(..., description="用户输入的文本内容")
    health_data: Optional[Dict[str, Any]] = Field(None, description="可选的健康数据, 如心率、睡眠等信息")

# Response model 
class AnalysisResponse(BaseModel):
    suggestion: str = Field(..., description="生成的回应或建议")
    emotion: str = Field(..., description="检测到的情绪类型")
    confidence: float = Field(..., description="情绪检测的置信度")
    context_used: Optional[bool] = Field(False, description="是否使用了上下文信息")
    
# Error response model
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="错误详情")
    error_type: str = Field(..., description="错误类型")
    timestamp: str = Field(..., description="错误发生时间")
    
# Singleton instance of AgentKernel
agent_kernel = AgentKernel()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_input(request: AnalysisRequest):
    """
    分析用户输入和健康数据以生成情感支持响应。
    
    - 输入: 用户文本和可选的Apple Watch健康指标
    - 处理: 情感分析、上下文检索、个性化建议
    - 输出: 包含建议的代理响应
    """
    try:
        logger.info(f"处理用户 {request.user_id} 的分析请求")
        
        # 使用agent_kernel分析输入
        result = await agent_kernel.analyze(
            user_id=request.user_id,
            text=request.text,
            health_data=request.health_data
        )
        
        logger.info(f"成功为用户 {request.user_id} 生成情感响应, 检测到的情绪: {result['emotion']}")
        
        # 标记是否使用了上下文
        if "context_used" not in result:
            result["context_used"] = True
            
        return result
    
    except ValueError as e:
        logger.warning(f"请求验证错误: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
        
    except Exception as e:
        logger.error(f"分析过程中出错: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """自定义HTTP异常处理"""
    import datetime
    
    error_response = ErrorResponse(
        detail=exc.detail,
        error_type="HTTPException",
        timestamp=datetime.datetime.now().isoformat()
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    ) 