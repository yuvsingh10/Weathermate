"""Data models for Weather Mate application."""

from typing import Optional, NamedTuple
from config import AQILevel


class WeatherData(NamedTuple):
    """Named tuple for current weather data.
    
    Attributes:
        temperature: Temperature value
        condition: Weather condition description
        humidity: Humidity percentage (0-100)
        wind_speed: Wind speed in specified units
        icon_code: OpenWeatherMap icon code
    """
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    icon_code: str


class Coordinates(NamedTuple):
    """Named tuple for geographic coordinates.
    
    Attributes:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    """
    latitude: float
    longitude: float


class AirQualityData(NamedTuple):
    """Named tuple for air quality data.
    
    Attributes:
        aqi_level: Air quality level as AQILevel enum
        aqi_value: Numeric AQI value (1-5)
        description: Human-readable AQI description
    """
    aqi_level: AQILevel
    aqi_value: int
    description: str
    
    @classmethod
    def from_value(cls, aqi_value: int) -> 'AirQualityData':
        """Create AirQualityData from numeric AQI value.
        
        Args:
            aqi_value: Numeric AQI value (1-5)
            
        Returns:
            AirQualityData instance
        """
        aqi_level = AQILevel.from_value(aqi_value)
        return cls(
            aqi_level=aqi_level,
            aqi_value=aqi_value,
            description=aqi_level.description
        )
