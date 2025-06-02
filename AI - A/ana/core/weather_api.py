#!/usr/bin/env python3
# Ana AI Assistant - Weather API Module

import os
import json
import logging
import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger('Ana.WeatherAPI')

class WeatherAPI:
    """
    Weather API integration for Ana
    
    Features:
    - Fetch current weather conditions
    - Get forecasts
    - Support for multiple weather API providers
    - Caching to prevent excessive API calls
    """
    
    def __init__(self, security_manager=None, settings: Dict[str, Any] = None):
        """Initialize the weather API module"""
        self.security_manager = security_manager
        self.settings = settings or {}
        
        # Default settings
        self.api_provider = self.settings.get("weather_api_provider", "openweathermap")
        self.units = self.settings.get("weather_units", "metric")  # metric or imperial
        self.default_location = self.settings.get("default_location", "New York")
        
        # API keys
        self.api_keys = {}
        self._load_api_keys()
        
        # Cache for weather data
        self.weather_cache = {}
        self.cache_duration = 3600  # Cache weather data for 1 hour
        
        logger.info("Weather API initialized")
    
    def _load_api_keys(self):
        """Load API keys from secure storage"""
        if self.security_manager:
            # Try to get API keys from secure storage
            openweathermap_creds = self.security_manager.get_api_credentials("openweathermap")
            if openweathermap_creds and "api_key" in openweathermap_creds:
                self.api_keys["openweathermap"] = openweathermap_creds["api_key"]
            
            weatherapi_creds = self.security_manager.get_api_credentials("weatherapi")
            if weatherapi_creds and "api_key" in weatherapi_creds:
                self.api_keys["weatherapi"] = weatherapi_creds["api_key"]
        
        # Fallback to settings if not in secure storage
        if "openweathermap" not in self.api_keys:
            self.api_keys["openweathermap"] = self.settings.get("openweathermap_api_key", "")
        
        if "weatherapi" not in self.api_keys:
            self.api_keys["weatherapi"] = self.settings.get("weatherapi_api_key", "")
    
    def get_current_weather(self, location: str = None) -> Dict[str, Any]:
        """
        Get current weather conditions for a location
        
        Args:
            location: Location to get weather for (city name, coordinates, etc.)
            
        Returns:
            Dict with weather data
        """
        location = location or self.default_location
        
        # Check cache first
        cache_key = f"current_{location}_{self.units}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch weather data based on provider
        weather_data = {}
        
        if self.api_provider == "openweathermap":
            weather_data = self._fetch_openweathermap(location)
        elif self.api_provider == "weatherapi":
            weather_data = self._fetch_weatherapi(location)
        else:
            # Fallback to dummy data if no provider is available
            weather_data = self._get_dummy_weather(location)
        
        # Cache the result
        if weather_data:
            self._add_to_cache(cache_key, weather_data)
        
        return weather_data
    
    def _fetch_openweathermap(self, location: str) -> Dict[str, Any]:
        """Fetch weather from OpenWeatherMap API"""
        api_key = self.api_keys.get("openweathermap")
        if not api_key:
            logger.warning("OpenWeatherMap API key not found")
            return self._get_dummy_weather(location)
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": self.units
            }
            
            # Apply privacy measures if security manager available
            if self.security_manager:
                params = self.security_manager.secure_api_request(
                    "openweathermap", 
                    params,
                    include_credentials=False
                )
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Format the response
            return {
                "location": {
                    "name": data.get("name", location),
                    "country": data.get("sys", {}).get("country", ""),
                    "lat": data.get("coord", {}).get("lat", 0),
                    "lon": data.get("coord", {}).get("lon", 0)
                },
                "current": {
                    "temp": data.get("main", {}).get("temp", 0),
                    "feels_like": data.get("main", {}).get("feels_like", 0),
                    "humidity": data.get("main", {}).get("humidity", 0),
                    "pressure": data.get("main", {}).get("pressure", 0),
                    "wind_speed": data.get("wind", {}).get("speed", 0),
                    "wind_direction": data.get("wind", {}).get("deg", 0),
                    "condition": data.get("weather", [{}])[0].get("main", "Clear"),
                    "description": data.get("weather", [{}])[0].get("description", "Clear sky"),
                    "icon": data.get("weather", [{}])[0].get("icon", "01d"),
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "units": self.units
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather from OpenWeatherMap: {str(e)}")
            return self._get_dummy_weather(location)
    
    def _fetch_weatherapi(self, location: str) -> Dict[str, Any]:
        """Fetch weather from WeatherAPI.com"""
        api_key = self.api_keys.get("weatherapi")
        if not api_key:
            logger.warning("WeatherAPI.com API key not found")
            return self._get_dummy_weather(location)
        
        try:
            url = f"https://api.weatherapi.com/v1/current.json"
            params = {
                "q": location,
                "key": api_key
            }
            
            # Apply privacy measures if security manager available
            if self.security_manager:
                params = self.security_manager.secure_api_request(
                    "weatherapi", 
                    params,
                    include_credentials=False
                )
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Format the response
            return {
                "location": {
                    "name": data.get("location", {}).get("name", location),
                    "country": data.get("location", {}).get("country", ""),
                    "lat": data.get("location", {}).get("lat", 0),
                    "lon": data.get("location", {}).get("lon", 0)
                },
                "current": {
                    "temp": data.get("current", {}).get("temp_c" if self.units == "metric" else "temp_f", 0),
                    "feels_like": data.get("current", {}).get("feelslike_c" if self.units == "metric" else "feelslike_f", 0),
                    "humidity": data.get("current", {}).get("humidity", 0),
                    "pressure": data.get("current", {}).get("pressure_mb", 0),
                    "wind_speed": data.get("current", {}).get("wind_kph" if self.units == "metric" else "wind_mph", 0),
                    "wind_direction": data.get("current", {}).get("wind_degree", 0),
                    "condition": data.get("current", {}).get("condition", {}).get("text", "Clear"),
                    "description": data.get("current", {}).get("condition", {}).get("text", "Clear sky"),
                    "icon": data.get("current", {}).get("condition", {}).get("icon", ""),
                    "time": data.get("current", {}).get("last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                },
                "units": self.units
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather from WeatherAPI.com: {str(e)}")
            return self._get_dummy_weather(location)
    
    def _get_dummy_weather(self, location: str) -> Dict[str, Any]:
        """Generate dummy weather data when API is unavailable"""
        import random
        
        # Random temperature based on current month
        month = datetime.now().month
        if 3 <= month <= 5:  # Spring
            temp = random.uniform(10, 25)
        elif 6 <= month <= 8:  # Summer
            temp = random.uniform(20, 35)
        elif 9 <= month <= 11:  # Fall
            temp = random.uniform(5, 20)
        else:  # Winter
            temp = random.uniform(-5, 10)
        
        # Random conditions
        conditions = ["Clear", "Clouds", "Rain", "Snow", "Thunderstorm", "Drizzle", "Mist"]
        condition = random.choice(conditions)
        
        # Descriptions based on condition
        descriptions = {
            "Clear": "Clear sky",
            "Clouds": ["Few clouds", "Scattered clouds", "Broken clouds", "Overcast clouds"],
            "Rain": ["Light rain", "Moderate rain", "Heavy rain"],
            "Snow": ["Light snow", "Moderate snow", "Heavy snow"],
            "Thunderstorm": ["Thunderstorm", "Heavy thunderstorm"],
            "Drizzle": ["Light drizzle", "Drizzle"],
            "Mist": ["Mist", "Fog"]
        }
        
        description = descriptions[condition]
        if isinstance(description, list):
            description = random.choice(description)
        
        return {
            "location": {
                "name": location,
                "country": "Unknown",
                "lat": 0,
                "lon": 0
            },
            "current": {
                "temp": temp,
                "feels_like": temp - random.uniform(-2, 2),
                "humidity": random.randint(30, 90),
                "pressure": random.randint(980, 1030),
                "wind_speed": random.uniform(0, 30),
                "wind_direction": random.randint(0, 359),
                "condition": condition,
                "description": description,
                "icon": "",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "units": self.units,
            "note": "This is simulated weather data"
        }
    
    def _add_to_cache(self, key: str, data: Dict[str, Any]):
        """Add weather data to cache"""
        self.weather_cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get weather data from cache if not expired"""
        if key in self.weather_cache:
            cache_entry = self.weather_cache[key]
            if time.time() - cache_entry["timestamp"] < self.cache_duration:
                logger.debug(f"Using cached weather data for {key}")
                return cache_entry["data"]
            else:
                # Cache expired
                del self.weather_cache[key]
        
        return None
    
    def get_forecast(self, location: str = None, days: int = 3) -> Dict[str, Any]:
        """
        Get weather forecast for a location
        
        Args:
            location: Location to get forecast for
            days: Number of days to forecast (1-7)
            
        Returns:
            Dict with forecast data
        """
        location = location or self.default_location
        days = min(max(1, days), 7)  # Limit to 1-7 days
        
        # Check cache first
        cache_key = f"forecast_{location}_{days}_{self.units}"
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # For now, just return dummy forecast data
        # In a real implementation, this would call the appropriate API
        forecast_data = self._get_dummy_forecast(location, days)
        
        # Cache the result
        self._add_to_cache(cache_key, forecast_data)
        
        return forecast_data
    
    def _get_dummy_forecast(self, location: str, days: int) -> Dict[str, Any]:
        """Generate dummy forecast data"""
        import random
        
        current = self.get_current_weather(location)
        forecasts = []
        
        current_temp = current.get("current", {}).get("temp", 20)
        current_condition = current.get("current", {}).get("condition", "Clear")
        
        for i in range(days):
            # Generate forecast for each day
            date = (datetime.now() + datetime.timedelta(days=i+1)).strftime("%Y-%m-%d")
            
            # Temperature varies by ±5 degrees from previous day
            temp = current_temp + random.uniform(-5, 5)
            
            # Conditions have some continuity
            if random.random() < 0.7:
                # 70% chance to keep similar condition
                condition = current_condition
            else:
                # 30% chance to change condition
                conditions = ["Clear", "Clouds", "Rain", "Snow", "Thunderstorm", "Drizzle", "Mist"]
                condition = random.choice(conditions)
            
            # Descriptions based on condition
            descriptions = {
                "Clear": "Clear sky",
                "Clouds": ["Few clouds", "Scattered clouds", "Broken clouds", "Overcast clouds"],
                "Rain": ["Light rain", "Moderate rain", "Heavy rain"],
                "Snow": ["Light snow", "Moderate snow", "Heavy snow"],
                "Thunderstorm": ["Thunderstorm", "Heavy thunderstorm"],
                "Drizzle": ["Light drizzle", "Drizzle"],
                "Mist": ["Mist", "Fog"]
            }
            
            description = descriptions[condition]
            if isinstance(description, list):
                description = random.choice(description)
            
            forecasts.append({
                "date": date,
                "temp_min": temp - random.uniform(1, 5),
                "temp_max": temp + random.uniform(1, 5),
                "humidity": random.randint(30, 90),
                "pressure": random.randint(980, 1030),
                "wind_speed": random.uniform(0, 30),
                "condition": condition,
                "description": description
            })
            
            # Set for next iteration
            current_temp = temp
            current_condition = condition
        
        return {
            "location": current.get("location", {}),
            "current": current.get("current", {}),
            "forecast": forecasts,
            "units": self.units,
            "note": "This is simulated forecast data"
        }
    
    def set_default_location(self, location: str):
        """Set the default location for weather queries"""
        self.default_location = location
        
        # Update settings if available
        if self.settings:
            self.settings["default_location"] = location
            
        logger.info(f"Default weather location set to: {location}")
    
    def set_units(self, units: str):
        """Set the units for weather data (metric or imperial)"""
        if units not in ["metric", "imperial"]:
            logger.warning(f"Invalid units '{units}', must be 'metric' or 'imperial'")
            return
            
        self.units = units
        
        # Update settings if available
        if self.settings:
            self.settings["weather_units"] = units
            
        logger.info(f"Weather units set to: {units}")
        
        # Clear cache since units changed
        self.weather_cache = {}


# For testing directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create weather API
    weather_api = WeatherAPI()
    
    # Test getting current weather
    weather = weather_api.get_current_weather("London")
    print("Current weather in London:")
    print(f"Temperature: {weather['current']['temp']}°C")
    print(f"Condition: {weather['current']['condition']}")
    print(f"Description: {weather['current']['description']}")
    
    # Test getting forecast
    forecast = weather_api.get_forecast("Tokyo", days=3)
    print("\nForecast for Tokyo:")
    for day in forecast["forecast"]:
        print(f"{day['date']}: {day['condition']}, {day['temp_min']:.1f}°C - {day['temp_max']:.1f}°C") 