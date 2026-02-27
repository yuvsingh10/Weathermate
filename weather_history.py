"""Weather history tracker for temperature trends."""

from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WeatherHistory:
    """Track weather history for trend analysis (in-memory, not persisted)."""
    
    def __init__(self):
        """Initialize weather history tracker."""
        self.history: Dict[str, List[Dict]] = {}
    
    def add_record(self, city: str, temp: float, condition: str) -> None:
        """Add weather record for a city.
        
        Args:
            city: City name
            temp: Temperature
            condition: Weather condition
        """
        if city not in self.history:
            self.history[city] = []
        
        timestamp = datetime.now().isoformat()
        
        self.history[city].append({
            "timestamp": timestamp,
            "temp": temp,
            "condition": condition
        })
        
        # Keep only last 30 records per city
        if len(self.history[city]) > 30:
            self.history[city] = self.history[city][-30:]
    
    def get_history(self, city: str, limit: int = 10) -> List[Dict]:
        """Get weather history for a city.
        
        Args:
            city: City name
            limit: Max number of records to return
            
        Returns:
            List of weather records
        """
        if city not in self.history:
            return []
        return self.history[city][-limit:]
    
    def get_temperature_trend(self, city: str) -> List[float]:
        """Get temperature trend for a city.
        
        Args:
            city: City name
            
        Returns:
            List of temperatures in chronological order
        """
        history = self.get_history(city, limit=30)
        return [h["temp"] for h in history]
    
    def get_avg_temperature(self, city: str) -> Optional[float]:
        """Get average temperature for a city.
        
        Args:
            city: City name
            
        Returns:
            Average temperature or None
        """
        temps = self.get_temperature_trend(city)
        if not temps:
            return None
        return sum(temps) / len(temps)
    
    def get_max_temperature(self, city: str) -> Optional[float]:
        """Get maximum temperature recorded for a city.
        
        Args:
            city: City name
            
        Returns:
            Maximum temperature or None
        """
        temps = self.get_temperature_trend(city)
        if not temps:
            return None
        return max(temps)
    
    def get_min_temperature(self, city: str) -> Optional[float]:
        """Get minimum temperature recorded for a city.
        
        Args:
            city: City name
            
        Returns:
            Minimum temperature or None
        """
        temps = self.get_temperature_trend(city)
        if not temps:
            return None
        return min(temps)
    
    def clear_city_history(self, city: str) -> None:
        """Clear history for a specific city.
        
        Args:
            city: City name
        """
        if city in self.history:
            del self.history[city]
    
    def get_all_cities(self) -> List[str]:
        """Get all cities with recorded history.
        
        Returns:
            List of city names
        """
        return list(self.history.keys())
