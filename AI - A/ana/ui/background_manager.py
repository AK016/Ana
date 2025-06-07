#!/usr/bin/env python3
# Ana AI Assistant - Background Manager

import os
import json
import time
import random
import logging
import requests
import traceback
from enum import Enum
from datetime import datetime
from threading import Thread, Event

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

from ana.ui.full_screen_character import BackgroundType

logger = logging.getLogger('Ana.BackgroundManager')

class ConversationMood(Enum):
    """Detected mood from conversation"""
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    URGENT = "urgent"
    RELAXED = "relaxed"

class BackgroundManager(QObject):
    """
    Manages background transitions based on conversation context and weather
    
    This class is responsible for:
    1. Monitoring conversation and detecting mood/context
    2. Fetching weather data at the user's location
    3. Determining appropriate background type
    4. Signaling when backgrounds should change
    """
    
    # Signal emitted when background should change
    background_changed = pyqtSignal(BackgroundType, dict)
    
    def __init__(self, settings=None):
        super().__init__()
        self.settings = settings or {}
        
        # Current state
        self.current_background = BackgroundType.GRADIENT
        self.current_bg_params = {}
        self.conversation_mood = ConversationMood.NEUTRAL
        self.weather_data = None
        self.last_weather_check = 0
        self.weather_check_interval = 30 * 60  # 30 minutes
        
        # Initialize background update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.check_for_updates)
        self.update_timer.start(5000)  # Check every 5 seconds
        
        # Thread for background weather fetching
        self.stop_event = Event()
        self.background_thread = Thread(target=self._background_worker, daemon=True)
        self.background_thread.start()
        
        logger.info("Background manager initialized")
    
    def _background_worker(self):
        """Background thread to periodically fetch weather"""
        while not self.stop_event.is_set():
            try:
                self._update_weather()
            except Exception as e:
                logger.error(f"Error in background worker: {str(e)}")
                logger.error(traceback.format_exc())
            
            # Sleep for a while
            for _ in range(300):  # 5 minute intervals (300 seconds)
                if self.stop_event.is_set():
                    break
                time.sleep(1)
    
    def check_for_updates(self):
        """Check if background should be updated"""
        # Determine time of day
        hour = datetime.now().hour
        
        if 6 <= hour < 10:
            time_of_day = "morning"
        elif 10 <= hour < 17:
            time_of_day = "day"
        elif 17 <= hour < 20:
            time_of_day = "sunset"
        else:
            time_of_day = "night"
        
        # Get background based on current factors
        new_bg, new_params = self._determine_background(time_of_day)
        
        # Only update if something changed
        if (new_bg != self.current_background or 
            new_params != self.current_bg_params):
            
            self.current_background = new_bg
            self.current_bg_params = new_params
            self.background_changed.emit(new_bg, new_params)
            logger.info(f"Background changed to {new_bg.value} with params: {new_params}")
    
    def _determine_background(self, time_of_day):
        """Determine appropriate background based on various factors"""
        # Start with default parameters
        params = {
            'time_of_day': time_of_day
        }
        
        # Default background based on time of day
        if time_of_day == "night":
            default_bg = BackgroundType.CYBERPUNK_CITY
        else:
            default_bg = BackgroundType.WEATHER
        
        # If we have weather data, use it
        if self.weather_data:
            weather_condition = self.weather_data.get('condition', 'clear').lower()
            params['weather'] = weather_condition
            
            # For stormy weather, use cyberpunk
            if weather_condition in ['thunderstorm', 'tornado', 'hurricane']:
                default_bg = BackgroundType.CYBERPUNK_CITY
                
            # For heavy rain, snow, use weather
            elif weather_condition in ['rain', 'snow', 'sleet', 'hail']:
                default_bg = BackgroundType.WEATHER
        
        # Adjust based on conversation mood
        if self.conversation_mood == ConversationMood.TECHNICAL:
            bg_type = BackgroundType.MATRIX
        elif self.conversation_mood == ConversationMood.CREATIVE:
            # For creative conversations, use colorful backgrounds
            bg_type = BackgroundType.GRADIENT
            params['gradient_colors'] = ['#FF3366', '#FF9933', '#FFCC33']
        elif self.conversation_mood == ConversationMood.URGENT:
            # For urgent conversations, use attention-grabbing backgrounds
            bg_type = BackgroundType.CYBERPUNK_CITY
        else:
            # Use the default background for other moods
            bg_type = default_bg
        
        return bg_type, params
    
    def _update_weather(self):
        """Fetch weather data if needed"""
        # Skip if recently checked
        current_time = time.time()
        if current_time - self.last_weather_check < self.weather_check_interval:
            return
        
        logger.info("Fetching weather data")
        self.last_weather_check = current_time
        
        try:
            location = self.settings.get("assistant", {}).get("weather_location", "New York")
            api_key = self.settings.get("weather", {}).get("api_key", "")
            
            # Use a free weather API if available, or mock data for development
            if api_key:
                # Example OpenWeatherMap API call
                url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    weather = data.get('weather', [{}])[0]
                    
                    self.weather_data = {
                        'condition': weather.get('main', 'Clear'),
                        'description': weather.get('description', ''),
                        'temperature': data.get('main', {}).get('temp', 20),
                        'humidity': data.get('main', {}).get('humidity', 50),
                        'wind_speed': data.get('wind', {}).get('speed', 0),
                        'location': location
                    }
            else:
                # Mock weather data for development
                conditions = ['clear', 'clouds', 'rain', 'thunderstorm', 'snow', 'mist']
                condition = random.choice(conditions)
                
                self.weather_data = {
                    'condition': condition,
                    'description': f'{condition} weather',
                    'temperature': random.uniform(10, 30),
                    'humidity': random.uniform(30, 90),
                    'wind_speed': random.uniform(0, 10),
                    'location': location
                }
            
            logger.info(f"Weather updated: {self.weather_data['condition']} in {location}")
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            logger.error(traceback.format_exc())
    
    def update_conversation_mood(self, mood, keywords=None):
        """Update the detected conversation mood"""
        try:
            if isinstance(mood, str):
                mood = ConversationMood(mood)
            
            self.conversation_mood = mood
            logger.info(f"Conversation mood updated to: {mood.value}")
            
            # Immediately check for background updates
            self.check_for_updates()
            
        except (ValueError, AttributeError) as e:
            logger.error(f"Invalid mood value: {str(e)}")
    
    def analyze_message(self, message):
        """Analyze a message to detect mood"""
        # Skip empty messages
        if not message or not message.strip():
            return
            
        # Simple keyword-based mood detection
        message = message.lower()
        
        # Define mood keywords
        mood_keywords = {
            ConversationMood.POSITIVE: [
                'happy', 'good', 'great', 'excellent', 'awesome', 'love', 'like', 'enjoy', 'thank'
            ],
            ConversationMood.NEGATIVE: [
                'sad', 'bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'upset', 'sorry'
            ],
            ConversationMood.TECHNICAL: [
                'code', 'program', 'function', 'algorithm', 'system', 'technical', 'debug', 'error',
                'python', 'java', 'javascript', 'html', 'css', 'api', 'database', 'sql'
            ],
            ConversationMood.CREATIVE: [
                'create', 'design', 'art', 'music', 'color', 'beautiful', 'creative', 'imagine',
                'story', 'poem', 'draw', 'paint', 'picture', 'image'
            ],
            ConversationMood.URGENT: [
                'urgent', 'emergency', 'quick', 'fast', 'now', 'asap', 'hurry', 'immediately'
            ],
            ConversationMood.RELAXED: [
                'relax', 'calm', 'slow', 'peace', 'quiet', 'gentle', 'easy', 'leisure'
            ]
        }
        
        # Count keyword matches for each mood
        mood_scores = {mood: 0 for mood in ConversationMood}
        
        for mood, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    mood_scores[mood] += 1
        
        # Find the mood with the highest score
        max_score = 0
        detected_mood = ConversationMood.NEUTRAL
        
        for mood, score in mood_scores.items():
            if score > max_score:
                max_score = score
                detected_mood = mood
        
        # Only update if we found a significant mood
        if max_score > 0:
            self.update_conversation_mood(detected_mood)
            
        return detected_mood
    
    def stop(self):
        """Stop the background manager"""
        self.stop_event.set()
        if self.background_thread.is_alive():
            self.background_thread.join(timeout=1.0)
        self.update_timer.stop() 