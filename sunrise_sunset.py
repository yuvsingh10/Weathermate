"""Sunrise/Sunset and UV index information."""

import requests
from typing import Optional, Tuple, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SunriseSunsetInfo:
    """Get sunrise, sunset, and UV index information."""
    
    SUNRISE_SUNSET_API = "https://api.sunrise-sunset.org/json"
    
    @staticmethod
    def get_sunrise_sunset(lat: float, lon: float) -> Optional[Dict[str, str]]:
        """Get sunrise and sunset times.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with sunrise, sunset, and daylight info
        """
        try:
            params = {"lat": lat, "lng": lon, "formatted": 0}
            response = requests.get(
                SunriseSunsetInfo.SUNRISE_SUNSET_API,
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "OK":
                    results = data["results"]
                    
                    sunrise_str = results["sunrise"]
                    sunset_str = results["sunset"]
                    
                    # Parse times
                    sunrise = datetime.fromisoformat(
                        sunrise_str.replace('Z', '+00:00')
                    )
                    sunset = datetime.fromisoformat(
                        sunset_str.replace('Z', '+00:00')
                    )
                    
                    sunrise_local = sunrise.strftime("%H:%M:%S")
                    sunset_local = sunset.strftime("%H:%M:%S")
                    
                    # Calculate daylight hours
                    daylight_seconds = (sunset - sunrise).total_seconds()
                    daylight_hours = int(daylight_seconds // 3600)
                    daylight_minutes = int((daylight_seconds % 3600) // 60)
                    
                    logger.info(
                        f"Sunrise/Sunset retrieved: {sunrise_local} / "
                        f"{sunset_local}"
                    )
                    
                    return {
                        "sunrise": sunrise_local,
                        "sunset": sunset_local,
                        "daylight_hours": str(daylight_hours),
                        "daylight_minutes": str(daylight_minutes)
                    }
        except requests.Timeout:
            logger.warning("Sunrise/Sunset API timeout")
        except requests.RequestException as e:
            logger.warning(f"Error fetching sunrise/sunset: {str(e)}")
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing sunrise/sunset data: {str(e)}")
        
        return None
    
    @staticmethod
    def estimate_uv_index(condition: str, time_str: str) -> Tuple[int, str]:
        """Estimate UV index based on condition and time.
        
        Args:
            condition: Weather condition
            time_str: Time in HH:MM:SS format
            
        Returns:
            Tuple of (uv_index: int, risk_level: str)
        """
        # Parse time
        try:
            hour = int(time_str.split(":")[0])
        except (ValueError, IndexError):
            hour = 12
        
        # Base UV index on condition
        clear_uv = 9 if 9 <= hour <= 15 else 4  # Peak hours
        cloudy_uv = 3
        rainy_uv = 1
        
        if "clear" in condition.lower() or "sunny" in condition.lower():
            uv = clear_uv
        elif "cloud" in condition.lower() or "overcast" in condition.lower():
            uv = cloudy_uv
        elif "rain" in condition.lower():
            uv = rainy_uv
        else:
            uv = 5
        
        # Apply time-of-day factor
        if hour < 9 or hour > 17:
            uv = max(1, int(uv * 0.3))
        elif 9 <= hour <= 11 or 14 <= hour <= 17:
            uv = int(uv * 0.7)
        
        # Get risk level
        risk_levels = {
            0: "None",
            1: "Low",
            2: "Low",
            3: "Moderate",
            4: "Moderate",
            5: "High",
            6: "High",
            7: "Very High",
            8: "Very High",
            9: "Extreme",
            10: "Extreme"
        }
        
        risk = risk_levels.get(min(uv, 10), "Unknown")
        
        return uv, risk
    
    @staticmethod
    def get_sun_info_text(
        lat: float,
        lon: float,
        condition: str
    ) -> str:
        """Get formatted sun and UV information.
        
        Args:
            lat: Latitude
            lon: Longitude
            condition: Weather condition
            
        Returns:
            Formatted sun info text
        """
        sun_data = SunriseSunsetInfo.get_sunrise_sunset(lat, lon)
        
        if not sun_data:
            return "☀️ Sun info: Unable to retrieve"
        
        sunrise = sun_data["sunrise"]
        sunset = sun_data["sunset"]
        daylight_h = sun_data["daylight_hours"]
        daylight_m = sun_data["daylight_minutes"]
        
        uv_index, uv_risk = SunriseSunsetInfo.estimate_uv_index(
            condition, sunrise
        )
        
        text = (
            f"☀️ SUNRISE/SUNSET & UV INFO\n"
            f"{'='*40}\n"
            f"🌅 Sunrise: {sunrise}\n"
            f"🌅 Sunset:  {sunset}\n"
            f"💡 Daylight: {daylight_h}h {daylight_m}m\n\n"
            f"☀️ UV Index: {uv_index}/10\n"
            f"⚠️ Risk Level: {uv_risk}\n\n"
        )
        
        if uv_index <= 2:
            text += "✅ Low risk - sunscreen optional\n"
        elif uv_index <= 5:
            text += "🟡 Moderate risk - wear SPF 30+ sunscreen\n"
        elif uv_index <= 7:
            text += "🔴 High risk - wear SPF 50+ sunscreen, limit time\n"
        else:
            text += "🚨 Very high risk - stay in shade during peak hours\n"
        
        return text
