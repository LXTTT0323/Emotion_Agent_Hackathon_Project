from typing import Dict, Any, List, Callable

# Import tools
from backend.tools.fetch_emotion_context import analyze_emotion
from backend.tools.fetch_health_data import fetch_health_data
from backend.tools.user_profile_tool import get_user_profile
from backend.tools.intervene import generate_suggestion
from backend.tools.should_trigger_breathing_tool import should_trigger_breathing_tool


class ToolRegistry:
    """
    Registry for all tools that can be used by the agent.

    In a full implementation with Semantic Kernel, this would:
    1. Import all tools from the tools/ directory
    2. Register them with Semantic Kernel
    3. Provide descriptions and signatures for the LLM to use them
    """

    def __init__(self):
        self.tools = {}
        self.register_all_tools()

    def register_tool(self, name: str, function: Callable, description: str):
        """Register a tool with the registry"""
        self.tools[name] = {
            "function": function,
            "description": description
        }

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered tools"""
        return self.tools

    def register_all_tools(self):
        """
        Import and register all tools.
        """
        # Register emotion analysis tool
        self.register_tool(
            name="analyze_emotion",
            function=analyze_emotion,
            description="Analyzes text to identify the user's emotional state and confidence level."
        )

        # Register health data tool
        self.register_tool(
            name="fetch_health_data",
            function=fetch_health_data,
            description="Fetches health data for a user, including heart rate, HRV, sleep, etc."
        )

        # Register user profile tool
        self.register_tool(
            name="get_user_profile",
            function=get_user_profile,
            description="Retrieves a user's profile information, including preferences and health goals."
        )

        # Register intervention tool
        self.register_tool(
            name="generate_suggestion",
            function=generate_suggestion,
            description="Generates a supportive suggestion based on emotion and health data."
        )

        # Register breathing tool
        self.register_tool(
            name="should_trigger_breathing_tool",
            function=should_trigger_breathing_tool,
            description="Determines if the breathing tool should be triggered based on the user's emotional state and health data."
        )
