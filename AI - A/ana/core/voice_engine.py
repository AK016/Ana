#!/usr/bin/env python3
# Ana AI Assistant - Voice Engine Module

import os
import sys
import time
import json
import wave
import logging
import threading
import tempfile
import requests
import queue
from enum import Enum
from datetime import datetime
import pyaudio
import numpy as np
from typing import Optional, Dict, List, Union, Callable

# Optional imports for specific voice features
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False

try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

logger = logging.getLogger('Ana.VoiceEngine')

class VoiceLanguage(Enum):
    """Supported voice languages"""
    ENGLISH = "en"
    HINDI = "hi"
    AUTO = "auto"  # Auto-detect language

class VoiceEmotion(Enum):
    """Voice emotion types for ElevenLabs"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CONCERNED = "concerned"
    SERIOUS = "serious"

class VoiceEngine:
    """
    Voice engine for Ana AI Assistant with text-to-speech and speech recognition
    
    Features:
    - Text-to-speech with multiple engine options (pyttsx3, ElevenLabs)
    - Speech recognition with wake word detection
    - Multi-language support (English, Hindi)
    - Voice customization (pitch, rate, gender)
    """
    
    def __init__(self, settings: Dict[str, Any], security_manager=None):
        """Initialize voice engine with settings"""
        self.settings = settings
        self.security_manager = security_manager
        
        # Voice settings
        voice_settings = settings.get("voice", {})
        self.tts_engine = voice_settings.get("tts_engine", "pyttsx3")  # pyttsx3 or elevenlabs
        self.voice_id = voice_settings.get("voice_id", "en-US-female-1")
        self.language = voice_settings.get("language", "en-US")
        self.pitch = voice_settings.get("pitch", 1.0)
        self.rate = voice_settings.get("rate", 1.0)
        self.volume = voice_settings.get("volume", 1.0)
        
        # Speech recognition settings
        self.wake_word = voice_settings.get("wake_word", "ana").lower()
        self.wake_word_sensitivity = voice_settings.get("wake_word_sensitivity", 0.6)
        self.continuous_listen = voice_settings.get("continuous_listen", False)
        self.auto_adjust_ambient = voice_settings.get("auto_adjust_ambient", True)
        
        # Initialize engines
        self._init_tts_engine()
        self._init_speech_recognition()
        
        # State variables
        self.running = False
        self.is_speaking = False
        self.is_listening = False
        
        # Queues and threads
        self.speak_queue = queue.Queue()
        self.speak_thread = None
        self.listen_thread = None
        
        # Directory for audio files
        self.audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "recordings")
        os.makedirs(self.audio_dir, exist_ok=True)
        
        logger.info("Voice engine initialized")
    
    def _init_tts_engine(self):
        """Initialize the text-to-speech engine"""
        if self.tts_engine == "elevenlabs" and ELEVENLABS_AVAILABLE:
            # Initialize ElevenLabs
            api_key = self.settings.get("voice", {}).get("elevenlabs_api_key", "")
            
            # Get API key from secure storage if available
            if self.security_manager:
                credentials = self.security_manager.get_api_credentials("elevenlabs")
                if credentials and "api_key" in credentials:
                    api_key = credentials["api_key"]
                elif api_key:
                    # Store API key securely
                    self.security_manager.store_api_credentials("elevenlabs", {"api_key": api_key})
            
            if api_key:
                set_api_key(api_key)
                logger.info("ElevenLabs TTS engine initialized")
            else:
                logger.warning("ElevenLabs API key not found, falling back to pyttsx3")
                self.tts_engine = "pyttsx3"
        
        if self.tts_engine == "pyttsx3":
            # Initialize pyttsx3
            self.pyttsx_engine = pyttsx3.init()
            
            # Set properties
            self.pyttsx_engine.setProperty('rate', int(self.rate * 200))  # Default rate is around 200
            self.pyttsx_engine.setProperty('volume', self.volume)
            
            # Try to find a suitable voice
            voices = self.pyttsx_engine.getProperty('voices')
            selected_voice = None
            
            # Check if we should use a female voice
            female_voice = "female" in self.voice_id.lower()
            
            for voice in voices:
                # Try to match language first
                if self.language[:2].lower() in voice.id.lower():
                    # If we have a preference for female/male voice
                    if female_voice and "female" in voice.id.lower():
                        selected_voice = voice.id
                        break
                    elif not female_voice and "male" in voice.id.lower():
                        selected_voice = voice.id
                        break
                    # If we haven't found a voice yet, use this one
                    if not selected_voice:
                        selected_voice = voice.id
            
            # If we still don't have a voice, use the first one
            if not selected_voice and voices:
                selected_voice = voices[0].id
            
            if selected_voice:
                self.pyttsx_engine.setProperty('voice', selected_voice)
                logger.info(f"Pyttsx3 TTS engine initialized with voice: {selected_voice}")
            else:
                logger.warning("No suitable voice found for pyttsx3")
    
    def _init_speech_recognition(self):
        """Initialize speech recognition"""
        self.recognizer = sr.Recognizer()
        
        # Adjust for ambient noise when starting
        if self.auto_adjust_ambient:
            try:
                with sr.Microphone() as source:
                    logger.info("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=2)
                    logger.info("Ambient noise adjustment complete")
            except Exception as e:
                logger.error(f"Error adjusting for ambient noise: {str(e)}")
    
    def start(self):
        """Start the voice engine"""
        if self.running:
            return True
            
        logger.info("Starting voice engine")
        self.running = True
        
        # Start speak thread
        self.speak_thread = threading.Thread(target=self._speak_worker, daemon=True)
        self.speak_thread.start()
        
        # Start listen thread if continuous listening is enabled
        if self.continuous_listen:
            self.listen_thread = threading.Thread(target=self._continuous_listen_worker, daemon=True)
            self.listen_thread.start()
        
        return True
    
    def stop(self):
        """Stop the voice engine"""
        if not self.running:
            return True
            
        logger.info("Stopping voice engine")
        self.running = False
        
        # Clear speak queue
        while not self.speak_queue.empty():
            try:
                self.speak_queue.get_nowait()
            except queue.Empty:
                break
        
        # Wait for threads to finish
        if self.speak_thread and self.speak_thread.is_alive():
            self.speak_thread.join(timeout=2.0)
            
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)
        
        return True
    
    def speak(self, text: str, priority: bool = False) -> bool:
        """
        Add text to speak queue
        
        Args:
            text: Text to speak
            priority: If True, add to front of queue
            
        Returns:
            bool: True if text was added to queue
        """
        if not text or not self.running:
            return False
            
        try:
            if priority:
                # Use a priority tuple (0 for high priority)
                self.speak_queue.put((0, text))
            else:
                # Normal priority (1)
                self.speak_queue.put((1, text))
                
            logger.debug(f"Added to speak queue: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error adding text to speak queue: {str(e)}")
            return False
    
    def _speak_worker(self):
        """Worker thread for processing speak queue"""
        while self.running:
            try:
                # Get item from queue with timeout
                try:
                    priority, text = self.speak_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # Set speaking flag
                self.is_speaking = True
                
                # Speak the text
                self._tts_speak(text)
                
                # Mark item as done
                self.speak_queue.task_done()
                
                # Clear speaking flag
                self.is_speaking = False
                
            except Exception as e:
                logger.error(f"Error in speak worker: {str(e)}")
                self.is_speaking = False
                time.sleep(0.1)
    
    def _tts_speak(self, text: str):
        """Speak text using the configured TTS engine"""
        if not text:
            return
            
        try:
            if self.tts_engine == "elevenlabs" and ELEVENLABS_AVAILABLE:
                # Get API key securely if security manager is available
                api_key = None
                if self.security_manager:
                    credentials = self.security_manager.get_api_credentials("elevenlabs")
                    if credentials and "api_key" in credentials:
                        api_key = credentials["api_key"]
                
                if api_key:
                    set_api_key(api_key)
                    
                    # Apply privacy measures
                    privacy_options = {}
                    if self.security_manager:
                        privacy_options = self.security_manager.secure_api_request(
                            "elevenlabs", 
                            {"disable_voice_cloning": True, "disable_sample_sharing": True},
                            include_credentials=False
                        )
                    
                    # Generate audio
                    audio = generate(
                        text=text,
                        voice=self.voice_id,
                        model="eleven_monolingual_v1"
                    )
                    
                    # Play audio
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                        temp_path = temp_file.name
                        temp_file.write(audio)
                    
                    # Play using pydub for better control
                    audio_segment = AudioSegment.from_file(temp_path, format="mp3")
                    play(audio_segment)
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                else:
                    # Fall back to pyttsx3
                    self.pyttsx_engine.say(text)
                    self.pyttsx_engine.runAndWait()
            else:
                # Use pyttsx3
                self.pyttsx_engine.say(text)
                self.pyttsx_engine.runAndWait()
                
        except Exception as e:
            logger.error(f"Error in TTS: {str(e)}")
            
            # Try fallback if primary method failed
            try:
                if self.tts_engine != "pyttsx3":
                    logger.info("Falling back to pyttsx3")
                    self.pyttsx_engine.say(text)
                    self.pyttsx_engine.runAndWait()
            except Exception as fallback_error:
                logger.error(f"Error in fallback TTS: {str(fallback_error)}")
    
    def listen(self, timeout: Optional[int] = None, continuous: bool = False) -> Optional[str]:
        """
        Listen for speech and convert to text
        
        Args:
            timeout: Maximum time to listen in seconds (None for default)
            continuous: Whether to listen continuously for wake word
            
        Returns:
            str: Recognized text, or None if nothing was recognized
        """
        # Set listening flag
        self.is_listening = True
        
        try:
            with sr.Microphone() as source:
                # Set timeout
                if timeout is None:
                    timeout = 5  # Default timeout
                
                # Adjust for ambient noise
                if self.auto_adjust_ambient:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                logger.info(f"Listening for {timeout} seconds...")
                
                # Listen for audio
                try:
                    audio = self.recognizer.listen(source, timeout=timeout)
                except sr.WaitTimeoutError:
                    logger.info("Listen timeout")
                    self.is_listening = False
                    return None
                
                # Save audio if security manager is available (for debugging/training)
                if self.security_manager:
                    timestamp = int(time.time())
                    audio_path = self.security_manager.secure_file_path(
                        "voice_recordings", f"recording_{timestamp}.wav")
                    
                    with open(audio_path, "wb") as f:
                        f.write(audio.get_wav_data())
                    
                    # Set secure permissions
                    os.chmod(audio_path, 0o600)  # Owner read/write only
                
                # Recognize speech
                if self.language.startswith("en"):
                    # Use Google's speech recognition
                    try:
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        logger.info(f"Recognized: {text}")
                        
                        # If continuous mode, check for wake word
                        if continuous and self.wake_word:
                            text_lower = text.lower()
                            if self.wake_word.lower() in text_lower:
                                # Remove wake word from text
                                command = text_lower.replace(self.wake_word.lower(), "").strip()
                                self.is_listening = False
                                return command
                            else:
                                self.is_listening = False
                                return None
                        
                        self.is_listening = False
                        return text
                    except sr.UnknownValueError:
                        logger.info("Google Speech Recognition could not understand audio")
                    except sr.RequestError as e:
                        logger.error(f"Could not request results from Google Speech Recognition service: {e}")
                else:
                    # Use Whisper or other models for non-English recognition
                    # This is a placeholder - implement as needed
                    pass
                    
        except Exception as e:
            logger.error(f"Error in listen: {str(e)}")
        
        # Clear listening flag
        self.is_listening = False
        return None
    
    def _continuous_listen_worker(self):
        """Worker thread for continuous listening"""
        while self.running:
            # Only listen if not speaking
            if not self.is_speaking:
                result = self.listen(timeout=5, continuous=True)
                
                # If we got a command (after wake word)
                if result:
                    # We could emit a signal here to process the command
                    # For now, just log it
                    logger.info(f"Wake word detected, command: {result}")
            
            # Sleep to prevent CPU hogging
            time.sleep(0.1)
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice to use for TTS
        
        Args:
            voice_id: ID of the voice to use
            
        Returns:
            bool: True if voice was set successfully
        """
        self.voice_id = voice_id
        
        if self.tts_engine == "pyttsx3":
            # Set voice in pyttsx3
            try:
                self.pyttsx_engine.setProperty('voice', voice_id)
                logger.info(f"Voice set to: {voice_id}")
                return True
            except Exception as e:
                logger.error(f"Error setting voice: {str(e)}")
                return False
        else:
            # For ElevenLabs, just store the ID for next use
            logger.info(f"Voice set to: {voice_id}")
            return True
    
    def set_language(self, language: str) -> bool:
        """
        Set the language for speech recognition and TTS
        
        Args:
            language: Language code (e.g., 'en-US', 'hi-IN')
            
        Returns:
            bool: True if language was set successfully
        """
        self.language = language
        logger.info(f"Language set to: {language}")
        
        # For pyttsx3, try to find a voice for this language
        if self.tts_engine == "pyttsx3":
            voices = self.pyttsx_engine.getProperty('voices')
            for voice in voices:
                if language[:2].lower() in voice.id.lower():
                    self.pyttsx_engine.setProperty('voice', voice.id)
                    logger.info(f"Found voice for language {language}: {voice.id}")
                    break
        
        return True
    
    def set_speech_rate(self, rate: float) -> bool:
        """
        Set the speech rate
        
        Args:
            rate: Rate multiplier (1.0 is normal speed)
            
        Returns:
            bool: True if rate was set successfully
        """
        self.rate = rate
        
        if self.tts_engine == "pyttsx3":
            try:
                self.pyttsx_engine.setProperty('rate', int(rate * 200))
                logger.info(f"Speech rate set to: {rate}")
                return True
            except Exception as e:
                logger.error(f"Error setting speech rate: {str(e)}")
                return False
        else:
            # For ElevenLabs, just store the rate for next use
            logger.info(f"Speech rate set to: {rate}")
            return True
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available voices
        
        Returns:
            List of dicts with voice info
        """
        voice_list = []
        
        if self.tts_engine == "pyttsx3":
            # Get voices from pyttsx3
            try:
                pyttsx_voices = self.pyttsx_engine.getProperty('voices')
                for voice in pyttsx_voices:
                    voice_list.append({
                        "id": voice.id,
                        "name": voice.name,
                        "languages": voice.languages,
                        "gender": "female" if "female" in voice.id.lower() else "male",
                        "engine": "pyttsx3"
                    })
            except Exception as e:
                logger.error(f"Error getting voices from pyttsx3: {str(e)}")
        
        elif self.tts_engine == "elevenlabs" and ELEVENLABS_AVAILABLE:
            # Get voices from ElevenLabs
            try:
                # Get API key securely if security manager is available
                api_key = None
                if self.security_manager:
                    credentials = self.security_manager.get_api_credentials("elevenlabs")
                    if credentials and "api_key" in credentials:
                        api_key = credentials["api_key"]
                
                if api_key:
                    set_api_key(api_key)
                    elevenlabs_voices = voices()
                    for voice in elevenlabs_voices:
                        voice_list.append({
                            "id": voice.voice_id,
                            "name": voice.name,
                            "languages": [voice.category],
                            "gender": "unknown",  # ElevenLabs doesn't provide gender info
                            "engine": "elevenlabs"
                        })
            except Exception as e:
                logger.error(f"Error getting voices from ElevenLabs: {str(e)}")
        
        return voice_list
    
    def set_wake_word(self, wake_word: str) -> bool:
        """
        Set the wake word for continuous listening
        
        Args:
            wake_word: Word or phrase to trigger the assistant
            
        Returns:
            bool: True if wake word was set successfully
        """
        self.wake_word = wake_word.lower()
        logger.info(f"Wake word set to: {wake_word}")
        return True

# For testing directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create voice engine
    engine = VoiceEngine({"voice": {"tts_engine": "pyttsx3"}})
    
    # Start engine
    engine.start()
    
    # Test speak
    engine.speak("Hello, I am Ana, your AI assistant. How can I help you today?")
    
    # Test listen
    print("Say something...")
    text = engine.listen(timeout=5)
    if text:
        print(f"You said: {text}")
        engine.speak(f"You said: {text}")
    
    # Stop engine
    engine.stop()
    
    print("Test complete") 