"""Response validation utilities for Weather Mate API."""

from typing import Any, Dict, List, Optional
import logging
from config import AQILevel

logger = logging.getLogger(__name__)


def validate_json_response(response_data: Any) -> bool:
    """Validate that response is a dictionary.
    
    Args:
        response_data: Data to validate
        
    Returns:
        True if valid, raises exception otherwise
    """
    if not isinstance(response_data, dict):
        raise ValueError(f"Expected dict response, got {type(response_data).__name__}")
    return True


def validate_key_exists(data: Dict, key: str, key_path: str = "") -> bool:
    """Validate that a key exists in a dictionary.
    
    Args:
        data: Dictionary to check
        key: Key to look for
        key_path: Path to the key (for error messages)
        
    Returns:
        True if key exists, raises exception otherwise
    """
    if key not in data:
        full_path = f"{key_path}.{key}" if key_path else key
        raise KeyError(f"Missing required key: '{full_path}'")
    return True


def validate_nested_key(data: Dict, keys: List[str], key_path: str = "") -> Any:
    """Validate and retrieve a nested key from a dictionary.
    
    Args:
        data: Dictionary to search
        keys: List of keys to traverse (e.g., ["coord", "lat"])
        key_path: Path for error messages
        
    Returns:
        The value at the nested key path
        
    Raises:
        KeyError if any key in the path is missing
        TypeError if intermediate value is not a dict
    """
    current = data
    current_path = key_path
    
    for key in keys:
        if not isinstance(current, dict):
            raise TypeError(f"Expected dict at '{current_path}', got {type(current).__name__}")
        
        if key not in current:
            full_path = f"{current_path}.{key}" if current_path else key
            raise KeyError(f"Missing required key: '{full_path}'")
        
        current = current[key]
        current_path = f"{current_path}.{key}" if current_path else key
    
    return current


def validate_coordinates_response(data: Dict) -> Dict:
    """Validate OpenWeatherMap coordinates response structure.
    
    Args:
        data: Response data from weather API
        
    Returns:
        The validated 'coord' dictionary
        
    Raises:
        KeyError if required keys are missing
        TypeError if response structure is wrong
        ValueError if values are invalid
    """
    validate_json_response(data)
    validate_key_exists(data, "coord")
    
    coord = data["coord"]
    if not isinstance(coord, dict):
        raise TypeError(f"Expected 'coord' to be dict, got {type(coord).__name__}")
    
    # Validate latitude and longitude
    for key in ["lat", "lon"]:
        validate_key_exists(coord, key, "coord")
        value = coord[key]
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Expected 'coord.{key}' to be number, "
                f"got {type(value).__name__}: {value}"
            )
        # Check if value is in valid range for coordinates
        if key == "lat" and not (-90 <= value <= 90):
            raise ValueError(f"Latitude out of range: {value}")
        if key == "lon" and not (-180 <= value <= 180):
            raise ValueError(f"Longitude out of range: {value}")
    
    return coord


def validate_current_weather_response(data: Dict) -> Dict:
    """Validate OpenWeatherMap current weather response structure.
    
    Args:
        data: Response data from weather API
        
    Returns:
        The validated response data
        
    Raises:
        KeyError if required keys are missing
        TypeError if response structure is wrong
        ValueError if values are invalid
    """
    validate_json_response(data)
    
    # Validate main section
    validate_key_exists(data, "main")
    main = data["main"]
    if not isinstance(main, dict):
        raise TypeError(f"Expected 'main' to be dict, got {type(main).__name__}")
    for key in ["temp", "humidity"]:
        validate_key_exists(main, key, "main")
        value = main[key]
        if not isinstance(value, (int, float)):
            raise ValueError(
                f"Expected 'main.{key}' to be number, "
                f"got {type(value).__name__}: {value}"
            )
    
    # Validate weather array
    validate_key_exists(data, "weather")
    weather = data["weather"]
    if not isinstance(weather, list):
        raise TypeError(f"Expected 'weather' to be list, got {type(weather).__name__}")
    if len(weather) == 0:
        raise ValueError("'weather' array is empty")
    
    weather_item = weather[0]
    if not isinstance(weather_item, dict):
        raise TypeError(f"Expected 'weather[0]' to be dict, got {type(weather_item).__name__}")
    for key in ["description", "icon"]:
        validate_key_exists(weather_item, key, "weather[0]")
        value = weather_item[key]
        if not isinstance(value, str):
            raise ValueError(
                f"Expected 'weather[0].{key}' to be string, "
                f"got {type(value).__name__}: {value}"
            )
    
    # Validate wind section
    validate_key_exists(data, "wind")
    wind = data["wind"]
    if not isinstance(wind, dict):
        raise TypeError(f"Expected 'wind' to be dict, got {type(wind).__name__}")
    validate_key_exists(wind, "speed", "wind")
    speed = wind["speed"]
    if not isinstance(speed, (int, float)):
        raise ValueError(
            f"Expected 'wind.speed' to be number, "
            f"got {type(speed).__name__}: {speed}"
        )
    
    return data


