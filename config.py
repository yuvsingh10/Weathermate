"""Configuration and constants for Weather Mate application."""

import os
import logging
from enum import Enum
from dotenv import load_dotenv
import tkinter as tk
from tkinter import font as tkFont

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not API_KEY:
    raise ValueError(
        "OPENWEATHER_API_KEY not found in environment variables. "
        "Please create a .env file with your API key."
    )

# ==================== API Configuration ====================

WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
ICON_URL = "http://openweathermap.org/img/wn/{}@2x.png"
API_TIMEOUT = 5  # seconds

# ==================== Forecast Configuration ====================

FORECAST_DAYS = 5
INTERVALS_PER_FORECAST = 40  # 5 days × 8 intervals (3-hourly data)
HOURS_PER_INTERVAL = 8  # OpenWeatherMap provides 3-hourly data (24/3 = 8 per day)

# ==================== Image Configuration ====================

ICON_SIZE = 80  # pixels

# ==================== Window Configuration ====================

MIN_WINDOW_WIDTH = 470
MIN_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_WIDTH = 700
DEFAULT_WINDOW_HEIGHT = 750

# ==================== Font Configuration ====================

FONT_HEADER_SIZE = 24  # Main title
FONT_LABEL_SIZE = 13   # Input labels
FONT_SMALL_SIZE = 11   # Radio buttons
FONT_RESULT_SIZE = 12  # Result text

# ==================== System-Independent Font Setup ====================

def get_default_fonts() -> dict:
    """Get system-independent fonts with fallbacks.
    
    Returns a dictionary of font objects that work across Windows, Mac, and Linux.
    Each font falls back to alternatives if primary font is not available.
    """
    # Fonts available on most systems (listed in order of preference)
    header_fonts = ["Arial", "Helvetica", "DejaVu Sans"]
    label_fonts = ["Arial", "Helvetica", "DejaVu Sans"]
    small_fonts = ["Arial", "Helvetica", "DejaVu Sans"]
    result_fonts = ["Arial", "Helvetica", "DejaVu Sans", "Courier"]
    
    return {
        "header": tkFont.Font(family=header_fonts, size=FONT_HEADER_SIZE, weight="bold"),
        "label": tkFont.Font(family=label_fonts, size=FONT_LABEL_SIZE),
        "label_bold": tkFont.Font(family=label_fonts, size=FONT_SMALL_SIZE, weight="bold"),
        "small": tkFont.Font(family=small_fonts, size=FONT_SMALL_SIZE),
        "result": tkFont.Font(family=result_fonts, size=FONT_RESULT_SIZE),
    }

# Initialize fonts (will be populated when GUI is created)
FONTS = {}

# ==================== Color Configuration ====================

BG_COLOR_PRIMARY = "#e3f2fd"      # Light blue background
BG_COLOR_SECONDARY = "#bbdefb"    # Darker blue for result box
COLOR_HEADER = "#1976d2"          # Dark blue for headers/buttons
COLOR_BUTTON_HOVER = "#1565c0"    # Darker blue for hover
COLOR_TEXT_PRIMARY = "#0d47a1"    # Dark blue for result text

# ==================== Layout Configuration ====================

PADDING_HEADER_Y = (18, 8)
PADDING_ENTRY_Y = 8
PADDING_UNIT_Y = 5
PADDING_BUTTON_Y = 14
PADDING_ICON_Y = 5
PADDING_FRAME_Y = 10
PADDING_FRAME_X = 16
PADDING_LABEL_X = (0, 8)
PADDING_RESULT_X = 10
PADDING_RESULT_Y = 12
ENTRY_WIDTH = 22

# ==================== Text Configuration ====================

MIN_WRAPLENGTH = 300  # Minimum text wrap width
DEFAULT_WRAPLENGTH = 600  # Default text wrap width
MAX_CITY_NAME_LENGTH = 100
MIN_CITY_NAME_LENGTH = 2
FRAME_PADDING_WIDTH = 20  # Width padding to subtract from frame width

# ==================== String Constants ====================

# Air Quality Index Levels
class AQILevel(Enum):
    """Air Quality Index levels with numeric values and descriptions.
    
    Values are tuples of (numeric_value, description)
    """
    GOOD = (1, "Good")
    FAIR = (2, "Fair")
    MODERATE = (3, "Moderate")
    POOR = (4, "Poor")
    VERY_POOR = (5, "Very Poor")
    
    @property
    def value_num(self) -> int:
        """Get the numeric AQI value."""
        return self.value[0]
    
    @property
    def description(self) -> str:
        """Get the description for this AQI level."""
        return self.value[1]
    
    @classmethod
    def from_value(cls, value: int) -> 'AQILevel':
        """Get AQI level by numeric value.
        
        Args:
            value: Numeric AQI value (1-5)
            
        Returns:
            Corresponding AQILevel enum
            
        Raises:
            ValueError if value is not 1-5
        """
        for level in cls:
            if level.value_num == value:
                return level
        raise ValueError(f"Invalid AQI value: {value}. Must be 1-5.")


