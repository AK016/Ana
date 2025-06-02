#!/usr/bin/env python3
# Ana AI Assistant - Intent Parser (Minimal Implementation)

import os
import logging
import json
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger('Ana.IntentParser')

class IntentParser:
    """Minimal intent parser implementation for testing"""
    
    def __init__(self, settings: Dict[str, Any]):
        """Initialize intent parser with settings"""
        self.settings = settings
        
        # Load intents from file
        self.intents_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "intents.json")
        self.intents = self._load_intents()
        
        logger.info("Intent parser initialized")
    
    def _load_intents(self) -> Dict[str, Any]:
        """Load intents from JSON file if available"""
        try:
            if os.path.exists(self.intents_file):
                with open(self.intents_file, 'r') as f:
                    return json.load(f)
            else:
                # Create empty intents structure
                return {
                    "intents": {
                        "greeting": {
                            "patterns": ["hello", "hi", "hey", "good morning", "good evening"],
                            "responses": ["Hello, Master.", "Greetings, Master.", "At your service, Master."],
                        },
                        "weather": {
                            "patterns": ["weather", "what's the weather like", "temperature"],
                            "responses": ["Let me check the weather for you, Master."],
                        },
                        "thanks": {
                            "patterns": ["thank you", "thanks", "appreciate it"],
                            "responses": ["You're welcome, Master.", "My pleasure, Master."],
                        }
                    }
                }
        except Exception as e:
            logger.error(f"Error loading intents: {str(e)}")
            return {"intents": {}}
    
    def parse(self, text: str) -> Tuple[str, List[Dict[str, Any]], Optional[str]]:
        """
        Parse user input and determine intent
        
        Returns:
            Tuple of (response, actions, emotion)
        """
        text = text.lower()
        
        # Very simple intent matching
        for intent_name, intent_data in self.intents.get("intents", {}).items():
            patterns = intent_data.get("patterns", [])
            
            for pattern in patterns:
                if pattern.lower() in text:
                    responses = intent_data.get("responses", [])
                    response = responses[0] if responses else f"I understand you want to {intent_name}."
                    
                    # Simple action example for weather intent
                    actions = []
                    if intent_name == "weather":
                        actions = [{"type": "weather", "action": "get_weather"}]
                    
                    # Determine emotion based on intent
                    emotion = None
                    if intent_name == "greeting":
                        emotion = "happy"
                    elif intent_name == "thanks":
                        emotion = "happy"
                    
                    logger.info(f"Detected intent: {intent_name}")
                    return response, actions, emotion
        
        # Default response if no intent matches
        return "I'm not sure I understand. Could you rephrase that, Master?", [], None 