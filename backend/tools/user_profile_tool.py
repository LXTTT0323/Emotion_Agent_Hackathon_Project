import json
import os
from typing import Dict, Any
from pathlib import Path

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Tool to fetch a user's profile information.
    
    In a real implementation, this would:
    1. Fetch profile data from a secure database
    2. Include personality traits, preferences, and communication style
    
    Input: user_id (string)
    Output: Dict with user profile information
    """
    # Determine the absolute path to the profile file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    profile_path = os.path.join(project_root, "backend", "memory", "user_profile.json")
    
    # Default profile if file not found
    default_profile = {
        "user_id": user_id,
        "personality": {
            "mbti": "INFJ",
            "communication_style": "supportive"
        },
        "preferences": {
            "suggestion_tone": "gentle",
            "likes_creative_suggestions": True,
            "activity_preferences": ["meditation", "journaling", "breathing_exercises"],
            "notification_frequency": "medium"
        },
        "health_goals": {
            "reduce_stress": True,
            "improve_sleep": True,
            "track_mood": True
        }
    }
    
    try:
        # Check if file exists
        if not os.path.exists(profile_path):
            return default_profile
            
        # Load profile from file
        with open(profile_path, "r") as f:
            profiles = json.load(f)
            
        # Find profile for specific user
        if user_id in profiles:
            return profiles[user_id]
        else:
            return default_profile
    except Exception as e:
        print(f"Error loading user profile: {str(e)}")
        return default_profile 