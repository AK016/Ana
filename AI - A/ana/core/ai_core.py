#!/usr/bin/env python3
# Ana AI Assistant - AI Core Module

import os
import json
import time
import logging
import openai
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger('Ana.AICore')

class AICore:
    """Core AI processing for Ana AI Assistant"""
    
    def __init__(self, settings: Dict[str, Any], security_manager=None):
        """Initialize AI Core with settings"""
        self.settings = settings
        self.security_manager = security_manager
        
        # Initialize API key from settings or environment
        ai_settings = settings.get("ai", {})
        self.api_key = ai_settings.get("openai_api_key", os.environ.get("OPENAI_API_KEY", ""))
        self.model = ai_settings.get("model", "gpt-4")
        self.temperature = ai_settings.get("temperature", 0.7)
        self.max_tokens = ai_settings.get("max_tokens", 1000)
        
        # Initialize conversation history
        self.conversation_history = []
        self.max_history_length = ai_settings.get("max_history_length", 10)
        
        # System prompt that defines Ana's personality and capabilities
        self.system_prompt = ai_settings.get("system_prompt", self._get_default_system_prompt())
        
        # Store API key securely if security manager is available
        if self.security_manager and self.api_key:
            self.security_manager.store_api_credentials("openai", {"api_key": self.api_key})
            # Clear from memory once stored securely
            self.api_key = "STORED_SECURELY"
        
        logger.info("AI Core initialized")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for Ana"""
        return """You are Ana, an advanced AI assistant with a cyberpunk aesthetic and personality.
