import sys
import os
import unittest
import json
from pathlib import Path
import asyncio

# Add parent directory to path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.memory.context_store import ContextStore

class TestContextStore(unittest.TestCase):
    def setUp(self):
        # Create a temporary memory file for testing
        self.test_memory_path = "tests/test_memory.json"
        self.context_store = ContextStore(memory_path=self.test_memory_path)
    
    def tearDown(self):
        # Clean up the test memory file
        if Path(self.test_memory_path).exists():
            os.remove(self.test_memory_path)
    
    def test_memory_initialization(self):
        """Test that the memory store initializes correctly"""
        self.assertEqual(self.context_store.memory, {"users": {}})
    
    def test_add_interaction(self):
        """Test adding a new interaction to memory"""
        # Use asyncio to run the async method
        asyncio.run(self.context_store.add_interaction(
            user_id="test_user",
            text="I'm feeling happy today!",
            emotion="happy",
            suggestion="That's great! Keep up the positive energy."
        ))
        
        # Check that the interaction was added
        self.assertIn("test_user", self.context_store.memory["users"])
        self.assertEqual(len(self.context_store.memory["users"]["test_user"]["interactions"]), 1)
        self.assertEqual(
            self.context_store.memory["users"]["test_user"]["interactions"][0]["emotion"],
            "happy"
        )
    
    def test_get_user_context(self):
        """Test retrieving user context"""
        # First add an interaction
        asyncio.run(self.context_store.add_interaction(
            user_id="test_user",
            text="I'm feeling stressed about work.",
            emotion="anxious",
            suggestion="Taking deep breaths might help reduce your stress."
        ))
        
        # Now retrieve the context
        context = asyncio.run(self.context_store.get_user_context("test_user"))
        
        # Check that we got the correct context
        self.assertTrue(context["has_context"])
        self.assertEqual(context["emotion_history"][0]["emotion"], "anxious")
    
    def test_get_nonexistent_user(self):
        """Test retrieving context for a user that doesn't exist"""
        context = asyncio.run(self.context_store.get_user_context("nonexistent_user"))
        
        # Check that we got an empty context with has_context = False
        self.assertFalse(context["has_context"])
        self.assertEqual(context["interactions"], [])

if __name__ == "__main__":
    unittest.main() 