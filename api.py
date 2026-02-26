"""API functions for Weather Mate application."""

import requests
from typing import Tuple, Optional
import logging

from validation import (
    validate_coordinates_response, validate_current_weather_response,
    validate_air_quality_response, validate_forecast_response
)
from config import (
    API_KEY, WEATHER_URL, FORECAST_URL, AIR_QUALITY_URL, ICON_URL, API_TIMEOUT,
    INTERVALS_PER_FORECAST, HOURS_PER_INTERVAL, MIN_CITY_NAME_LENGTH, MAX_CITY_NAME_LENGTH,
    UNITS_METRIC, TEMP_UNIT_METRIC, TEMP_UNIT_IMPERIAL,
    AQILevel, AQI_LEVELS,
    ERROR_EMPTY_CITY, ERROR_CITY_TOO_SHORT, ERROR_CITY_TOO_LONG, ERROR_INVALID_CHARS,
    ERROR_NO_LETTERS, ERROR_PURELY_NUMERIC, ERROR_TOO_MANY_SPECIAL,
    MSG_UNAVAILABLE_INVALID_RESPONSE, MSG_UNAVAILABLE_API_KEY, MSG_UNAVAILABLE_RATE_LIMITED,
    MSG_UNAVAILABLE_API_ERROR, MSG_UNAVAILABLE_TIMEOUT, MSG_UNAVAILABLE_NO_CONNECTION,
    MSG_UNAVAILABLE_NETWORK_ERROR,
    MSG_FORECAST_UNAVAILABLE_NO_DATA, MSG_FORECAST_UNAVAILABLE_PARSE_ERROR,
    MSG_FORECAST_UNAVAILABLE_INVALID_RESPONSE, MSG_FORECAST_UNAVAILABLE_API_KEY,
    MSG_FORECAST_UNAVAILABLE_RATE_LIMITED, MSG_FORECAST_UNAVAILABLE_API_ERROR,
    MSG_FORECAST_UNAVAILABLE_TIMEOUT, MSG_FORECAST_UNAVAILABLE_NO_CONNECTION,
    MSG_FORECAST_UNAVAILABLE_NETWORK_ERROR,
    logger
)


def validate_city_input(city: str) -> Tuple[bool, Optional[str]]:
    """
    Validate city name input.
    
    Args:
        city: City name to validate
    
    Returns: Tuple of (is_valid: bool, error_message: str or None)
    """
    # Check if empty (already done but for completeness)
    if not city or len(city.strip()) == 0:
        return False, ERROR_EMPTY_CITY
    
    # Check length
    if len(city) < MIN_CITY_NAME_LENGTH:
        return False, ERROR_CITY_TOO_SHORT
    if len(city) > MAX_CITY_NAME_LENGTH:
        return False, ERROR_CITY_TOO_LONG
    
    # Check for invalid special characters (only allow letters, spaces, hyphens, apostrophes, commas)
    # Unicode letters are allowed for international city names
    import re
    valid_pattern = (
        r'^[\p{L}\p{N}\s\-\',\.]+$' if hasattr(re, 'UNICODE')
        else r'^[a-zA-Z0-9\s\-\',.]+$'
    )
    
    # Alternative: Check if input contains only acceptable characters
    invalid_chars = set()
    for char in city:
        # Allow: letters (a-z, A-Z), digits, spaces, hyphens, apostrophes, commas, periods
        if not (char.isalpha() or char.isdigit() or char in ' -\',.'):
            invalid_chars.add(char)
    
    if invalid_chars:
        return False, ERROR_INVALID_CHARS.format(chars=', '.join(invalid_chars))
    
    # Check if it's only special characters or numbers
    if not any(char.isalpha() for char in city):
        return False, ERROR_NO_LETTERS
    
    # Check if purely numeric
    if city.replace(' ', '').replace('-', '').replace("'", '').isdigit():
        return False, ERROR_PURELY_NUMERIC
    
    # Warn if mostly special characters (less than 50% letters)
    letter_count = sum(1 for char in city if char.isalpha())
    if letter_count < len(city.strip()) * 0.5:
        return False, ERROR_TOO_MANY_SPECIAL
    
    return True, None