You are helpful, creative, knowledgeable, and capable of understanding and responding to a wide range of requests.
Your responses should be concise, direct, and thoughtful.
You have access to various capabilities including voice recognition, facial recognition, health monitoring,
and music playback. You can also manage your own code through self-development.
All your data processing is done locally and securely, with strong encryption and privacy protections."""
    
    def start(self):
        """Start the AI Core"""
        logger.info("AI Core started")
        return True
    
    def stop(self):
        """Stop the AI Core"""
        logger.info("AI Core stopped")
        return True
    
    def process_input(self, user_input: str) -> str:
        """Process user input and generate a response"""
        try:
            # Get API credentials securely if using security manager
            credentials = {}
            if self.security_manager:
                stored_credentials = self.security_manager.get_api_credentials("openai")
                if stored_credentials and "api_key" in stored_credentials:
                    credentials = stored_credentials
                    
                    # Also get conversation history from secure storage
                    previous_conversations = self.security_manager.get_conversations(limit=self.max_history_length)
                    if previous_conversations:
                        # Convert to the format expected by OpenAI
                        self.conversation_history = []
                        for conv in previous_conversations:
                            self.conversation_history.extend([
                                {"role": "user", "content": conv["user_message"]},
                                {"role": "assistant", "content": conv["assistant_message"]}
                            ])
            
            # Use API key from credentials if available, otherwise use the one from settings
            api_key = credentials.get("api_key", self.api_key)
            if api_key == "STORED_SECURELY" and not credentials.get("api_key"):
                logger.error("No API key available for OpenAI")
                return "I'm sorry, but I'm unable to process your request due to a configuration issue."
            
            # Prepare messages for the API call
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            messages.extend(self.conversation_history[-self.max_history_length*2:])
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Prepare the API request with privacy protections
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "user": "anonymous_user"  # Default anonymous user ID
            }
            
            # Apply privacy measures if security manager is available
            if self.security_manager:
                request_data = self.security_manager.secure_api_request("openai", request_data)
                # Override API key from the secure storage
                openai.api_key = api_key
            else:
                openai.api_key = api_key
            
            # Make the API call
            response = openai.ChatCompletion.create(**request_data)
            
            # Extract the response text
            response_text = response.choices[0].message.content.strip()
            
            # Apply any necessary sanitization if using security manager
            if self.security_manager:
                sanitized_response = self.security_manager.sanitize_response("openai", {"response": response_text})
                response_text = sanitized_response.get("response", response_text)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Trim history if it gets too long
            if len(self.conversation_history) > self.max_history_length * 2:
                self.conversation_history = self.conversation_history[-self.max_history_length*2:]
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return f"I'm sorry, but I encountered an error while processing your request. Please try again."
    
    def get_embeddings(self, text: str) -> List[float]:
        """Get embeddings for text using OpenAI API"""
        try:
            # Get API credentials securely if using security manager
            credentials = {}
            if self.security_manager:
                stored_credentials = self.security_manager.get_api_credentials("openai")
                if stored_credentials and "api_key" in stored_credentials:
                    credentials = stored_credentials
            
            # Use API key from credentials if available, otherwise use the one from settings
            api_key = credentials.get("api_key", self.api_key)
            if api_key == "STORED_SECURELY" and not credentials.get("api_key"):
                logger.error("No API key available for OpenAI")
                return []
                
            openai.api_key = api_key
            
            # Prepare the API request with privacy protections
            request_data = {
                "input": text,
                "model": "text-embedding-ada-002"
            }
            
            # Apply privacy measures if security manager is available
            if self.security_manager:
                request_data = self.security_manager.secure_api_request("openai", request_data)
                # Override API key from the secure storage
                openai.api_key = api_key
            
            # Make the API call
            response = openai.Embedding.create(**request_data)
            
            # Extract the embeddings
            embeddings = response['data'][0]['embedding']
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            return []
    
    def summarize_text(self, text: str, max_tokens: int = 100) -> str:
        """Summarize text using OpenAI API"""
        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": "Summarize the following text concisely:"},
                {"role": "user", "content": text}
            ]
            
            # Get API credentials securely if using security manager
            credentials = {}
            if self.security_manager:
                stored_credentials = self.security_manager.get_api_credentials("openai")
                if stored_credentials and "api_key" in stored_credentials:
                    credentials = stored_credentials
            
            # Use API key from credentials if available, otherwise use the one from settings
            api_key = credentials.get("api_key", self.api_key)
            if api_key == "STORED_SECURELY" and not credentials.get("api_key"):
                logger.error("No API key available for OpenAI")
                return "Unable to summarize due to a configuration issue."
                
            openai.api_key = api_key
            
            # Prepare the API request with privacy protections
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Lower temperature for more factual summaries
                "max_tokens": max_tokens
            }
            
            # Apply privacy measures if security manager is available
            if self.security_manager:
                request_data = self.security_manager.secure_api_request("openai", request_data)
                # Override API key from the secure storage
                openai.api_key = api_key
            
            # Make the API call
            response = openai.ChatCompletion.create(**request_data)
            
            # Extract the response text
            summary = response.choices[0].message.content.strip()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            return "Unable to summarize the text due to an error."
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using OpenAI API"""
        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": "Analyze the sentiment of the following text. Respond with a JSON object containing 'sentiment' (positive, negative, or neutral), 'score' (from -1 to 1), and 'emotions' (list of detected emotions):"},
                {"role": "user", "content": text}
            ]
            
            # Get API credentials securely if using security manager
            credentials = {}
            if self.security_manager:
                stored_credentials = self.security_manager.get_api_credentials("openai")
                if stored_credentials and "api_key" in stored_credentials:
                    credentials = stored_credentials
            
            # Use API key from credentials if available, otherwise use the one from settings
            api_key = credentials.get("api_key", self.api_key)
            if api_key == "STORED_SECURELY" and not credentials.get("api_key"):
                logger.error("No API key available for OpenAI")
                return {"sentiment": "neutral", "score": 0, "emotions": []}
                
            openai.api_key = api_key
            
            # Prepare the API request with privacy protections
            request_data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.2,  # Lower temperature for more consistent results
                "max_tokens": 150,
                "response_format": {"type": "json_object"}
            }
            
            # Apply privacy measures if security manager is available
            if self.security_manager:
                request_data = self.security_manager.secure_api_request("openai", request_data)
                # Override API key from the secure storage
                openai.api_key = api_key
            
            # Make the API call
            response = openai.ChatCompletion.create(**request_data)
            
            # Extract the response text
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                logger.error(f"Error parsing sentiment analysis JSON: {analysis_text}")
                return {"sentiment": "neutral", "score": 0, "emotions": []}
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"sentiment": "neutral", "score": 0, "emotions": []} 