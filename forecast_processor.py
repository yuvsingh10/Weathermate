"""Process and format forecast data for interactive display."""

from typing import List, Dict, Tuple
from datetime import datetime


class ForecastDay:
    """Represents a day's forecast with hourly details."""
    
    def __init__(self, date: str):
        """Initialize a forecast day.
        
        Args:
            date: Date string (YYYY-MM-DD format)
        """
        self.date = date
        self.hourly_data: List[Dict] = []
        self.min_temp = float('inf')
        self.max_temp = float('-inf')
        self.conditions: List[str] = []
    
    def add_hourly(
        self,
        time: str,
        temp: float,
        condition: str,
        humidity: int,
        wind: float
    ) -> None:
        """Add hourly forecast data.
        
        Args:
            time: Time string (HH:MM format)
            temp: Temperature
            condition: Weather condition
            humidity: Humidity percentage
            wind: Wind speed
        """
        self.hourly_data.append({
            "time": time,
            "temp": temp,
            "condition": condition,
            "humidity": humidity,
            "wind": wind
        })
        
        # Update min/max
        self.min_temp = min(self.min_temp, temp)
        self.max_temp = max(self.max_temp, temp)
        
        # Track conditions
        if condition not in self.conditions:
            self.conditions.append(condition)
    
    def get_summary(self) -> str:
        """Get a one-line summary of the day.
        
        Returns:
            Summary string with date, temp range, and conditions
        """
        if self.min_temp == float('inf'):
            return f"{self.date}: No data"
        
        conditions_str = ", ".join(set(self.conditions))
        return (
            f"{self.date}: {self.min_temp}°-{self.max_temp}° | "
            f"{conditions_str}"
        )
    
    def get_details(self) -> str:
        """Get detailed hourly breakdown.
        
        Returns:
            Formatted string with all hourly details
        """
        if not self.hourly_data:
            return f"No hourly data for {self.date}"
        
        details = f"\n{'='*50}\n📅 {self.date}\n{'='*50}\n"
        
        for hour in self.hourly_data:
            details += (
                f"⏰ {hour['time']} | "
                f"🌡️ {hour['temp']}° | "
                f"💧 {hour['humidity']}% | "
                f"💨 {hour['wind']:.1f}\n"
                f"   Condition: {hour['condition']}\n\n"
            )
        
        return details


def process_forecast_data(
    forecast_list: List[Dict],
    units: str
) -> List[ForecastDay]:
    """Process raw forecast data into daily summaries.
    
    Args:
        forecast_list: List of forecast entries from API
        units: Unit system ('metric' or 'imperial')
        
    Returns:
        List of ForecastDay objects organized by date
    """
    forecast_days: Dict[str, ForecastDay] = {}
    
    for entry in forecast_list:
        try:
            # Extract date and time
            dt_txt = entry.get("dt_txt", "")
            date = dt_txt.split(" ")[0]  # YYYY-MM-DD
            time = dt_txt.split(" ")[1]  # HH:MM:SS
            time = time[:5]  # Keep only HH:MM
            
            # Extract temp and condition
            main = entry.get("main", {})
            weather = entry.get("weather", [{}])[0]
            wind = entry.get("wind", {})
            
            temp = main.get("temp", 0)
            condition = weather.get("description", "Unknown")
            humidity = main.get("humidity", 0)
            wind_speed = wind.get("speed", 0)
            
            # Create day if not exists
            if date not in forecast_days:
                forecast_days[date] = ForecastDay(date)
            
            # Add hourly data
            forecast_days[date].add_hourly(
                time, temp, condition.title(), humidity, wind_speed
            )
        
        except (KeyError, IndexError, ValueError):
            # Skip malformed entries
            continue
    
    # Return ordered by date
    return sorted(
        forecast_days.values(),
        key=lambda x: x.date
    )


def create_forecast_view(
    forecast_days: List[ForecastDay],
    expanded_date: str = None
) -> str:
    """Create formatted forecast view.
    
    Args:
        forecast_days: List of ForecastDay objects
        expanded_date: Date to show detailed view for (None for summary)
        
    Returns:
        Formatted forecast string
    """
    if not forecast_days:
        return "No forecast data available"
    
    if expanded_date:
        # Find and show details for specific date
        for day in forecast_days:
            if day.date == expanded_date:
                return day.get_details()
        return f"No data for {expanded_date}"
    
    # Show summary for all days
    forecast_text = "\n📊 5-DAY FORECAST SUMMARY:\n"
    forecast_text += "Click on a day to see hourly details\n\n"
    
    for i, day in enumerate(forecast_days, 1):
        summary = day.get_summary()
        forecast_text += f"[Day {i}] {summary}\n"
    
    return forecast_text
