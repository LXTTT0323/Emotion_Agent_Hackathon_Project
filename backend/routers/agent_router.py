from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from services.agent_kernel import AgentKernel

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)

# Input model for analyze endpoint
class AnalysisRequest(BaseModel):
    user_id: str
    text: str
    health_data: Optional[Dict[str, Any]] = None

# Response model 
class AnalysisResponse(BaseModel):
    suggestion: str
    emotion: str
    confidence: float
    
# Singleton instance of AgentKernel
agent_kernel = AgentKernel()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_input(request: AnalysisRequest):
    """
    Analyze user input and health data to generate an emotionally supportive response.
    
    - Input: User text and optional health metrics from Apple Watch
    - Process: Emotion analysis, context retrieval, personalized suggestion
    - Output: Agent response with suggestion
    """
    try:
        # Use the agent_kernel to analyze the input
        result = await agent_kernel.analyze(
            user_id=request.user_id,
            text=request.text,
            health_data=request.health_data
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") 