def validate_air_quality_response(data: Dict) -> Dict:
    """Validate OpenWeatherMap air quality response structure.
    
    Args:
        data: Response data from air quality API
        
    Returns:
        The validated response data
        
    Raises:
        KeyError if required keys are missing
        TypeError if response structure is wrong
        ValueError if values are invalid
    """
    validate_json_response(data)
    validate_key_exists(data, "list")
    
    aqi_list = data["list"]
    if not isinstance(aqi_list, list):
        raise TypeError(f"Expected 'list' to be list, got {type(aqi_list).__name__}")
    if len(aqi_list) == 0:
        raise ValueError("'list' array is empty")
    
    aqi_item = aqi_list[0]
    if not isinstance(aqi_item, dict):
        raise TypeError(f"Expected 'list[0]' to be dict, got {type(aqi_item).__name__}")
    
    validate_key_exists(aqi_item, "main", "list[0]")
    main = aqi_item["main"]
    if not isinstance(main, dict):
        raise TypeError(f"Expected 'list[0].main' to be dict, got {type(main).__name__}")
    
    validate_key_exists(main, "aqi", "list[0].main")
    aqi_value = main["aqi"]
    if not isinstance(aqi_value, int):
        raise ValueError(
            f"Expected 'list[0].main.aqi' to be integer, "
            f"got {type(aqi_value).__name__}: {aqi_value}"
        )
    
    # Validate using AQILevel enum
    try:
        AQILevel.from_value(aqi_value)
    except ValueError as e:
        raise ValueError(f"Invalid AQI value in response: {aqi_value}. {str(e)}")
    
    return data


def validate_forecast_response(data: Dict) -> List[Dict]:
    """Validate OpenWeatherMap forecast response structure.
    
    Args:
        data: Response data from forecast API
        
    Returns:
        The validated 'list' array
        
    Raises:
        KeyError if required keys are missing
        TypeError if response structure is wrong
        ValueError if values are invalid
    """
    validate_json_response(data)
    validate_key_exists(data, "list")
    
    forecast_list = data["list"]
    if not isinstance(forecast_list, list):
        raise TypeError(f"Expected 'list' to be list, got {type(forecast_list).__name__}")
    if len(forecast_list) == 0:
        raise ValueError("'list' array is empty")
    
    # Validate first forecast item structure
    first_item = forecast_list[0]
    if not isinstance(first_item, dict):
        raise TypeError(f"Expected 'list[0]' to be dict, got {type(first_item).__name__}")
    
    # Check required keys
    for key in ["dt_txt", "main", "weather"]:
        validate_key_exists(first_item, key, "list[0]")
    
    # Validate dt_txt is string
    dt_txt = first_item["dt_txt"]
    if not isinstance(dt_txt, str):
        raise ValueError(
            f"Expected 'list[0].dt_txt' to be string, "
            f"got {type(dt_txt).__name__}: {dt_txt}"
        )
    
    # Validate main structure
    main = first_item["main"]
    if not isinstance(main, dict):
        raise TypeError(f"Expected 'list[0].main' to be dict, got {type(main).__name__}")
    if "temp" not in main:
        raise KeyError("Missing required key: 'list[0].main.temp'")
    if not isinstance(main["temp"], (int, float)):
        raise ValueError(
            f"Expected 'list[0].main.temp' to be number, "
            f"got {type(main['temp']).__name__}: {main['temp']}"
        )
    
    # Validate weather array
    weather = first_item["weather"]
    if not isinstance(weather, list):
        raise TypeError(f"Expected 'list[0].weather' to be list, got {type(weather).__name__}")
    if len(weather) == 0:
        raise ValueError("'list[0].weather' array is empty")
    
    weather_item = weather[0]
    if not isinstance(weather_item, dict):
        raise TypeError(
            f"Expected 'list[0].weather[0]' to be dict, "
            f"got {type(weather_item).__name__}"
        )
    for key in ["description", "icon"]:
        if key not in weather_item:
            raise KeyError(f"Missing required key: 'list[0].weather[0].{key}'")
        value = weather_item[key]
        if not isinstance(value, str):
            raise ValueError(
                f"Expected 'list[0].weather[0].{key}' to be string, "
                f"got {type(value).__name__}: {value}"
            )
    
    return forecast_list