# Legacy dictionary for backwards compatibility (maps to enum)
AQI_LEVELS = {
    1: AQILevel.GOOD.description,
    2: AQILevel.FAIR.description,
    3: AQILevel.MODERATE.description,
    4: AQILevel.POOR.description,
    5: AQILevel.VERY_POOR.description
}

# UI Messages
TITLE_MAIN = "Weather Mate"
LABEL_CITY = "Enter City Name:"
LABEL_UNITS = "Units:"
UNIT_CELSIUS = "Celsius"
UNIT_FAHRENHEIT = "Fahrenheit"
BUTTON_GET_WEATHER = "Get Weather"

# Temperature Units
UNITS_METRIC = "metric"
UNITS_IMPERIAL = "imperial"
TEMP_UNIT_METRIC = "Celsius"
TEMP_UNIT_IMPERIAL = "Fahrenheit"
WIND_UNIT_METRIC = "meters/second"
WIND_UNIT_IMPERIAL = "miles/hour"

# API Status Codes
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_UNAUTHORIZED = 401
HTTP_RATE_LIMITED = 429

# Error Messages
ERROR_EMPTY_CITY = "City name cannot be empty."
ERROR_CITY_TOO_SHORT = f"City name must be at least {MIN_CITY_NAME_LENGTH} characters long."
ERROR_CITY_TOO_LONG = f"City name is too long (max {MAX_CITY_NAME_LENGTH} characters)."
ERROR_INVALID_CHARS = (
    "Invalid characters detected: {chars}. "
    "Only letters, numbers, spaces, hyphens, apostrophes, and commas are allowed."
)
ERROR_NO_LETTERS = "City name must contain at least one letter."
ERROR_PURELY_NUMERIC = "City name cannot be purely numeric."
ERROR_TOO_MANY_SPECIAL = "City name contains too many special characters."
ERROR_NETWORK_SERVICE = "Could not connect to weather service."
ERROR_FETCH_WEATHER = "Could not fetch weather data."
ERROR_CITY_NOT_FOUND = "City '{}' not found. Please check the spelling."
ERROR_UNEXPECTED = "An unexpected error occurred."
ERROR_NETWORK_TIMEOUT = "Network timeout"
ERROR_CONNECTION = "Connection error"
ERROR_NETWORK_GENERAL = "Network error"
ERROR_INVALID_RESPONSE = "Invalid response format"

# Message Box Titles
TITLE_INPUT_ERROR = "Input Error"
TITLE_NETWORK_ERROR = "Network Error"
TITLE_ERROR = "Error"
TITLE_UNEXPECTED_ERROR = "Unexpected Error"

# Success Messages
MSG_WEATHER_DISPLAYED = "Weather displayed successfully for {}"
MSG_ICON_LOADED = "Weather icon loaded successfully"
MSG_NO_WEATHER_DATA = "Could not retrieve weather data."

# Availability Messages
MSG_UNAVAILABLE = "Unavailable"
MSG_UNAVAILABLE_TIMEOUT = "Unavailable (Timeout)"
MSG_UNAVAILABLE_NO_CONNECTION = "Unavailable (No Connection)"
MSG_UNAVAILABLE_NETWORK_ERROR = "Unavailable (Network Error)"
MSG_UNAVAILABLE_INVALID_RESPONSE = "Unavailable (Invalid Response)"
MSG_UNAVAILABLE_API_KEY = "Unavailable (API Key Issue)"
MSG_UNAVAILABLE_RATE_LIMITED = "Unavailable (Rate Limited)"
MSG_UNAVAILABLE_API_ERROR = "Unavailable (API Error)"
MSG_FORECAST_UNAVAILABLE = "Forecast unavailable."
MSG_FORECAST_UNAVAILABLE_TIMEOUT = "Forecast unavailable (Timeout)"
MSG_FORECAST_UNAVAILABLE_NO_CONNECTION = "Forecast unavailable (No Connection)"
MSG_FORECAST_UNAVAILABLE_NETWORK_ERROR = "Forecast unavailable (Network Error)"
MSG_FORECAST_UNAVAILABLE_INVALID_RESPONSE = "Forecast unavailable (Invalid Response)"
MSG_FORECAST_UNAVAILABLE_API_KEY = "Forecast unavailable (API Key Issue)"
MSG_FORECAST_UNAVAILABLE_RATE_LIMITED = "Forecast unavailable (Rate Limited)"
MSG_FORECAST_UNAVAILABLE_API_ERROR = "Forecast unavailable (API Error)"
MSG_FORECAST_UNAVAILABLE_NO_DATA = "Forecast unavailable (No data)"
MSG_FORECAST_UNAVAILABLE_PARSE_ERROR = "Forecast unavailable (Parse Error)"

# Weather Display Format
WEATHER_DISPLAY_FORMAT = (
    "Current Weather for {city}:\n"
    "Condition: {condition}\n"
    "Temperature: {temp} {temp_unit}\n"
    "Humidity: {humidity}%\n"
    "Wind Speed: {wind_speed} {wind_unit}\n"
    "Air Quality Index: {air_quality}\n\n"
    "5-Day Forecast:{forecast}"
)

# ==================== Logging Configuration ====================

LOG_FILE = "weathermate.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also print to console
    ]
)
logger = logging.getLogger(__name__)
