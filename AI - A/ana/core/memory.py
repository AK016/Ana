#!/usr/bin/env python3
# Ana AI Assistant - Memory Manager (Minimal Implementation)

import os
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger('Ana.Memory')

class MemoryManager:
    """Minimal memory manager implementation for testing"""
    
    def __init__(self, settings: Dict[str, Any]):
        """Initialize memory manager with settings"""
        self.settings = settings
        self.conversations = []
        self.tasks = []
        self.reminders = []
        
        # Create memory directory if it doesn't exist
        self.memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "memory")
        os.makedirs(self.memory_dir, exist_ok=True)
        
        logger.info("Memory manager initialized")
    
    def initialize(self):
        """Initialize memory storage"""
        logger.info("Memory storage initialized")
        return True
    
    def add_user_message(self, text: str) -> bool:
        """Add user message to conversation history"""
        message = {
            "role": "user",
            "content": text,
            "timestamp": datetime.now().isoformat()
        }
        self.conversations.append(message)
        logger.info(f"Added user message: {text[:50]}...")
        return True
    
    def add_assistant_message(self, text: str) -> bool:
        """Add assistant message to conversation history"""
        message = {
            "role": "assistant",
            "content": text,
            "timestamp": datetime.now().isoformat()
        }
        self.conversations.append(message)
        logger.info(f"Added assistant message: {text[:50]}...")
        return True
    
    def get_last_assistant_message(self) -> Optional[Dict[str, Any]]:
        """Get the last message from the assistant"""
        for message in reversed(self.conversations):
            if message["role"] == "assistant":
                return message
        return None
    
    def shutdown(self):
        """Clean shutdown of memory manager"""
        logger.info("Memory manager shutdown")
        return True 