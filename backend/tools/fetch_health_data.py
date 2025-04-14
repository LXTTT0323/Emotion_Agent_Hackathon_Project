from typing import Dict, Any
import json
import os
from pathlib import Path

async def fetch_health_data(user_id: str) -> Dict[str, Any]:
    """
    Tool to fetch health data for a user.
    
    In a real implementation, this would:
    1. Authenticate with the user's account
    2. Fetch real-time health data from HealthKit via the iOS app
    3. Process and return the structured data
    
    Input: user_id (string)
    Output: Dict with health metrics (heart rate, HRV, sleep, etc.)
    """
    # For now, we'll return mock data
    try:
        # Determine the absolute path to the mock data file
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
        print(f"Error fetching health data: {str(e)}")
        return {
            "error": f"Failed to fetch health data: {str(e)}"
        } 