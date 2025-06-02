#!/usr/bin/env python3
# Ana AI Assistant - Core Assistant Module

import os
import time
import logging
import threading
import asyncio
from datetime import datetime

# Import core modules
from core.voice_engine import VoiceEngine, VoiceLanguage, VoiceEmotion
from core.memory import MemoryManager
from core.intent_parser import IntentParser
from core.updater import Updater
from core.self_dev import SelfEvolution
from core.events import register_event_handler
from core.weather_api import WeatherAPI

logger = logging.getLogger('Ana.Assistant')

class AnaAssistant:
    """Core class for Ana AI Assistant"""
    
    def __init__(self, settings):
        """Initialize Ana Assistant with settings"""
        self.settings = settings
        self.name = settings["assistant"]["name"]
        self.wake_word = settings["assistant"]["wake_word"]
        self.running = False
        self.listening = False
        self.speaking = False
        self.processing = False
        self.user_title = "Master"  # Default form of address
        
        # Initialize components
        self.voice_engine = VoiceEngine(settings)
        self.memory = MemoryManager(settings)
        self.intent_parser = IntentParser(settings)
        self.updater = Updater(settings)
        self.self_evolution = SelfEvolution(settings)
        
        # Initialize weather API
        self.weather_api = WeatherAPI(settings=settings)
        self.last_weather_update = 0
        self.current_weather = None
        self.weather_location = settings.get("assistant", {}).get("weather_location", "New York")
        
        # Event hooks
        self.on_wake_callbacks = []
        self.on_listen_callbacks = []
        self.on_process_callbacks = []
        self.on_speak_callbacks = []
        self.on_idle_callbacks = []
        self.on_face_detected_callbacks = []
        
        # State variables
        self.last_interaction = time.time()
        self.face_detected = False
        self.user_mood = "neutral"
        
        # Register for wake word event
        register_event_handler("wake_word_detected", self.on_wake_word_detected)
        
        logger.info(f"{self.name} initialized")
    
    def start_services(self):
        """Start all assistant services"""
        logger.info("Starting assistant services...")
        self.running = True
        
        # Initialize services in separate threads
        threading.Thread(target=self.memory.initialize, daemon=True).start()
        
        # Check for updates
        if self.settings["assistant"]["self_evolution"]["auto_update"]:
            threading.Thread(target=self.updater.check_for_updates, daemon=True).start()
        
        # Start voice engine in separate thread
        threading.Thread(target=self.voice_engine.initialize, daemon=True).start()
        
        # Initialize weather data
        threading.Thread(target=self._update_weather_data, daemon=True).start()
        
        # Start main assistant loop
        threading.Thread(target=self._assistant_loop, daemon=True).start()
        
        # Start facial recognition if enabled
        if self.settings["features"]["facial_recognition"]["enabled"]:
            threading.Thread(target=self._start_facial_recognition, daemon=True).start()
        
        # Speak introduction
        self.greet_user()
    
    def _assistant_loop(self):
        """Main assistant loop that handles periodic tasks"""
        while self.running:
            # Perform periodic tasks here
            time.sleep(1)
            
            # Check idle time for idle animations
            idle_time = time.time() - self.last_interaction
            if idle_time > 30 and not self.speaking and not self.listening:
                self._trigger_callbacks(self.on_idle_callbacks)
            
            # Update weather data periodically (every 30 minutes)
            if time.time() - self.last_weather_update > 1800:
                threading.Thread(target=self._update_weather_data, daemon=True).start()
    
    def _update_weather_data(self):
        """Update weather data from API"""
        try:
            self.current_weather = self.weather_api.get_current_weather(self.weather_location)
            self.last_weather_update = time.time()
            logger.info(f"Weather updated for {self.weather_location}")
        except Exception as e:
            logger.error(f"Error updating weather: {str(e)}")
    
    def get_weather_info(self):
        """Get current weather information"""
        # Update if data is old or doesn't exist
        if not self.current_weather or time.time() - self.last_weather_update > 1800:
            self._update_weather_data()
        
        return self.current_weather.get("current", {}) if self.current_weather else None
    
    def get_weather_condition(self):
        """Get current weather condition string"""
        weather_info = self.get_weather_info()
        if weather_info:
            return weather_info.get("condition", "").lower()
        return "clear"  # Default if no data
    
    def set_weather_location(self, location):
        """Set the weather location"""
        self.weather_location = location
        
        # Update settings
        if "assistant" in self.settings:
            self.settings["assistant"]["weather_location"] = location
        
        # Update weather data for new location
        threading.Thread(target=self._update_weather_data, daemon=True).start()
        
        return True
    
    def _start_facial_recognition(self):
        """Start facial recognition in background"""
        try:
            from core.facial_recognition import FacialRecognition
            
            facial_recognition = FacialRecognition(self.settings)
            facial_recognition.on_face_detected = self._on_face_detected
            facial_recognition.on_face_lost = self._on_face_lost
            facial_recognition.on_emotion_detected = self._on_emotion_detected
            
            facial_recognition.start()
            logger.info("Facial recognition started")
        except ImportError:
            logger.warning("Facial recognition module not available")
        except Exception as e:
            logger.error(f"Error starting facial recognition: {str(e)}")
    
    def _on_face_detected(self, face_data):
        """Handle face detection event"""
        if not self.face_detected:
            self.face_detected = True
            self._trigger_callbacks(self.on_face_detected_callbacks)
            
            # Greet user if not recently interacted
            if time.time() - self.last_interaction > 60:
                self.speak(f"Welcome back, {self.user_title}. It's good to see you.")
    
    def _on_face_lost(self):
        """Handle face lost event"""
        self.face_detected = False
    
    def _on_emotion_detected(self, emotion):
        """Handle emotion detection"""
        previous_mood = self.user_mood
        self.user_mood = emotion
        
        # Only react if the mood changed significantly
        if emotion != previous_mood:
            logger.info(f"User emotion changed from {previous_mood} to {emotion}")
            
            # Set the voice emotion based on user's mood
            voice_emotion = self._map_user_emotion_to_voice_emotion(emotion)
            self.voice_engine.set_emotion(voice_emotion)
            
            # React to user's mood if it changed to happy
            if emotion == "happy" and previous_mood != "happy":
                self.speak(f"You seem cheerful today, {self.user_title}. That makes me happy too.")
            # React to user's mood if it changed to sad
            elif emotion == "sad" and previous_mood != "sad":
                self.speak(f"Is everything alright, {self.user_title}? I'm here if you need anything.")
    
    def _map_user_emotion_to_voice_emotion(self, user_emotion):
        """Map user emotion to voice emotion for appropriate response"""
        emotion_map = {
            "neutral": VoiceEmotion.NEUTRAL,
            "happy": VoiceEmotion.HAPPY,
            "sad": VoiceEmotion.CONCERNED,
            "angry": VoiceEmotion.SERIOUS,
            "surprised": VoiceEmotion.EXCITED
        }
        return emotion_map.get(user_emotion, VoiceEmotion.NEUTRAL)
    
    def greet_user(self):
        """Greet the user based on time of day"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greeting = "Good morning"
            voice_emotion = VoiceEmotion.HAPPY
        elif 12 <= hour < 18:
            greeting = "Good afternoon"
            voice_emotion = VoiceEmotion.NEUTRAL
        else:
            greeting = "Good evening"
            voice_emotion = VoiceEmotion.NEUTRAL
        
        # Add weather info if available
        weather_info = ""
        try:
            if self.current_weather:
                current = self.current_weather.get("current", {})
                condition = current.get("condition", "").lower()
                temp = current.get("temp", 0)
                
                if condition and temp:
                    weather_info = f" It's {temp:.1f}°C and {condition} outside today."
        except Exception as e:
            logger.error(f"Error adding weather to greeting: {str(e)}")
            
        message = f"{greeting}, {self.user_title}.{weather_info} What would you like do to today?"
        self.speak(message, emotion=voice_emotion)
    
    def listen(self):
        """Activate listening mode"""
        if self.speaking:
            return False
            
        self.listening = True
        self.last_interaction = time.time()
        self._trigger_callbacks(self.on_listen_callbacks)
        
        # Use voice engine to listen
        text = self.voice_engine.listen()
        self.listening = False
        
        if text:
            self.process_input(text)
            return True
        return False
    
    def process_input(self, text):
        """Process user input text"""
        logger.info(f"Processing input: {text}")
        self.processing = True
        self.last_interaction = time.time()
        self._trigger_callbacks(self.on_process_callbacks)
        
        # Add to memory
        self.memory.add_user_message(text)
        
        # Process with intent parser
        response, actions, emotion = self.intent_parser.parse(text)
        
        # Execute any actions
        if actions:
            self._execute_actions(actions)
        
        # Process response with appropriate emotion
        if response:
            # Replace generic terms with formal address
            response = self._add_formal_address(response)
            self.memory.add_assistant_message(response)
            
            # Determine voice emotion if not specified by intent parser
            if not emotion:
                emotion = self._determine_response_emotion(text, response)
                
            # Speak with the determined emotion
            self.speak(response, emotion=emotion)
        
        self.processing = False
    
    def _add_formal_address(self, text):
        """Add formal address to responses when appropriate"""
        import random
        
        # List of phrases to replace
        replacements = {
            "Hello!": f"Hello, {self.user_title}!",
            "Hi there!": f"Greetings, {self.user_title}.",
            "Thank you": f"Thank you, {self.user_title}",
            "Yes": f"Yes, {self.user_title}",
            "No": f"No, {self.user_title}",
            "Sure": f"Of course, {self.user_title}",
            "Of course": f"Of course, {self.user_title}",
            "I can help": f"I can help you, {self.user_title}",
            "I'll do that": f"I'll do that for you, {self.user_title}",
            "Would you like": f"Would you like, {self.user_title}"
        }
        
        # Apply replacements
        for phrase, replacement in replacements.items():
            if text.startswith(phrase):
                return text.replace(phrase, replacement, 1)
        
        # If no specific replacement, add formal address randomly at beginning or end
        if len(text) > 0 and random.random() < 0.4:
            if text[-1] in ['.', '!', '?']:
                text = text[:-1] + f", {self.user_title}."
            else:
                text = text + f", {self.user_title}."
                
        return text
    
    def _determine_response_emotion(self, user_text, response):
        """Determine appropriate emotion for response based on context"""
        # Default to neutral
        emotion = VoiceEmotion.NEUTRAL
        
        # Check for questions
        if "?" in user_text:
            emotion = VoiceEmotion.NEUTRAL
        
        # Check for gratitude
        if any(word in user_text.lower() for word in ["thank", "thanks", "appreciate"]):
            emotion = VoiceEmotion.HAPPY
        
        # Check for urgency or problems
        if any(word in user_text.lower() for word in ["help", "urgent", "emergency", "problem"]):
            emotion = VoiceEmotion.CONCERNED
        
        # Check for excitement in response
        if any(char in response for char in ["!", "Wow", "Great"]):
            emotion = VoiceEmotion.EXCITED
        
        # Mirror user's mood if appropriate
        if self.user_mood == "happy":
            emotion = VoiceEmotion.HAPPY
        elif self.user_mood == "sad":
            emotion = VoiceEmotion.CONCERNED
        
        return emotion
    
    def speak(self, text, language=None, emotion=None):
        """Speak text response"""
        if not text:
            return
            
        logger.info(f"Speaking: {text}")
        self.speaking = True
        self.last_interaction = time.time()
        self._trigger_callbacks(self.on_speak_callbacks)
        
        # Determine language for speech
        detected_language = self._detect_language(text)
        if language is None and detected_language:
            language = detected_language
        
        # Use voice engine to speak with specified emotion and language
        self.voice_engine.speak(text, language=language, emotion=emotion)
        
        self.speaking = False
        self._trigger_callbacks(self.on_idle_callbacks)
    
    def _detect_language(self, text):
        """Simple language detection for common languages"""
        # Basic detection of Hindi by checking for Devanagari Unicode range
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            return VoiceLanguage.HINDI
        
        # Default to English
        return VoiceLanguage.ENGLISH
    
    def _execute_actions(self, actions):
        """Execute actions from intent parser"""
        for action in actions:
            if action["type"] == "calendar":
                # Handle calendar actions
                pass
            elif action["type"] == "task":
                # Handle task actions
                pass
            elif action["type"] == "music":
                # Handle music actions
                pass
            elif action["type"] == "health":
                # Handle health actions
                pass
            elif action["type"] == "system":
                # Handle system actions
                pass
    
    def add_callback(self, event_type, callback):
        """Add callback for specific event"""
        if event_type == "wake":
            self.on_wake_callbacks.append(callback)
        elif event_type == "listen":
            self.on_listen_callbacks.append(callback)
        elif event_type == "process":
            self.on_process_callbacks.append(callback)
        elif event_type == "speak":
            self.on_speak_callbacks.append(callback)
        elif event_type == "idle":
            self.on_idle_callbacks.append(callback)
        elif event_type == "face_detected":
            self.on_face_detected_callbacks.append(callback)
    
    def _trigger_callbacks(self, callbacks):
        """Trigger a list of callbacks"""
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in callback: {str(e)}")
    
    def shutdown(self):
        """Shutdown the assistant gracefully"""
        logger.info("Shutting down assistant...")
        self.running = False
        self.voice_engine.shutdown()
        self.memory.shutdown()
        
        # Say goodbye
        farewell = f"Goodbye, {self.user_title}! I'll be here when you need me."
        self.speak(farewell)

    def on_wake_word_detected(self):
        """Handle wake word detection"""
        logger.info("Wake word detected!")
        self._trigger_callbacks(self.on_wake_callbacks)
        self.listen() 