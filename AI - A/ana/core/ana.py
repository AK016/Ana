#!/usr/bin/env python3
# Ana AI Assistant - Main Application Module

import os
import sys
import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Core modules
from .voice_engine import VoiceEngine
from .facial_recognition import FacialRecognition
from .self_dev import SelfDev
from .health_integration import HealthIntegration
from .ai_core import AICore
from .youtube_music import YouTubeMusic
from .ui_controller import UIController
from .security import SecurityManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "logs", "ana.log"))
    ]
)
logger = logging.getLogger('Ana')

class Ana:
    """Main Ana AI Assistant class - integrates all components"""
    
    def __init__(self):
        """Initialize Ana AI Assistant"""
        logger.info("Initializing Ana AI Assistant")
        
        # Create necessary directories
        self._create_directories()
        
        # Load settings
        self.settings = self._load_settings()
        
        # Initialize security manager first (required by other components)
        self.security_manager = SecurityManager(self.settings)
        
        # Initialize components
        self.ai_core = AICore(self.settings, self.security_manager)
        self.voice_engine = VoiceEngine(self.settings, self.security_manager)
        self.facial_recognition = FacialRecognition(self.settings, self.security_manager)
        self.self_dev = SelfDev(self.settings, self.security_manager)
        self.youtube_music = YouTubeMusic(self.settings, self.security_manager)
        self.health_integration = HealthIntegration(self.settings, self.security_manager)
        
        # UI controller needs to be initialized last
        self.ui_controller = UIController(self, self.settings)
        
        # State variables
        self.running = False
        self.is_listening = False
        self.current_task = None
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        
        logger.info("Ana AI Assistant initialized")
    
    def _create_directories(self):
        """Create necessary directories for Ana"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        directories = [
            os.path.join(base_dir, "logs"),
            os.path.join(base_dir, "data"),
            os.path.join(base_dir, "data", "recordings"),
            os.path.join(base_dir, "data", "health_cache"),
            os.path.join(base_dir, "data", "facial_data"),
            os.path.join(base_dir, "data", "security"),
            os.path.join(base_dir, "config"),
            os.path.join(base_dir, "temp")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        logger.info(f"Created necessary directories")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from configuration files"""
        settings = {}
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(base_dir, "config")
        
        # Load main settings
        main_settings_path = os.path.join(config_dir, "settings.json")
        if os.path.exists(main_settings_path):
            with open(main_settings_path, 'r') as f:
                settings.update(json.load(f))
        
        # Load health settings
        health_settings_path = os.path.join(config_dir, "health_settings.json")
        if os.path.exists(health_settings_path):
            with open(health_settings_path, 'r') as f:
                settings.update(json.load(f))
        
        # Load voice settings
        voice_settings_path = os.path.join(config_dir, "voice_settings.json")
        if os.path.exists(voice_settings_path):
            with open(voice_settings_path, 'r') as f:
                settings.update(json.load(f))
        
        # Load security settings
        security_settings_path = os.path.join(config_dir, "security_settings.json")
        if os.path.exists(security_settings_path):
            with open(security_settings_path, 'r') as f:
                settings.update(json.load(f))
        
        logger.info(f"Loaded settings from configuration files")
        return settings
    
    def start(self):
        """Start Ana AI Assistant"""
        logger.info("Starting Ana AI Assistant")
        
        # Start all components
        self.running = True
        
        # Start AI core
        self.ai_core.start()
        
        # Start voice engine
        self.voice_engine.start()
        
        # Start facial recognition
        self.facial_recognition.start()
        
        # Start self-development module
        self.self_dev.start()
        
        # Start YouTube Music module
        self.youtube_music.start()
        
        # Start health integration module
        self.health_integration.start()
        
        # Start UI controller (should be last)
        self.ui_controller.start()
        
        logger.info("Ana AI Assistant started successfully")
        
        # Signal that Ana is ready
        self.speak("Ana is ready and at your service.")
    
    def stop(self):
        """Stop Ana AI Assistant"""
        logger.info("Stopping Ana AI Assistant")
        self.running = False
        
        # Stop components in reverse order
        self.ui_controller.stop()
        self.health_integration.shutdown()
        self.youtube_music.stop()
        self.self_dev.stop()
        self.facial_recognition.stop()
        self.voice_engine.stop()
        self.ai_core.stop()
        
        logger.info("Ana AI Assistant stopped")
    
    def speak(self, text: str, priority: bool = False):
        """Speak text using voice engine"""
        return self.voice_engine.speak(text, priority)
    
    def listen(self, timeout: Optional[int] = None, continuous: bool = False):
        """Listen for user input using voice engine"""
        self.is_listening = True
        result = self.voice_engine.listen(timeout, continuous)
        self.is_listening = False
        return result
    
    def process_command(self, command: str) -> str:
        """Process a voice command"""
        logger.info(f"Processing command: {command}")
        
        # Record metadata for the conversation
        metadata = {
            "timestamp": time.time(),
            "session_id": self.session_id,
            "source": "voice" if self.is_listening else "text",
            "command_type": self._detect_command_type(command)
        }
        
        # Get response from AI core
        response = self.ai_core.process_input(command)
        
        # Store conversation securely
        self.security_manager.store_conversation(
            user_message=command,
            assistant_message=response,
            session_id=self.session_id,
            metadata=metadata
        )
        
        # Look for specific command patterns
        if "play music" in command.lower():
            # Extract song name
            song = command.lower().replace("play music", "").strip()
            if song:
                self.youtube_music.play_song(song)
                return f"Playing {song}"
            else:
                self.youtube_music.play()
                return "Playing music"
        
        elif "stop music" in command.lower():
            self.youtube_music.stop_playback()
            return "Music stopped"
        
        elif "volume" in command.lower():
            # Extract volume level
            if "up" in command.lower():
                self.youtube_music.volume_up()
                return "Volume increased"
            elif "down" in command.lower():
                self.youtube_music.volume_down()
                return "Volume decreased"
            else:
                # Try to extract a number
                import re
                volume_match = re.search(r'(\d+)', command)
                if volume_match:
                    volume = int(volume_match.group(1))
                    self.youtube_music.set_volume(volume)
                    return f"Volume set to {volume}%"
        
        # Health data commands
        elif "health" in command.lower() or "fitness" in command.lower():
            if "summary" in command.lower() or "overview" in command.lower():
                summary = self.health_integration.get_health_summary()
                interpretation = self.health_integration.interpret_health_data(summary)
                return interpretation
            
            elif "steps" in command.lower():
                steps_data = self.health_integration.get_step_data()
                return f"Today you've taken {steps_data['steps']} steps, covering {steps_data['distance']:.2f} kilometers and burning {steps_data['calories']:.0f} calories."
            
            elif "sleep" in command.lower():
                sleep_data = self.health_integration.get_sleep_data()
                return f"Last night you slept for {sleep_data['duration_formatted']} with a sleep quality score of {sleep_data['quality']:.1f}. Your deep sleep was {sleep_data['deep_sleep_minutes']} minutes."
            
            elif "stress" in command.lower():
                stress_data = self.health_integration.get_stress_data()
                return f"Your current stress level is {stress_data['stress_category']} with an average score of {stress_data['average_level']}."
            
            elif "heart" in command.lower() or "pulse" in command.lower():
                heart_data = self.health_integration.get_heart_rate_data("day")
                return f"Your average heart rate today is {heart_data['average_bpm']} BPM, with a range from {heart_data['min_bpm']} to {heart_data['max_bpm']} BPM."
        
        # Privacy and security commands
        elif "privacy" in command.lower() or "security" in command.lower():
            if "report" in command.lower() or "status" in command.lower():
                report = self.security_manager.generate_privacy_report()
                return self._format_privacy_report(report)
            
            elif "wipe" in command.lower() or "delete" in command.lower() or "clear" in command.lower():
                return "To protect your data, I require explicit confirmation. Please say 'confirm data wipe' if you want to delete all stored data."
            
            elif "confirm data wipe" in command.lower():
                success = self.security_manager.wipe_all_data(confirm=True)
                if success:
                    return "All your data has been securely wiped from my storage."
                else:
                    return "There was an error wiping the data. Please try again or check the logs."
            
            elif "explain" in command.lower() or "how" in command.lower() or "works" in command.lower():
                return ("Your data is secured with encryption and stored only on your device. " 
                       "I use AES-256 encryption with a locally stored key that never leaves your device. "
                       "API calls are anonymized, and no personal data is shared with external services.")
        
        return response
    
    def _detect_command_type(self, command: str) -> str:
        """Detect the type of command for metadata"""
        command_lower = command.lower()
        
        if "play" in command_lower or "music" in command_lower or "song" in command_lower:
            return "music"
        elif "health" in command_lower or "fitness" in command_lower or "steps" in command_lower:
            return "health"
        elif "privacy" in command_lower or "security" in command_lower or "data" in command_lower:
            return "privacy"
        elif "github" in command_lower or "code" in command_lower or "development" in command_lower:
            return "development"
        else:
            return "general"
    
    def _format_privacy_report(self, report: Dict[str, Any]) -> str:
        """Format privacy report for user-friendly display"""
        lines = [
            "PRIVACY AND SECURITY REPORT",
            f"Generated on: {report.get('report_time', 'Unknown')}",
            f"Encryption: {'Enabled' if report.get('encryption_enabled', False) else 'Disabled'}",
            "",
            "DATA STORED LOCALLY:",
        ]
        
        # Add data counts
        counts = report.get("data_counts", {})
        for data_type, count in counts.items():
            lines.append(f"- {data_type.replace('_', ' ').title()}: {count} entries")
        
        return "\n".join(lines)
    
    def update_ui(self, state: Dict[str, Any]):
        """Update UI with current state"""
        self.ui_controller.update_state(state)
    
    def run_task(self, task_name: str, **kwargs):
        """Run a specific task"""
        self.current_task = task_name
        
        # Update UI
        self.update_ui({"current_task": task_name})
        
        # Task implementations
        if task_name == "listen_continuous":
            self._task_listen_continuous()
        elif task_name == "self_development":
            self.self_dev.run_development_cycle()
        elif task_name == "analyze_face":
            self.facial_recognition.analyze_current_face()
        elif task_name == "privacy_audit":
            self._task_privacy_audit()
        # Add more tasks as needed
        
        self.current_task = None
        self.update_ui({"current_task": None})
    
    def _task_listen_continuous(self):
        """Task to listen continuously for commands"""
        self.speak("I'm listening for commands")
        
        while self.running and self.current_task == "listen_continuous":
            command = self.listen(timeout=5, continuous=True)
            
            if command:
                response = self.process_command(command)
                self.speak(response)
                
            time.sleep(0.1)
    
    def _task_privacy_audit(self):
        """Task to audit privacy and security settings"""
        # Generate a privacy report
        report = self.security_manager.generate_privacy_report()
        
        # Check for security issues
        security_issues = []
        
        # Check encryption status
        if not report.get("encryption_enabled", False):
            security_issues.append("Encryption is disabled")
        
        # Check for excessive data storage
        counts = report.get("data_counts", {})
        if counts.get("conversations", 0) > 1000:
            security_issues.append("Large number of stored conversations (>1000)")
        
        # Report findings
        if security_issues:
            self.speak(f"I found {len(security_issues)} security concerns. The first issue is {security_issues[0]}.")
        else:
            self.speak("Security audit complete. No issues found.")
        
        # Log detailed report
        logger.info(f"Privacy audit results: {json.dumps(report)}")
        
        # Store audit record
        self.security_manager.store_user_data(
            key="last_privacy_audit",
            value={
                "timestamp": time.time(),
                "issues_found": len(security_issues),
                "issues": security_issues
            }
        )
            
    def get_health_data(self, data_type: str = "summary", period: str = "day"):
        """Get health data from health integration module"""
        if data_type == "summary":
            return self.health_integration.get_health_summary()
        elif data_type == "steps":
            return self.health_integration.get_step_data()
        elif data_type == "sleep":
            return self.health_integration.get_sleep_data()
        elif data_type == "stress":
            return self.health_integration.get_stress_data()
        elif data_type == "heart_rate":
            return self.health_integration.get_heart_rate_data(period)
        else:
            return {"error": f"Unknown data type: {data_type}"}
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history (for context)"""
        # Use security manager to get encrypted conversations
        return self.security_manager.get_conversations(
            session_id=self.session_id,
            limit=limit
        )

# Main entry point
def main():
    """Main entry point for Ana AI Assistant"""
    ana = Ana()
    
    try:
        ana.start()
        
        # Keep the main thread running
        while ana.running:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}", exc_info=True)
    finally:
        ana.stop()

if __name__ == "__main__":
    main() 