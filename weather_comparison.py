"""Weather comparison tool for multiple cities."""

from typing import List, Dict, Optional
import customtkinter as ctk
from api import get_current_weather, get_air_quality, get_coordinates
import logging

logger = logging.getLogger(__name__)


class WeatherComparison:
    """Compare weather between multiple cities."""
    
    def __init__(self, units: str = "metric"):
        """Initialize comparison tool.
        
        Args:
            units: Unit system ('metric' or 'imperial')
        """
        self.units = units
        self.cities_data: List[Dict] = []
    
    def add_city(self, city: str) -> bool:
        """Add a city to comparison (max 3).
        
        Args:
            city: City name to add
            
        Returns:
            True if added, False if limit reached
        """
        if len(self.cities_data) >= 3:
            return False
        
        try:
            lat, lon = get_coordinates(city)
            if lat is None or lon is None:
                return False
            
            weather = get_current_weather(city, self.units)
            if not weather:
                return False
            
            air_quality = get_air_quality(lat, lon)
            
            temp, condition, humidity, wind_speed, icon_code = weather
            
            self.cities_data.append({
                "city": city,
                "temp": temp,
                "condition": condition,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "icon_code": icon_code,
                "air_quality": air_quality,
                "lat": lat,
                "lon": lon
            })
            logger.info(f"Added {city} to comparison")
            return True
        except Exception as e:
            logger.error(f"Error adding city to comparison: {str(e)}")
            return False
    
    def remove_city(self, city: str) -> None:
        """Remove a city from comparison.
        
        Args:
            city: City name to remove
        """
        self.cities_data = [
            c for c in self.cities_data if c["city"] != city
        ]
        logger.info(f"Removed {city} from comparison")
    
    def clear(self) -> None:
        """Clear all cities from comparison."""
        self.cities_data = []
    
    def get_comparison_text(self) -> str:
        """Generate comparison display text.
        
        Returns:
            Formatted comparison text
        """
        if not self.cities_data:
            return "No cities to compare. Add cities to compare weather."
        
        text = "🌍 WEATHER COMPARISON\n" + "="*50 + "\n\n"
        
        for i, city_data in enumerate(self.cities_data, 1):
            city = city_data["city"]
            temp = city_data["temp"]
            condition = city_data["condition"]
            humidity = city_data["humidity"]
            wind = city_data["wind_speed"]
            aqi = city_data["air_quality"]
            
            text += f"[{i}] {city.upper()}\n"
            text += f"    🌡️ {temp}°\n"
            text += f"    ☁️ {condition}\n"
            text += f"    💧 {humidity}% humidity\n"
            text += f"    💨 {wind} wind\n"
            text += f"    🌫️ AQI: {aqi}\n\n"
        
        return text
    
    def get_city_names(self) -> List[str]:
        """Get list of compared city names.
        
        Returns:
            List of city names
        """
        return [c["city"] for c in self.cities_data]
    
    def get_warmest_city(self) -> Optional[str]:
        """Get the warmest city in comparison.
        
        Returns:
            City name with highest temperature
        """
        if not self.cities_data:
            return None
        return max(
            self.cities_data, key=lambda x: x["temp"]
        )["city"]
    
    def get_coldest_city(self) -> Optional[str]:
        """Get the coldest city in comparison.
        
        Returns:
            City name with lowest temperature
        """
        if not self.cities_data:
            return None
        return min(
            self.cities_data, key=lambda x: x["temp"]
        )["city"]
    
    def get_most_humid_city(self) -> Optional[str]:
        """Get city with highest humidity.
        
        Returns:
            City name with highest humidity
        """
        if not self.cities_data:
            return None
        return max(
            self.cities_data, key=lambda x: x["humidity"]
        )["city"]
    
    def get_windiest_city(self) -> Optional[str]:
        """Get city with highest wind speed.
        
        Returns:
            City name with highest wind speed
        """
        if not self.cities_data:
            return None
        return max(
            self.cities_data, key=lambda x: x["wind_speed"]
        )["city"]
