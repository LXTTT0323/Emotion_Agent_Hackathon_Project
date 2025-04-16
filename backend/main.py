#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import logging
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.routers import agent_router, health_router
from backend.services.logging_config import setup_logging, get_default_log_file

# 设置日志
setup_logging(log_file=get_default_log_file())
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 配置应用
app = FastAPI(
    title="Emotion Agent API",
    description="Backend for Emotion Agent iOS app with Semantic Kernel integration",
    version="0.2.0"
)

# Configure CORS for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("Emotion Agent API 正在启动...")
    
    # 验证环境配置
    try:
        from backend.services.ai_config import AIConfig
        config = AIConfig()
        config.validate()
        logger.info(f"AI配置验证成功: {config}")
    except Exception as e:
        logger.warning(f"AI配置验证失败: {str(e)}. 某些功能可能无法正常工作。")
        
    # 加载记忆系统
    try:
        from backend.memory.context_store import ContextStore
        context_store = ContextStore()
        users = context_store.get_users()
        logger.info(f"记忆系统加载成功. 找到 {len(users)} 个用户。")
    except Exception as e:
        logger.error(f"记忆系统加载失败: {str(e)}")
        
    logger.info("Emotion Agent API 启动完成!")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Emotion Agent API 正在关闭...")

# Include routers
app.include_router(agent_router.router)
app.include_router(health_router.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Emotion Agent API",
        "version": "0.2.0",
        "features": [
            "Emotion analysis",
            "Personalized suggestions",
            "Health data integration",
            "Memory context awareness",
            "Semantic Kernel integration"
        ]
    }

# 添加健康检查端点
@app.get("/health")
async def health_check():
    # 这里可以添加更多健康检查逻辑
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取主机和端口
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"启动服务器于 {host}:{port}")
    uvicorn.run(app, host=host, port=port) 