def get_coordinates(city: str) -> Tuple[Optional[float], Optional[float]]:
    """Fetch city coordinates from OpenWeatherMap API.
    
    Args:
        city: City name to search for
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if city not found
    """
    try:
        logger.info(f"Fetching coordinates for city: {city}")
        params = {
            "q": city,
            "appid": API_KEY
        }
        response = requests.get(WEATHER_URL, params=params, timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            # Validate response structure
            coord = validate_coordinates_response(data)
            lat, lon = coord["lat"], coord["lon"]
            logger.info(f"Coordinates found for {city}: {lat}, {lon}")
            return lat, lon
        elif response.status_code == 404:
            logger.warning(f"City not found: {city}")
            return None, None
        else:
            logger.warning(
                f"Unexpected status code {response.status_code} "
                f"when fetching coordinates for {city}"
            )
            return None, None
    except requests.Timeout:
        logger.error(f"Timeout while fetching coordinates for {city}")
        raise Exception(f"Network timeout while fetching coordinates")
    except requests.ConnectionError as e:
        logger.error(f"Connection error while fetching coordinates for {city}: {str(e)}")
        raise Exception(f"Connection error while fetching coordinates")
    except requests.RequestException as e:
        logger.error(f"Network error while fetching coordinates for {city}: {str(e)}")
        raise Exception(f"Network error while fetching coordinates: {str(e)}")
    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Invalid response format from coordinates API: {str(e)}")
        raise Exception(f"Invalid response format while fetching coordinates")


def get_air_quality(lat: float, lon: float) -> str:
    """Fetch air quality index from OpenWeatherMap API.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        Air quality string or error message
    """
    try:
        logger.info(f"Fetching air quality for coordinates: {lat}, {lon}")
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY
        }
        response = requests.get(AIR_QUALITY_URL, params=params, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Validate response structure
                validated_data = validate_air_quality_response(data)
                aqi_value = validated_data["list"][0]["main"]["aqi"]
                # Use enum to get AQI level
                try:
                    aqi_level = AQILevel.from_value(aqi_value)
                    result = f"{aqi_value} ({aqi_level.description})"
                except ValueError:
                    # Fallback for unexpected AQI values
                    result = f"{aqi_value} (Unknown)"
                logger.info(f"Air quality fetched successfully: {result}")
                return result
            except (KeyError, TypeError, ValueError) as e:
                logger.error(f"Failed to parse air quality response: {str(e)}", exc_info=True)
                return MSG_UNAVAILABLE_INVALID_RESPONSE
        elif response.status_code == 401:
            logger.error("Air Quality API Error: Invalid API Key")
            return MSG_UNAVAILABLE_API_KEY
        elif response.status_code == 429:
            logger.warning("Air Quality API: Rate limit exceeded")
            return MSG_UNAVAILABLE_RATE_LIMITED
        else:
            logger.warning(f"Air Quality API returned status code {response.status_code}")
            return MSG_UNAVAILABLE_API_ERROR
    except requests.Timeout:
        logger.error("Air Quality API request timed out after 5 seconds")
        return MSG_UNAVAILABLE_TIMEOUT
    except requests.ConnectionError as e:
        logger.error(f"Air Quality API connection error: {str(e)}")
        return MSG_UNAVAILABLE_NO_CONNECTION
    except requests.RequestException as e:
        logger.error(f"Air Quality API request error: {str(e)}", exc_info=True)
        return MSG_UNAVAILABLE_NETWORK_ERROR


def get_current_weather(city: str, units: str) -> Optional[Tuple[float, str, int, float, str]]:
    """Fetch current weather data from OpenWeatherMap API.
    
    Args:
        city: City name
        units: Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit)
        
    Returns:
        Tuple of (temperature, condition, humidity, wind_speed, icon_code) or None if failed
    """
    try:
        logger.info(f"Fetching current weather for {city} (units: {units})")
        params = {
            "q": city,
            "appid": API_KEY,
            "units": units
        }
        response = requests.get(WEATHER_URL, params=params, timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            # Validate response structure
            validated_data = validate_current_weather_response(data)
            temp = validated_data["main"]["temp"]
            condition = validated_data["weather"][0]["description"].title()
            humidity = validated_data["main"]["humidity"]
            wind_speed = validated_data["wind"]["speed"]
            icon_code = validated_data["weather"][0]["icon"]
            logger.info(f"Current weather fetched for {city}: {condition}, {temp}°")
            return temp, condition, humidity, wind_speed, icon_code
        return None
    except requests.Timeout:
        logger.error(f"Timeout while fetching weather for {city}")
        raise Exception(f"Network timeout while fetching weather")
    except requests.ConnectionError as e:
        logger.error(f"Connection error while fetching weather for {city}: {str(e)}")
        raise Exception(f"Connection error while fetching weather")
    except requests.RequestException as e:
        logger.error(f"Network error while fetching weather for {city}: {str(e)}")
        raise Exception(f"Network error while fetching weather: {str(e)}")
    except (KeyError, TypeError, ValueError) as e:
        logger.error(f"Invalid response format from weather API: {str(e)}")
        raise Exception(f"Invalid weather response format")


def get_5_day_forecast(city: str, units: str) -> str:
    """Fetch 5-day forecast from OpenWeatherMap API.
    
    Args:
        city: City name
        units: Temperature units ('metric' for Celsius, 'imperial' for Fahrenheit)
        
    Returns:
        Formatted forecast string or error message
    """
    try:
        logger.info(f"Fetching 5-day forecast for {city}")
        params = {
            "q": city,
            "appid": API_KEY,
            "units": units
        }
        response = requests.get(FORECAST_URL, params=params, timeout=API_TIMEOUT)
        forecast_text = "\n"
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Validate response structure
                forecast_list = validate_forecast_response(data)
                    
                temp_unit = TEMP_UNIT_METRIC if units == UNITS_METRIC else TEMP_UNIT_IMPERIAL
                for i in range(
                    0,
                    min(INTERVALS_PER_FORECAST, len(forecast_list)),
                    HOURS_PER_INTERVAL
                ):
                    try:
                        entry = forecast_list[i]
                        date = entry["dt_txt"].split(" ")[0]
                        temp = entry["main"]["temp"]
                        condition = entry["weather"][0]["description"].title()
                        forecast_text += f"{date}: {condition}, {temp} {temp_unit}\n"
                    except (KeyError, IndexError, TypeError, ValueError) as e:
                        logger.error(f"Error parsing forecast entry {i}: {str(e)}")
                        continue
                
                if forecast_text.strip() == "":
                    logger.warning(f"Could not parse any forecast data for {city}")
                    return MSG_FORECAST_UNAVAILABLE_PARSE_ERROR
                    
                logger.info(f"5-day forecast fetched successfully for {city}")
                return forecast_text
            except (ValueError, KeyError, TypeError) as e:
                logger.error(f"Failed to parse forecast response: {str(e)}", exc_info=True)
                return MSG_FORECAST_UNAVAILABLE_INVALID_RESPONSE
        elif response.status_code == 401:
            logger.error("Forecast API Error: Invalid API Key")
            return MSG_FORECAST_UNAVAILABLE_API_KEY
        elif response.status_code == 429:
            logger.warning("Forecast API: Rate limit exceeded")
            return MSG_FORECAST_UNAVAILABLE_RATE_LIMITED
        else:
            logger.warning(f"Forecast API returned status code {response.status_code}")
            return MSG_FORECAST_UNAVAILABLE_API_ERROR
    except requests.Timeout:
        logger.error(f"Forecast API request timed out after 5 seconds for {city}")
        return MSG_FORECAST_UNAVAILABLE_TIMEOUT
    except requests.ConnectionError as e:
        logger.error(f"Forecast API connection error: {str(e)}")
        return MSG_FORECAST_UNAVAILABLE_NO_CONNECTION
    except requests.RequestException as e:
        logger.error(f"Forecast API request error: {str(e)}", exc_info=True)
        return MSG_FORECAST_UNAVAILABLE_NETWORK_ERROR
