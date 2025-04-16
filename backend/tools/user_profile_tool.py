import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    Tool to fetch a user's profile information.
    
    In a real implementation, this would:
    1. Fetch profile data from a secure database
    2. Include personality traits, preferences, and communication style
    
    Input: user_id (string)
    Output: Dict with user profile information including MBTI, communication style,
            interests, zodiac sign, and other personalization attributes
    """
    # Determine the absolute path to the profile file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    profile_path = os.path.join(project_root, "backend", "memory", "user_profile.json")
    
    # Default profile if file not found
    default_profile = {
        "user_id": user_id,
        "creation_date": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "personality": {
            "mbti": "INFJ",
            "communication_style": "supportive",
            "zodiac_sign": "Pisces",
            "dominant_traits": ["empathetic", "introspective", "creative"]
        },
        "preferences": {
            "suggestion_tone": "gentle",
            "likes_creative_suggestions": True,
            "activity_preferences": ["meditation", "journaling", "breathing_exercises", "nature walks"],
            "notification_frequency": "medium",
            "response_length": "medium",  # short, medium, long
            "preferred_time_of_day": {
                "morning": True,
                "afternoon": True,
                "evening": True,
                "night": False
            }
        },
        "interests": {
            "categories": ["wellness", "mindfulness", "personal growth"],
            "specific_activities": ["yoga", "reading", "cooking"]
        },
        "health_goals": {
            "reduce_stress": True,
            "improve_sleep": True,
            "track_mood": True,
            "increase_activity": False,
            "improve_nutrition": False
        },
        "communication_preferences": {
            "metaphors": True,
            "direct_advice": True,
            "scientific_explanations": False,
            "inspirational_quotes": True
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
            # Ensure the profile has all the fields from default_profile
            user_profile = profiles[user_id]
            # Update with any missing default fields (deep merge)
            _deep_merge_defaults(user_profile, default_profile)
            return user_profile
        else:
            return default_profile
    except Exception as e:
        print(f"Error loading user profile: {str(e)}")
        return default_profile

async def update_user_profile(user_id: str, profile_updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool to update a user's profile information.
    
    Input: 
        - user_id (string)
        - profile_updates (dict) - partial profile updates to apply
    Output: Updated user profile
    """
    # Get current profile
    current_profile = await get_user_profile(user_id)
    
    # Determine the absolute path to the profile file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    profile_path = os.path.join(project_root, "backend", "memory", "user_profile.json")
    
    try:
        # Load all profiles
        profiles = {}
        if os.path.exists(profile_path):
            with open(profile_path, "r") as f:
                profiles = json.load(f)
        
        # Update specific profile
        _deep_merge(current_profile, profile_updates)
        current_profile["last_updated"] = datetime.now().isoformat()
        
        # Save back to profiles
        profiles[user_id] = current_profile
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        
        # Save to file
        with open(profile_path, "w") as f:
            json.dump(profiles, f, indent=2)
            
        return current_profile
    except Exception as e:
        print(f"Error updating user profile: {str(e)}")
        return current_profile

async def get_profile_attribute(user_id: str, attribute_path: str) -> Any:
    """
    Tool to fetch a specific attribute from a user's profile using dot notation.
    
    Example: "personality.mbti" would retrieve the MBTI from the personality section
    
    Input:
        - user_id (string)
        - attribute_path (string) - dot-separated path to the attribute
    Output: Value of the requested attribute or None if not found
    """
    profile = await get_user_profile(user_id)
    
    # Parse the path and retrieve the attribute
    parts = attribute_path.split('.')
    current = profile
    
    try:
        for part in parts:
            current = current[part]
        return current
    except (KeyError, TypeError):
        return None

def _deep_merge(target: Dict, source: Dict) -> Dict:
    """
    Recursively merge source dict into target dict
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value
    return target

def _deep_merge_defaults(target: Dict, defaults: Dict) -> Dict:
    """
    Recursively add default values to target dict if they don't exist
    """
    for key, value in defaults.items():
        if key not in target:
            target[key] = value
        elif isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge_defaults(target[key], value)
    return target 