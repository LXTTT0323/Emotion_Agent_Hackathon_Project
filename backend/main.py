from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# Add the parent directory to the path so we can import from the local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.routers import agent_router, health_router

app = FastAPI(
    title="Emotion Agent API",
    description="Backend for Emotion Agent iOS app",
    version="0.1.0"
)

# Configure CORS for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router.router)
app.include_router(health_router.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Emotion Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 