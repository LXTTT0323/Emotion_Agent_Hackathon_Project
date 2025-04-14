import os
from typing import Dict, Any, List
import json

# Imports for tools
from backend.tools.fetch_emotion_context import analyze_emotion
from backend.tools.fetch_health_data import fetch_health_data
from backend.tools.user_profile_tool import get_user_profile
from backend.tools.intervene import generate_suggestion
from backend.memory.context_store import ContextStore
from backend.services.tool_registry import ToolRegistry

# In a real implementation, this would use Semantic Kernel
# For now, we'll create a class that demonstrates the structure
class AgentKernel:
    def __init__(self):
        """
        Initialize the agent with tools and memory.
        
        In a full implementation, this would:
        1. Load API keys from environment
        2. Initialize Semantic Kernel
        3. Register all tools from tool_registry
        4. Connect to memory/context store
        """
        self.context_store = ContextStore()
        self.tool_registry = ToolRegistry()
        self.tools = self.tool_registry.get_tools()
        self.prompt_templates = {}
        
        # Load prompt templates
        self._load_prompts()
        
    def _load_prompts(self):
        """Load prompt templates from files"""
        try:
            # Determine the absolute path to the prompt template
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            prompt_path = os.path.join(project_root, "backend", "prompts", "empathy_prompt.txt")
            
            with open(prompt_path, "r") as f:
                self.prompt_templates["empathy"] = f.read()
        except FileNotFoundError:
            # Default template if file not found
            self.prompt_templates["empathy"] = """
            You are an empathetic AI assistant helping someone who is feeling {{emotion}}.
            Their physiological data shows {{health_context}}.
            Craft a gentle, supportive response that:
            - Acknowledges their feelings
            - Offers a suggestion based on their current state
            - Provides encouragement
            """
    
    async def analyze(self, user_id: str, text: str, health_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input through tool pipeline.
        
        1. Classify emotion in the text
        2. Retrieve health context from data
        3. Fetch user profile and preferences
        4. Generate a personalized suggestion
        5. Update memory/context with the interaction
        """
        # Step 1: Analyze emotion in the text
        emotion_result = await analyze_emotion(text)
        
        # Step 2: Get health data if not provided
        if health_data is None:
            health_data = await fetch_health_data(user_id)
        
        # Step 3: Get user profile
        user_profile = await get_user_profile(user_id)
        
        # Step 4: Get user context from memory
        user_context = await self.context_store.get_user_context(user_id)
        
        # Step 5: Generate suggestion based on emotion, health data, and user profile
        suggestion_result = await generate_suggestion(
            emotion=emotion_result["emotion"],
            confidence=emotion_result["confidence"],
            health_data=health_data,
            user_profile=user_profile
        )
        
        # Step 6: Store interaction in memory
        await self.context_store.add_interaction(
            user_id=user_id,
            text=text,
            emotion=emotion_result["emotion"],
            suggestion=suggestion_result["suggestion"]
        )
        
        # Return result
        return {
            "suggestion": suggestion_result["suggestion"],
            "emotion": emotion_result["emotion"],
            "confidence": emotion_result["confidence"]
        } 