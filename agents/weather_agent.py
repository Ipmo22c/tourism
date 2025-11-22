"""
Weather Agent - Fetches current weather and forecast using Open-Meteo API
"""
import requests
from typing import Dict, Optional, Tuple


class WeatherAgent:
    """Child Agent 1: Handles weather information for a given location"""
    
    def __init__(self):
        self.api_base = "https://api.open-meteo.com/v1/forecast"
    
    def get_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Fetch current weather and forecast for given coordinates
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            
        Returns:
            Dictionary with weather information or None if error
        """
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,precipitation_probability",
                "forecast_days": 1
            }
            
            response = requests.get(self.api_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "current" in data:
                current = data["current"]
                temperature = current.get("temperature_2m", "N/A")
                precipitation_prob = current.get("precipitation_probability", 0)
                
                return {
                    "temperature": temperature,
                    "precipitation_probability": precipitation_prob,
                    "success": True
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            return None
    
    def format_weather_response(self, weather_data: Dict, place_name: str) -> str:
        """
        Format weather data into a user-friendly response
        
        Args:
            weather_data: Weather data dictionary
            place_name: Name of the place
            
        Returns:
            Formatted string response
        """
        if not weather_data or not weather_data.get("success"):
            return f"Unable to fetch weather information for {place_name}."
        
        temp = weather_data.get("temperature", None)
        rain_chance = weather_data.get("precipitation_probability", 0)
        
        # Format temperature - always show with unit
        if temp is not None:
            temp_str = f"{round(temp)}°C"
        else:
            temp_str = "N/A"
        
        # Round rain chance to nearest integer
        rain_chance_rounded = round(rain_chance)
        
        return f"In {place_name} it's currently {temp_str} with a chance of {rain_chance_rounded}% to rain."

