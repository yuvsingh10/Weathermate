"""Settings and preferences management (in-memory, not persisted)."""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class Settings:
    """Manage application preferences and settings (session-only)."""
    
    DEFAULT_SETTINGS = {
        "theme": "dark",  # dark or light
        "temperature_unit": "C",  # C or F
        "auto_refresh": 30,  # minutes
        "font_size": "medium",  # small, medium, large
        "notifications": True,
        "weather_alerts": True,
        "store_history": True,
        "default_city": "London"
    }
    
    def __init__(self):
        """Initialize settings with defaults."""
        self.settings: Dict[str, Any] = Settings.DEFAULT_SETTINGS.copy()
        logger.info("Settings initialized (in-memory)")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        logger.info(f"Setting '{key}' changed to '{value}'")
    
    def set_theme(self, theme: str) -> None:
        """Set the application theme.
        
        Args:
            theme: 'dark' or 'light'
        """
        if theme in ["dark", "light"]:
            self.set("theme", theme)
    
    def get_theme(self) -> str:
        """Get current theme.
        
        Returns:
            Current theme ('dark' or 'light')
        """
        return self.get("theme", "dark")
    
    def set_temperature_unit(self, unit: str) -> None:
        """Set temperature unit.
        
        Args:
            unit: 'C' for Celsius, 'F' for Fahrenheit
        """
        if unit in ["C", "F"]:
            self.set("temperature_unit", unit)
    
    def get_temperature_unit(self) -> str:
        """Get temperature unit.
        
        Returns:
            'C' or 'F'
        """
        return self.get("temperature_unit", "C")
    
    def set_auto_refresh(self, minutes: int) -> None:
        """Set auto-refresh interval.
        
        Args:
            minutes: Refresh interval in minutes
        """
        if 1 <= minutes <= 60:
            self.set("auto_refresh", minutes)
    
    def get_auto_refresh(self) -> int:
        """Get auto-refresh interval in minutes.
        
        Returns:
            Refresh interval in minutes
        """
        return self.get("auto_refresh", 30)
    
    def set_font_size(self, size: str) -> None:
        """Set font size.
        
        Args:
            size: 'small', 'medium', or 'large'
        """
        if size in ["small", "medium", "large"]:
            self.set("font_size", size)
    
    def get_font_size(self) -> str:
        """Get font size.
        
        Returns:
            Font size: 'small', 'medium', or 'large'
        """
        return self.get("font_size", "medium")
    
    def get_font_size_value(self) -> int:
        """Get numeric font size for rendering.
        
        Returns:
            Font size in points
        """
        sizes = {"small": 9, "medium": 11, "large": 13}
        return sizes.get(self.get_font_size(), 11)
    
    def toggle_notifications(self) -> bool:
        """Toggle notifications on/off.
        
        Returns:
            New notification state
        """
        current = self.get("notifications", True)
        self.set("notifications", not current)
        return not current
    
    def are_notifications_enabled(self) -> bool:
        """Check if notifications are enabled.
        
        Returns:
            Notification state
        """
        return self.get("notifications", True)
    
    def toggle_weather_alerts(self) -> bool:
        """Toggle weather alerts on/off.
        
        Returns:
            New alert state
        """
        current = self.get("weather_alerts", True)
        self.set("weather_alerts", not current)
        return not current
    
    def are_weather_alerts_enabled(self) -> bool:
        """Check if weather alerts are enabled.
        
        Returns:
            Alert state
        """
        return self.get("weather_alerts", True)
    
    def set_default_city(self, city: str) -> None:
        """Set default city.
        
        Args:
            city: City name
        """
        self.set("default_city", city)
    
    def get_default_city(self) -> str:
        """Get default city.
        
        Returns:
            Default city name
        """
        return self.get("default_city", "London")
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self.settings = Settings.DEFAULT_SETTINGS.copy()
        logger.info("Settings reset to defaults")
