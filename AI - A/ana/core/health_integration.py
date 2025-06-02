#!/usr/bin/env python3
# Ana AI Assistant - Samsung Health Integration Module

import os
import json
import time
import logging
import requests
import sqlite3
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger('Ana.HealthIntegration')

class HealthIntegration:
    """Samsung Health integration for Ana AI Assistant"""
    
    def __init__(self, settings):
        """Initialize health integration with settings"""
        self.settings = settings
        self.enabled = settings.get("health_integration", {}).get("enabled", False)
        
        # Health API settings
        health_settings = settings.get("health_integration", {})
        self.client_id = health_settings.get("client_id", "")
        self.client_secret = health_settings.get("client_secret", "")
        self.access_token = health_settings.get("access_token", "")
        self.refresh_token = health_settings.get("refresh_token", "")
        self.token_expiry = health_settings.get("token_expiry", 0)
        
        # Data cache settings
        self.cache_dir = os.path.join(os.path.dirname(__file__), "..", "data", "health_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_db_path = os.path.join(self.cache_dir, "health_data.db")
        
        # Cache refresh settings
        self.last_refresh = time.time() - 86400  # Force refresh on first run
        self.refresh_interval = 3600  # 1 hour default
        
        # Initialize cache database
        self._init_cache_db()
        
        # Thread for background data sync
        self.running = False
        self.sync_thread = None
        
        logger.info("Health integration initialized")
    
    def start(self):
        """Start health integration services"""
        if not self.enabled:
            logger.info("Health integration is disabled in settings")
            return False
            
        # Validate configuration
        if not self._validate_config():
            logger.error("Health integration configuration is incomplete")
            return False
        
        # Refresh access token if needed
        if time.time() > self.token_expiry:
            if not self._refresh_access_token():
                logger.error("Failed to refresh access token")
                return False
        
        # Start background sync thread
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        logger.info("Health integration started")
        
        return True
    
    def _validate_config(self) -> bool:
        """Validate API configuration"""
        if not self.client_id or not self.client_secret:
            logger.error("Missing client_id or client_secret")
            return False
            
        if not self.access_token and not self.refresh_token:
            logger.error("Missing both access_token and refresh_token")
            return False
            
        return True
    
    def _init_cache_db(self):
        """Initialize the SQLite cache database"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS steps (
                date TEXT PRIMARY KEY,
                count INTEGER,
                distance REAL,
                calories REAL,
                last_updated INTEGER
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sleep (
                date TEXT PRIMARY KEY,
                duration INTEGER,
                deep_sleep INTEGER,
                light_sleep INTEGER,
                rem_sleep INTEGER,
                awake_time INTEGER,
                quality REAL,
                last_updated INTEGER
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stress (
                date TEXT PRIMARY KEY,
                average_level INTEGER,
                max_level INTEGER,
                min_level INTEGER,
                duration INTEGER,
                last_updated INTEGER
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS heart_rate (
                timestamp INTEGER PRIMARY KEY,
                bpm INTEGER,
                last_updated INTEGER
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Health cache database initialized")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing cache database: {str(e)}")
    
    def _refresh_access_token(self) -> bool:
        """Refresh the Samsung Health API access token"""
        if not self.refresh_token:
            logger.error("No refresh token available")
            return False
            
        try:
            # This is a simplified example - in a real implementation,
            # you would make an actual API call to Samsung Health's token endpoint
            url = "https://api.health.samsung.com/oauth/token"
            data = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.token_expiry = time.time() + token_data.get("expires_in", 3600)
                
                # Also update refresh token if provided
                if "refresh_token" in token_data:
                    self.refresh_token = token_data["refresh_token"]
                
                # Update settings file
                self._update_tokens_in_settings()
                
                logger.info("Access token refreshed successfully")
                return True
            else:
                logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            return False
    
    def _update_tokens_in_settings(self):
        """Update tokens in the settings file"""
        try:
            settings_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.json")
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                
                # Update token information
                if "health_integration" not in settings:
                    settings["health_integration"] = {}
                    
                settings["health_integration"]["access_token"] = self.access_token
                settings["health_integration"]["refresh_token"] = self.refresh_token
                settings["health_integration"]["token_expiry"] = self.token_expiry
                
                # Write back to file
                with open(settings_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                    
                logger.info("Updated tokens in settings file")
                
        except Exception as e:
            logger.error(f"Error updating tokens in settings: {str(e)}")
    
    def _sync_loop(self):
        """Background loop for syncing health data"""
        while self.running:
            try:
                # Check if it's time to refresh data
                if time.time() - self.last_refresh > self.refresh_interval:
                    self._sync_health_data()
                    self.last_refresh = time.time()
                
                # Sleep to avoid high CPU usage
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in health data sync loop: {str(e)}")
                time.sleep(300)  # Sleep longer after an error
    
    def _sync_health_data(self):
        """Sync health data from Samsung Health API"""
        logger.info("Syncing health data from Samsung Health")
        
        # Ensure token is valid
        if time.time() > self.token_expiry:
            if not self._refresh_access_token():
                logger.error("Failed to refresh token, skipping sync")
                return
        
        # Get data for the last week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Sync each data type
        self._sync_step_data(start_date, end_date)
        self._sync_sleep_data(start_date, end_date)
        self._sync_stress_data(start_date, end_date)
        self._sync_heart_rate_data(start_date, end_date)
        
        logger.info("Health data sync completed")
    
    def _sync_step_data(self, start_date, end_date):
        """Sync step data from Samsung Health"""
        try:
            # In a real implementation, you would call the Samsung Health API
            # This is a simulated example using random data
            import random
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Generate simulated data
                steps = random.randint(3000, 15000)
                distance = steps * 0.0007  # km
                calories = steps * 0.04  # kcal
                
                # Store in database
                cursor.execute('''
                INSERT OR REPLACE INTO steps (date, count, distance, calories, last_updated)
                VALUES (?, ?, ?, ?, ?)
                ''', (date_str, steps, distance, calories, int(time.time())))
                
                current_date += timedelta(days=1)
            
            conn.commit()
            conn.close()
            logger.info(f"Step data synced for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            logger.error(f"Error syncing step data: {str(e)}")
    
    def _sync_sleep_data(self, start_date, end_date):
        """Sync sleep data from Samsung Health"""
        try:
            # In a real implementation, you would call the Samsung Health API
            # This is a simulated example using random data
            import random
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Generate simulated data
                total_sleep = random.randint(5 * 60, 9 * 60)  # 5-9 hours in minutes
                deep_sleep = int(total_sleep * random.uniform(0.1, 0.3))
                rem_sleep = int(total_sleep * random.uniform(0.2, 0.3))
                light_sleep = total_sleep - deep_sleep - rem_sleep
                awake_time = random.randint(5, 30)
                quality = random.uniform(50, 95)
                
                # Store in database
                cursor.execute('''
                INSERT OR REPLACE INTO sleep (date, duration, deep_sleep, light_sleep, rem_sleep, awake_time, quality, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (date_str, total_sleep, deep_sleep, light_sleep, rem_sleep, awake_time, quality, int(time.time())))
                
                current_date += timedelta(days=1)
            
            conn.commit()
            conn.close()
            logger.info(f"Sleep data synced for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            logger.error(f"Error syncing sleep data: {str(e)}")
    
    def _sync_stress_data(self, start_date, end_date):
        """Sync stress data from Samsung Health"""
        try:
            # In a real implementation, you would call the Samsung Health API
            # This is a simulated example using random data
            import random
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                
                # Generate simulated data
                avg_level = random.randint(20, 60)
                max_level = min(100, avg_level + random.randint(10, 40))
                min_level = max(0, avg_level - random.randint(10, 20))
                duration = random.randint(30, 120)  # minutes
                
                # Store in database
                cursor.execute('''
                INSERT OR REPLACE INTO stress (date, average_level, max_level, min_level, duration, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (date_str, avg_level, max_level, min_level, duration, int(time.time())))
                
                current_date += timedelta(days=1)
            
            conn.commit()
            conn.close()
            logger.info(f"Stress data synced for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            logger.error(f"Error syncing stress data: {str(e)}")
    
    def _sync_heart_rate_data(self, start_date, end_date):
        """Sync heart rate data from Samsung Health"""
        try:
            # In a real implementation, you would call the Samsung Health API
            # This is a simulated example using random data
            import random
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Clear existing data in the range
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            cursor.execute("DELETE FROM heart_rate WHERE timestamp >= ? AND timestamp <= ?", 
                         (start_timestamp, end_timestamp))
            
            # Generate data points every hour
            current_time = start_date
            while current_time <= end_date:
                timestamp = int(current_time.timestamp())
                
                # Generate simulated heart rate
                bpm = random.randint(60, 100)
                
                # Store in database
                cursor.execute('''
                INSERT INTO heart_rate (timestamp, bpm, last_updated)
                VALUES (?, ?, ?)
                ''', (timestamp, bpm, int(time.time())))
                
                current_time += timedelta(hours=1)
            
            conn.commit()
            conn.close()
            logger.info(f"Heart rate data synced for {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            logger.error(f"Error syncing heart rate data: {str(e)}")
    
    def get_step_data(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get step data for a specific date or today"""
        if not date:
            date = datetime.now()
            
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT count, distance, calories FROM steps WHERE date = ?", (date_str,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return {
                    "date": date_str,
                    "steps": result[0],
                    "distance": result[1],
                    "calories": result[2]
                }
            else:
                return {
                    "date": date_str,
                    "steps": 0,
                    "distance": 0,
                    "calories": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting step data: {str(e)}")
            return {
                "date": date_str,
                "steps": 0,
                "distance": 0,
                "calories": 0,
                "error": str(e)
            }
    
    def get_sleep_data(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get sleep data for a specific date or yesterday"""
        if not date:
            # Default to yesterday for sleep data
            date = datetime.now() - timedelta(days=1)
            
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT duration, deep_sleep, light_sleep, rem_sleep, awake_time, quality 
                FROM sleep WHERE date = ?
            """, (date_str,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return {
                    "date": date_str,
                    "duration_minutes": result[0],
                    "duration_formatted": f"{result[0] // 60}h {result[0] % 60}m",
                    "deep_sleep_minutes": result[1],
                    "light_sleep_minutes": result[2],
                    "rem_sleep_minutes": result[3],
                    "awake_minutes": result[4],
                    "quality": result[5]
                }
            else:
                return {
                    "date": date_str,
                    "duration_minutes": 0,
                    "duration_formatted": "0h 0m",
                    "deep_sleep_minutes": 0,
                    "light_sleep_minutes": 0,
                    "rem_sleep_minutes": 0,
                    "awake_minutes": 0,
                    "quality": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting sleep data: {str(e)}")
            return {
                "date": date_str,
                "duration_minutes": 0,
                "duration_formatted": "0h 0m",
                "error": str(e)
            }
    
    def get_stress_data(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get stress data for a specific date or today"""
        if not date:
            date = datetime.now()
            
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT average_level, max_level, min_level, duration 
                FROM stress WHERE date = ?
            """, (date_str,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                # Interpret stress level
                avg_level = result[0]
                if avg_level < 30:
                    stress_category = "Low"
                elif avg_level < 60:
                    stress_category = "Moderate"
                else:
                    stress_category = "High"
                
                return {
                    "date": date_str,
                    "average_level": result[0],
                    "max_level": result[1],
                    "min_level": result[2],
                    "duration_minutes": result[3],
                    "stress_category": stress_category
                }
            else:
                return {
                    "date": date_str,
                    "average_level": 0,
                    "max_level": 0,
                    "min_level": 0,
                    "duration_minutes": 0,
                    "stress_category": "Unknown"
                }
                
        except Exception as e:
            logger.error(f"Error getting stress data: {str(e)}")
            return {
                "date": date_str,
                "average_level": 0,
                "stress_category": "Error",
                "error": str(e)
            }
    
    def get_heart_rate_data(self, period: str = "day") -> Dict[str, Any]:
        """Get heart rate data for a period (day, week, month)"""
        try:
            end_time = datetime.now()
            
            if period == "day":
                start_time = end_time - timedelta(days=1)
            elif period == "week":
                start_time = end_time - timedelta(days=7)
            elif period == "month":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
            
            start_timestamp = int(start_time.timestamp())
            end_timestamp = int(end_time.timestamp())
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, bpm FROM heart_rate 
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
            """, (start_timestamp, end_timestamp))
            
            results = cursor.fetchall()
            
            conn.close()
            
            data_points = []
            bpm_values = []
            
            for timestamp, bpm in results:
                time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                data_points.append({"time": time_str, "bpm": bpm})
                bpm_values.append(bpm)
            
            if bpm_values:
                avg_bpm = sum(bpm_values) / len(bpm_values)
                max_bpm = max(bpm_values)
                min_bpm = min(bpm_values)
            else:
                avg_bpm = 0
                max_bpm = 0
                min_bpm = 0
            
            return {
                "period": period,
                "data_points": data_points,
                "average_bpm": round(avg_bpm, 1),
                "max_bpm": max_bpm,
                "min_bpm": min_bpm,
                "count": len(data_points)
            }
                
        except Exception as e:
            logger.error(f"Error getting heart rate data: {str(e)}")
            return {
                "period": period,
                "data_points": [],
                "average_bpm": 0,
                "error": str(e)
            }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health data for today/yesterday"""
        try:
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            
            # Get step data for today
            steps_data = self.get_step_data(today)
            
            # Get sleep data for last night
            sleep_data = self.get_sleep_data(yesterday)
            
            # Get stress data for today
            stress_data = self.get_stress_data(today)
            
            # Get heart rate for last 24 hours
            heart_rate_data = self.get_heart_rate_data("day")
            
            # Create summary
            summary = {
                "date": today.strftime("%Y-%m-%d"),
                "steps": {
                    "count": steps_data["steps"],
                    "distance_km": round(steps_data["distance"], 2),
                    "calories": round(steps_data["calories"], 2)
                },
                "sleep": {
                    "duration": sleep_data["duration_formatted"],
                    "quality": sleep_data["quality"],
                    "deep_sleep_percent": round(sleep_data["deep_sleep_minutes"] / max(sleep_data["duration_minutes"], 1) * 100, 1)
                },
                "stress": {
                    "level": stress_data["average_level"],
                    "category": stress_data["stress_category"]
                },
                "heart_rate": {
                    "average": heart_rate_data["average_bpm"],
                    "max": heart_rate_data["max_bpm"],
                    "min": heart_rate_data["min_bpm"]
                }
            }
            
            # Add health score (simplified calculation)
            steps_score = min(100, steps_data["steps"] / 10000 * 100)
            sleep_score = sleep_data["quality"]
            stress_score = max(0, 100 - stress_data["average_level"])
            heart_score = 100 if 60 <= heart_rate_data["average_bpm"] <= 100 else max(0, 100 - abs(heart_rate_data["average_bpm"] - 80))
            
            health_score = (steps_score + sleep_score + stress_score + heart_score) / 4
            summary["health_score"] = round(health_score, 1)
            
            return summary
                
        except Exception as e:
            logger.error(f"Error getting health summary: {str(e)}")
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "error": str(e)
            }
    
    def interpret_health_data(self, summary: Dict[str, Any]) -> str:
        """Interpret health data and provide human-readable insights"""
        try:
            insights = []
            
            # Step insights
            steps = summary["steps"]["count"]
            if steps >= 10000:
                insights.append(f"Great job! You've taken {steps} steps today, exceeding the recommended 10,000 steps.")
            elif steps >= 7500:
                insights.append(f"Good progress! You've taken {steps} steps today, approaching the recommended 10,000 steps.")
            elif steps >= 5000:
                insights.append(f"You've taken {steps} steps today. Try to reach 10,000 for optimal health benefits.")
            else:
                insights.append(f"You've only taken {steps} steps today. Consider increasing your physical activity.")
            
            # Sleep insights
            sleep_minutes = summary["sleep"].get("duration_minutes", 0)
            if isinstance(sleep_minutes, str):
                # Handle case where duration is already formatted
                sleep_hours = 0
            else:
                sleep_hours = sleep_minutes / 60
                
            if sleep_hours >= 7 and sleep_hours <= 9:
                insights.append(f"You slept for {summary['sleep']['duration']}, which is within the recommended 7-9 hours.")
            elif sleep_hours > 9:
                insights.append(f"You slept for {summary['sleep']['duration']}, which is longer than usual. Extended sleep can sometimes indicate fatigue.")
            elif sleep_hours >= 6:
                insights.append(f"You slept for {summary['sleep']['duration']}, slightly below the recommended 7-9 hours.")
            else:
                insights.append(f"You only slept for {summary['sleep']['duration']}. Lack of sleep can impact your cognitive functions and overall health.")
            
            # Deep sleep insights
            deep_sleep_percent = summary["sleep"].get("deep_sleep_percent", 0)
            if deep_sleep_percent >= 25:
                insights.append(f"Your deep sleep percentage is excellent at {deep_sleep_percent}%, supporting memory consolidation and recovery.")
            elif deep_sleep_percent >= 15:
                insights.append(f"Your deep sleep percentage is adequate at {deep_sleep_percent}%.")
            else:
                insights.append(f"Your deep sleep percentage is low at {deep_sleep_percent}%. Consider improving sleep quality.")
            
            # Stress insights
            stress_category = summary["stress"]["category"]
            if stress_category == "Low":
                insights.append("Your stress levels are low today, which is excellent for your overall wellbeing.")
            elif stress_category == "Moderate":
                insights.append("You're experiencing moderate stress levels. Consider taking short breaks for relaxation.")
            elif stress_category == "High":
                insights.append("Your stress levels are high. Consider stress management techniques like deep breathing or meditation.")
            
            # Heart rate insights
            avg_bpm = summary["heart_rate"]["average"]
            if 60 <= avg_bpm <= 100:
                insights.append(f"Your average heart rate of {avg_bpm} bpm is within the normal resting range.")
            elif avg_bpm < 60:
                insights.append(f"Your average heart rate of {avg_bpm} bpm is below the typical resting range, which can be normal for athletes.")
            else:
                insights.append(f"Your average heart rate of {avg_bpm} bpm is elevated. This could be due to activity, stress, or other factors.")
            
            # Overall health score
            health_score = summary.get("health_score", 0)
            if health_score >= 80:
                insights.append(f"Your overall health score is excellent at {health_score}/100. Keep up the good work!")
            elif health_score >= 60:
                insights.append(f"Your overall health score is good at {health_score}/100. There's room for some improvement.")
            else:
                insights.append(f"Your overall health score is {health_score}/100. Focus on improving your sleep, physical activity, and stress management.")
            
            return "\n\n".join(insights)
                
        except Exception as e:
            logger.error(f"Error interpreting health data: {str(e)}")
            return "I couldn't interpret your health data at this time. Please try again later."
    
    def shutdown(self):
        """Shutdown health integration"""
        logger.info("Shutting down health integration")
        self.running = False
        
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=2.0) 