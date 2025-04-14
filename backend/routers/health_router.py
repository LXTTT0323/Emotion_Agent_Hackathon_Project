from fastapi import APIRouter, HTTPException
import json
import os
from typing import Dict, Any
from pathlib import Path

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

@router.get("/mock_health/{user_id}")
async def get_mock_health_data(user_id: str) -> Dict[str, Any]:
    """
    Return mock health data for testing and development.
    In production, this would be replaced by real data from HealthKit.
    """
    try:
        # For absolute path, we can use the current file's location to determine the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        mock_data_path = os.path.join(project_root, "backend", "mock_data", "health_data_sample.json")
        
        # Check if mock data file exists, if not return placeholder data
        if not os.path.exists(mock_data_path):
            return {
                "heart_rate": {"avg": 75, "min": 62, "max": 110},
                "hrv": {"rmssd": 45.2, "sdnn": 52.8},
                "sleep": {"deep_sleep_minutes": 90, "total_minutes": 420},
                "steps": 8500,
                "menstrual_cycle": {"phase": "follicular", "day": 8},
                "timestamp": "2023-04-12T08:30:00Z"
            }
            
        # Load mock data from file
        with open(mock_data_path, "r") as f:
            mock_data = json.load(f)
            
        return mock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching health data: {str(e)}") 