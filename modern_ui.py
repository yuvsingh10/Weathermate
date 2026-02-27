"""Modern GUI components using CustomTkinter for WeatherMate."""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import requests
import logging
from typing import Optional
from datetime import datetime
import config

from config import (
    TITLE_MAIN, LABEL_CITY, LABEL_UNITS, UNIT_CELSIUS, UNIT_FAHRENHEIT,
    BUTTON_GET_WEATHER,
    UNITS_METRIC, UNITS_IMPERIAL, TEMP_UNIT_METRIC, TEMP_UNIT_IMPERIAL,
    WIND_UNIT_METRIC, WIND_UNIT_IMPERIAL,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    FONT_HEADER_SIZE, FONT_LABEL_SIZE, FONT_SMALL_SIZE, FONT_RESULT_SIZE,
    BG_COLOR_PRIMARY, BG_COLOR_SECONDARY, COLOR_HEADER, COLOR_BUTTON_HOVER,
    COLOR_TEXT_PRIMARY,
    PADDING_HEADER_Y, PADDING_ENTRY_Y, PADDING_UNIT_Y, PADDING_BUTTON_Y,
    PADDING_ICON_Y,
    PADDING_FRAME_Y, PADDING_FRAME_X, PADDING_LABEL_X, PADDING_RESULT_X,
    PADDING_RESULT_Y,
    ENTRY_WIDTH, MIN_WRAPLENGTH, DEFAULT_WRAPLENGTH, FRAME_PADDING_WIDTH,
    ICON_SIZE, API_TIMEOUT,
    ICON_URL, WEATHER_DISPLAY_FORMAT,
    TITLE_INPUT_ERROR, TITLE_NETWORK_ERROR, TITLE_ERROR,
    TITLE_UNEXPECTED_ERROR,
    ERROR_NETWORK_SERVICE, ERROR_FETCH_WEATHER, ERROR_CITY_NOT_FOUND,
    ERROR_UNEXPECTED,
    MSG_NO_WEATHER_DATA, MSG_ICON_LOADED,
    get_default_fonts, FONTS, get_weather_emoji,
    logger
)
from api import (
    validate_city_input, get_coordinates, get_air_quality,
    get_current_weather, get_5_day_forecast
)
from history import SearchHistory
from forecast_processor import process_forecast_data, create_forecast_view
from weather_comparison import WeatherComparison
from weather_history import WeatherHistory
from air_quality_details import AirQualityDetails
from sunrise_sunset import SunriseSunsetInfo
from settings import Settings
from settings_dialog import SettingsDialog


# Set modern theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Global GUI variables
root: ctk.CTk
city_entry: ctk.CTkEntry
unit_var: ctk.StringVar
result_label: ctk.CTkLabel
icon_label: ctk.CTkLabel
results_frame: ctk.CTkFrame
loading_label: ctk.CTkLabel
get_weather_button: ctk.CTkButton
favorite_button: ctk.CTkButton
search_history: SearchHistory
current_city: str = ""
last_weather_data: Optional[dict] = None
clock_label: ctk.CTkLabel
last_updated_label: ctk.CTkLabel
forecast_data: list = []
forecast_label: ctk.CTkLabel
forecast_button_frame: ctk.CTkFrame
expanded_forecast_date: Optional[str] = None
# New feature modules
weather_comparison: WeatherComparison
weather_history_tracker: WeatherHistory
app_settings: Settings


def show_comparison_dialog() -> None:
    """Show weather comparison dialog for multiple cities."""
    if not weather_comparison.cities_data:
        messagebox.showinfo(
            "Weather Comparison",
            "Add cities to compare.\n\nUse the comparison window to add "
            "up to 3 cities and compare their weather side-by-side."
        )
        return
    
    comparison_text = weather_comparison.get_comparison_text()
    
    # Create dialog
    dialog = ctk.CTkToplevel(root)
    dialog.title("🌍 Weather Comparison")
    dialog.geometry("500x400")
    dialog.transient(root)
    
    # Text display
    text_widget = ctk.CTkTextbox(dialog, font=("Segoe UI", 11))
    text_widget.pack(fill="both", expand=True, padx=10, pady=10)
    text_widget.insert("0.0", comparison_text)
    text_widget.configure(state="disabled")


def add_city_to_comparison() -> None:
    """Add current city to comparison."""
    if not current_city:
        messagebox.showwarning(
            "No City",
            "Search for a city first before adding to comparison."
        )
        return
    
    success = weather_comparison.add_city(current_city)
    if success:
        count = len(weather_comparison.cities_data)
        messagebox.showinfo(
            "Added",
            f"{current_city} added to comparison. ({count}/3)"
        )
    else:
        messagebox.showwarning(
            "Comparison Full",
            "Maximum 3 cities to compare. Remove one first."
        )


def show_air_quality_dialog() -> None:
    """Show detailed air quality information."""
    if not last_weather_data:
        messagebox.showinfo(
            "Air Quality",
            "Search for a city first to see air quality details."
        )
        return
    
    air_quality_str = last_weather_data["air_quality"]
    
    # Extract AQI level from string
    try:
        aqi_level = int(air_quality_str.split()[-1])
    except (ValueError, IndexError):
        aqi_level = 2
    
    report = AirQualityDetails.get_detailed_report(aqi_level)
    
    # Create dialog
    dialog = ctk.CTkToplevel(root)
    dialog.title("🌫️ Air Quality Details")
    dialog.geometry("550x600")
    dialog.transient(root)
    
    text_widget = ctk.CTkTextbox(dialog, font=("Segoe UI", 10))
    text_widget.pack(fill="both", expand=True, padx=10, pady=10)
    text_widget.insert("0.0", report)
    text_widget.configure(state="disabled")


def show_sunrise_sunset_info() -> None:
    """Show sunrise, sunset, and UV information."""
    if not last_weather_data:
        messagebox.showinfo(
            "Sun Info",
            "Search for a city first to see sunrise/sunset times."
        )
        return
    
    lat = last_weather_data.get("lat")
    lon = last_weather_data.get("lon")
    condition = last_weather_data.get("condition", "Sunny")
    
    if not lat or not lon:
        messagebox.showerror(
            "Error",
            "Location data not available."
        )
        return
    
    sun_text = SunriseSunsetInfo.get_sun_info_text(lat, lon, condition)
    
    # Create dialog
    dialog = ctk.CTkToplevel(root)
    dialog.title("☀️ Sunrise/Sunset & UV Index")
    dialog.geometry("450x350")
    dialog.transient(root)
    
    text_widget = ctk.CTkTextbox(dialog, font=("Segoe UI", 11))
    text_widget.pack(fill="both", expand=True, padx=10, pady=10)
    text_widget.insert("0.0", sun_text)
    text_widget.configure(state="disabled")


def show_forecast_dialog() -> None:
    """Show 5-day forecast in a dialog."""
    if not forecast_data:
        messagebox.showinfo(
            "Forecast",
            "Search for a city first to see the forecast."
        )
        return
    
    # Create dialog
    dialog = ctk.CTkToplevel(root)
    dialog.title("📅 5-Day Forecast")
    dialog.geometry("550x500")
    dialog.transient(root)
    
    # Create scrollable frame for forecast
    scroll_frame = ctk.CTkScrollableFrame(dialog)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Show summary view
    forecast_text = create_forecast_view(forecast_data, None)
    
    # Forecast summary label
    summary_label = ctk.CTkLabel(
        scroll_frame,
        text=forecast_text,
        font=("Segoe UI", 11),
        justify="left",
        wraplength=480
    )
    summary_label.pack(fill="x", pady=10)
    
    # Day selection buttons
    for day in forecast_data[:5]:
        btn = ctk.CTkButton(
            scroll_frame,
            text=f"📅 {day.date} - {day.get_summary()}",
            command=lambda d=day: show_day_details(scroll_frame, d),
            font=("Segoe UI", 10),
            fg_color="#1f6aa5",
            hover_color="#0d47a1",
            text_color="white",
            corner_radius=8
        )
        btn.pack(fill="x", pady=5)


def show_day_details(parent: ctk.CTkScrollableFrame, day) -> None:
    """Show detailed forecast for a specific day."""
    # Clear parent frame
    for widget in parent.winfo_children():
        widget.destroy()
    
    # Back button
    back_btn = ctk.CTkButton(
        parent,
        text="⬅️ Back to Summary",
        command=lambda: show_forecast_dialog(),
        font=("Segoe UI", 10),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        text_color="white",
        corner_radius=8
    )
    back_btn.pack(fill="x", pady=5)
    
    # Day details
    details = day.get_details()
    details_label = ctk.CTkLabel(
        parent,
        text=details,
        font=("Segoe UI", 10),
        justify="left",
        wraplength=480
    )
    details_label.pack(fill="x", pady=10)


def show_settings_dialog() -> None:
    """Open settings dialog."""
    settings_dialog = SettingsDialog(root, app_settings)
    root.wait_window(settings_dialog)


def show_weather_history_info() -> None:
    """Show weather history and trends."""
    if not current_city:
        messagebox.showinfo(
            "Weather History",
            "Search for a city first to see weather history."
        )
        return
    
    history = weather_history_tracker.get_history(current_city)
    temp_trend = weather_history_tracker.get_temperature_trend(current_city)
    
    if not history:
        messagebox.showinfo(
            "Weather History",
            f"No history available for {current_city}.\n\n"
            "History is recorded each time you search for weather."
        )
        return
    
    avg_temp = weather_history_tracker.get_avg_temperature(current_city)
    max_temp = weather_history_tracker.get_max_temperature(current_city)
    min_temp = weather_history_tracker.get_min_temperature(current_city)
    
    history_text = f"📊 WEATHER HISTORY: {current_city}\n"
    history_text += f"{'='*40}\n\n"
    history_text += f"Average Temp: {avg_temp:.1f}°\n"
    history_text += f"Max Temp: {max_temp:.1f}°\n"
    history_text += f"Min Temp: {min_temp:.1f}°\n\n"
    history_text += "Recent Records:\n"
    
    for record in reversed(history[-5:]):
        timestamp = record["timestamp"].split("T")[1][:5]
        temp = record["temp"]
        condition = record["condition"]
        history_text += f"  • {timestamp}: {temp}° ({condition})\n"
    
    messagebox.showinfo("Weather History", history_text)


def update_wraplength(event: Optional[object] = None) -> None:
    """Update text wraplength when window is resized."""
    available_width = results_frame.winfo_width() - FRAME_PADDING_WIDTH
    new_wraplength = max(MIN_WRAPLENGTH, available_width)
    result_label.configure(wraplength=new_wraplength)


def show_recent_searches() -> None:
    """Display recent cities in a dialog."""
    recent = search_history.get_recent()
    if not recent:
        messagebox.showinfo("Recent Searches", "No recent searches yet.")
        return
    
    recent_text = "\n".join([f"• {city}" for city in recent])
    messagebox.showinfo(
        "Recent Searches",
        f"Your recent searches:\n\n{recent_text}\n\n" +
        "Click on entry field and type to search."
    )


def toggle_favorite() -> None:
    """Toggle favorite status for current city."""
    if not current_city:
        messagebox.showwarning(
            "No City Selected",
            "Search for a city first to add it to favorites."
        )
        return
    
    if search_history.is_favorite(current_city):
        search_history.remove_favorite(current_city)
        favorite_button.configure(text="♡ Add to Favorites")
        messagebox.showinfo(
            "Removed",
            f"{current_city} removed from favorites."
        )
    else:
        search_history.add_favorite(current_city)
        favorite_button.configure(text="♥ Remove from Favorites")
        messagebox.showinfo(
            "Added",
            f"{current_city} added to favorites!"
        )


def display_weather_with_unit(
    city: str,
    units: str,
    temp: float,
    condition: str,
    humidity: int,
    wind_speed: float,
    air_quality: str,
    forecast: str,
    icon_code: str
) -> None:
    """Display weather information with formatted units."""
    temp_unit = TEMP_UNIT_METRIC if units == UNITS_METRIC else \
                TEMP_UNIT_IMPERIAL
    wind_unit = WIND_UNIT_METRIC if units == UNITS_METRIC else \
                WIND_UNIT_IMPERIAL
    
    emoji = get_weather_emoji(icon_code)
    alerts = generate_weather_alerts(temp, wind_speed, air_quality, units)
    
    result = (
        f"{emoji} {condition.upper()}\n"
        f"City: {city}\n"
        f"Temperature: {temp} {temp_unit}\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind_speed} {wind_unit}\n"
        f"Air Quality Index: {air_quality}\n"
    )
    
    if alerts:
        result += f"\n⚠️ ALERTS:\n{alerts}\n"
    
    result_label.configure(text=result)
    # Clear forecast initially
    forecast_label.configure(text="")


def generate_weather_alerts(
    temp: float,
    wind_speed: float,
    air_quality: str,
    units: str
) -> str:
    """Generate weather alert messages."""
    alerts = []
    
    # Temperature alerts
    if units == UNITS_METRIC:
        if temp >= 40:
            alerts.append("🔴 Extreme heat warning!")
        elif temp >= 35:
            alerts.append("🟠 High temperature alert")
        elif temp <= -20:
            alerts.append("🔴 Extreme cold warning!")
        elif temp <= -10:
            alerts.append("🟠 Low temperature alert")
    else:
        if temp >= 104:
            alerts.append("🔴 Extreme heat warning!")
        elif temp >= 95:
            alerts.append("🟠 High temperature alert")
        elif temp <= -4:
            alerts.append("🔴 Extreme cold warning!")
        elif temp <= 14:
            alerts.append("🟠 Low temperature alert")
    
    # Wind speed alerts
    if units == UNITS_METRIC:
        if wind_speed >= 15:
            alerts.append("💨 High wind advisory")
        elif wind_speed >= 25:
            alerts.append("🔴 Severe wind warning!")
    else:
        if wind_speed >= 25:
            alerts.append("💨 High wind advisory")
        elif wind_speed >= 40:
            alerts.append("🔴 Severe wind warning!")
    
    # Air quality alerts
    if "Very Poor" in air_quality or "5" in air_quality:
        alerts.append("🔴 Very poor air quality!")
    elif "Poor" in air_quality or "4" in air_quality:
        alerts.append("🟠 Poor air quality warning")
    elif "Moderate" in air_quality or "3" in air_quality:
        alerts.append("🟡 Moderate air quality")
    
    return "\n".join(alerts) if alerts else ""


def update_clock() -> None:
    """Update the clock display every second."""
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        clock_label.configure(text=f"🕐 {current_time}")
        clock_label.after(1000, update_clock)
    except:
        pass


def reset_forecast_view() -> None:
    """Reset the forecast to summary view."""
    global expanded_forecast_date
    expanded_forecast_date = None
    update_forecast_display()


def toggle_forecast_expansion(date: str) -> None:
    """Toggle the detailed view for a forecast date."""
    global expanded_forecast_date
    
    if expanded_forecast_date == date:
        expanded_forecast_date = None
    else:
        expanded_forecast_date = date
    
    update_forecast_display()


def update_forecast_display() -> None:
    """Update forecast label with current expansion state."""
    global forecast_data, expanded_forecast_date
    
    if not forecast_data:
        forecast_label.configure(text="⏳ No forecast data available")
        for widget in forecast_button_frame.winfo_children():
            widget.destroy()
        return
    
    forecast_text = create_forecast_view(
        forecast_data,
        expanded_forecast_date
    )
    
    forecast_label.configure(text=forecast_text)
    
    # Clear previous buttons
    for widget in forecast_button_frame.winfo_children():
        widget.destroy()
    
    # Create buttons for each day
    if not expanded_forecast_date:
        for day in forecast_data[:5]:
            btn = ctk.CTkButton(
                forecast_button_frame,
                text=f"📅 {day.date}",
                command=lambda d=day.date: toggle_forecast_expansion(d),
                font=(None, 10),
                fg_color="#1f6aa5",
                hover_color="#0d47a1",
                text_color="white",
                corner_radius=8
            )
            btn.pack(side="left", padx=3, pady=3)
    else:
        back_btn = ctk.CTkButton(
            forecast_button_frame,
            text="⬅️ Back to Summary",
            command=reset_forecast_view,
            font=(None, 10),
            fg_color="#1f6aa5",
            hover_color="#0d47a1",
            text_color="white",
            corner_radius=8
        )
        back_btn.pack(side="left", padx=3, pady=3)


def show_weather() -> None:
    """Fetch and display weather information."""
    global current_city, forecast_data
    try:
        loading_label.configure(text="Fetching...")
        get_weather_button.configure(state="disabled")
        root.update()
        
        city = city_entry.get().strip()
        current_city = city
        units = UNITS_METRIC if unit_var.get() == UNIT_CELSIUS else \
                UNITS_IMPERIAL
        temp_unit = TEMP_UNIT_METRIC if units == UNITS_METRIC else \
                    TEMP_UNIT_IMPERIAL
        wind_unit = WIND_UNIT_METRIC if units == UNITS_METRIC else \
                    WIND_UNIT_IMPERIAL
        
        logger.info(f"User requested weather for: {city} (Units: {temp_unit})")
        
        is_valid, error_message = validate_city_input(city)
        if not is_valid:
            messagebox.showwarning(TITLE_INPUT_ERROR, error_message)
            logger.warning(f"Invalid city input: {city} - {error_message}")
            loading_label.configure(text="")
            get_weather_button.configure(state="normal")
            return

        try:
            lat, lon = get_coordinates(city)
        except Exception as e:
            messagebox.showerror(
                TITLE_NETWORK_ERROR,
                f"Failed to fetch coordinates: {str(e)}"
            )
            logger.error(f"Failed to get coordinates for {city}: {str(e)}")
            icon_label.configure(image="")
            loading_label.configure(text="")
            get_weather_button.configure(state="normal")
            return

        if lat is None or lon is None:
            messagebox.showerror(
                TITLE_ERROR,
                f"City '{city}' not found. Try another spelling."
            )
            logger.warning(f"City not found: {city}")
            icon_label.configure(image="")
            loading_label.configure(text="")
            get_weather_button.configure(state="normal")
            return

        try:
            weather = get_current_weather(city, units)
        except Exception as e:
            messagebox.showerror(
                TITLE_NETWORK_ERROR,
                f"Failed to fetch weather data: {str(e)}"
            )
            logger.error(f"Failed to get weather for {city}: {str(e)}")
            icon_label.configure(image="")
            loading_label.configure(text="")
            get_weather_button.configure(state="normal")
            return

        if weather:
            temp, condition, humidity, wind_speed, icon_code = weather
            air_quality = get_air_quality(lat, lon)
            forecast_raw = get_5_day_forecast(city, units)

            global last_weather_data
            last_weather_data = {
                "city": city,
                "temp": temp,
                "condition": condition,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "air_quality": air_quality,
                "forecast": forecast_raw,
                "units": units,
                "lat": lat,
                "lon": lon
            }
            
            # Record in weather history
            weather_history_tracker.add_record(city, temp, condition)

            if isinstance(forecast_raw, str):
                forecast = forecast_raw
                forecast_data = []
            else:
                try:
                    forecast_data = process_forecast_data(
                        forecast_raw if isinstance(forecast_raw, list) else [],
                        units
                    )
                    forecast = ""
                except Exception as e:
                    logger.error(f"Error processing forecast data: {str(e)}")
                    forecast = str(forecast_raw)
                    forecast_data = []

            display_weather_with_unit(
                city, units, temp, condition,
                humidity, wind_speed, air_quality,
                forecast if forecast_data else forecast,
                icon_code
            )
            logger.info(f"Weather displayed successfully for {city}")
            loading_label.configure(text="")
            get_weather_button.configure(state="normal")

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_updated_label.configure(text=f"Last updated: {now}")
            
            search_history.add_recent(city)
            
            if search_history.is_favorite(city):
                favorite_button.configure(text="♥ Remove from Favorites")
            else:
                favorite_button.configure(text="♡ Add to Favorites")

            # Fetch weather icon
            try:
                icon_url = ICON_URL.format(icon_code)
                logger.info(f"Fetching weather icon from: {icon_url}")
                icon_response = requests.get(icon_url, timeout=API_TIMEOUT)
                
                if icon_response.status_code == 200:
                    try:
                        img_data = icon_response.content
                        img = Image.open(io.BytesIO(img_data))
                        img = img.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
                        icon_img = ImageTk.PhotoImage(img)
                        icon_label.configure(image=icon_img)
                        icon_label.image = icon_img
                        logger.info(MSG_ICON_LOADED)
                    except IOError as e:
                        icon_label.configure(image="")
                        logger.error(f"Failed to read/process image: {str(e)}")
                    except ValueError as e:
                        icon_label.configure(image="")
                        logger.error(f"Invalid image data: {str(e)}")
                    except MemoryError:
                        icon_label.configure(image="")
                        logger.error("Out of memory while processing icon")
                    except Exception as e:
                        icon_label.configure(image="")
                        logger.error(
                            f"Unexpected error processing icon: "
                            f"{type(e).__name__}: {str(e)}",
                            exc_info=True
                        )
                else:
                    icon_label.configure(image="")
                    logger.warning(
                        f"Failed to fetch icon: HTTP {icon_response.status_code}"
                    )
            except requests.Timeout:
                icon_label.configure(image="")
                logger.warning(f"Icon request timed out ({API_TIMEOUT}s)")
            except requests.ConnectionError as e:
                icon_label.configure(image="")
                logger.warning(f"Connection error fetching icon: {str(e)}")
            except requests.RequestException as e:
                icon_label.configure(image="")
                logger.warning(f"Network error fetching icon: {str(e)}")
            except Exception as e:
                icon_label.configure(image="")
                logger.error(
                    f"Unexpected error fetching icon: "
                    f"{type(e).__name__}: {str(e)}",
                    exc_info=True
                )
        else:
            result_label.configure(text=MSG_NO_WEATHER_DATA)
            icon_label.configure(image="")
            logger.error(f"No weather data returned for {city}")
    except Exception as e:
        messagebox.showerror(
            TITLE_UNEXPECTED_ERROR,
            f"{ERROR_UNEXPECTED}\n{str(e)}"
        )
        logger.error(f"Unexpected error in show_weather: {str(e)}", exc_info=True)
        icon_label.configure(image="")
        loading_label.configure(text="")
        get_weather_button.configure(state="normal")


def create_gui() -> ctk.CTk:
    """Create and configure the modern GUI using CustomTkinter."""
    global root, city_entry, unit_var, result_label, icon_label, \
           results_frame, loading_label, get_weather_button, \
           favorite_button, search_history, clock_label, \
           last_updated_label, forecast_label, forecast_button_frame, \
           weather_comparison, weather_history_tracker, app_settings
    
    # Create root window
    root = ctk.CTk()
    root.title(TITLE_MAIN)
    root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    root.resizable(True, True)
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
    
    # Initialize search history
    search_history = SearchHistory()
    
    # Initialize new features
    weather_comparison = WeatherComparison(
        units=UNITS_METRIC  # Will be updated based on user selection
    )
    weather_history_tracker = WeatherHistory()
    app_settings = Settings()
    
    # Main container
    main_container = ctk.CTkFrame(root, fg_color="#2b2b2b")
    main_container.pack(fill="both", expand=True, padx=0, pady=0)

    # Header
    header = ctk.CTkLabel(
        main_container,
        text=TITLE_MAIN,
        font=("Segoe UI", 24, "bold"),
        text_color="#1f6aa5"
    )
    header.pack(pady=PADDING_HEADER_Y)

    # Clock Display
    clock_label = ctk.CTkLabel(
        main_container,
        text="🕐 --:--:--",
        font=("Segoe UI", 12),
        text_color="#1f6aa5"
    )
    clock_label.pack(pady=5)
    update_clock()

    # Entry Frame
    entry_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    entry_frame.pack(pady=PADDING_ENTRY_Y, padx=10)
    
    ctk.CTkLabel(
        entry_frame,
        text=LABEL_CITY,
        font=("Segoe UI", 12),
        text_color="white"
    ).pack(side="left", padx=PADDING_LABEL_X)
    
    city_entry = ctk.CTkEntry(
        entry_frame,
        font=("Segoe UI", 12),
        width=200,
        placeholder_text="Enter city name...",
        corner_radius=8
    )
    city_entry.pack(side="left", fill="x", expand=True, padx=5)

    # Unit selection
    unit_var = ctk.StringVar(value=UNIT_CELSIUS)
    unit_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    unit_frame.pack(pady=PADDING_UNIT_Y)
    
    ctk.CTkLabel(
        unit_frame,
        text=LABEL_UNITS,
        font=("Segoe UI", 12, "bold"),
        text_color="white"
    ).pack(side="left", padx=(0, 10))
    
    ctk.CTkRadioButton(
        unit_frame,
        text=UNIT_CELSIUS,
        variable=unit_var,
        value=UNIT_CELSIUS,
        font=("Segoe UI", 11),
        text_color="white",
        corner_radius=8
    ).pack(side="left", padx=5)
    
    ctk.CTkRadioButton(
        unit_frame,
        text=UNIT_FAHRENHEIT,
        variable=unit_var,
        value=UNIT_FAHRENHEIT,
        font=("Segoe UI", 11),
        text_color="white",
        corner_radius=8
    ).pack(side="left", padx=5)

    # Recent Searches Button
    recent_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    recent_frame.pack(pady=5)
    
    ctk.CTkButton(
        recent_frame,
        text="📋 Recent",
        command=show_recent_searches,
        font=("Segoe UI", 11),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        text_color="white",
        corner_radius=8,
        width=120
    ).pack(side="left", padx=5)

    # Main Button
    get_weather_button = ctk.CTkButton(
        main_container,
        text=BUTTON_GET_WEATHER,
        command=show_weather,
        font=("Segoe UI", 13, "bold"),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        text_color="white",
        corner_radius=8,
        height=40
    )
    get_weather_button.pack(pady=PADDING_BUTTON_Y, padx=20, fill="x")

    # Loading Indicator
    loading_label = ctk.CTkLabel(
        main_container,
        text="",
        font=("Segoe UI", 11),
        text_color="#1f6aa5"
    )
    loading_label.pack(pady=2)

    # Favorite Button
    favorite_button = ctk.CTkButton(
        main_container,
        text="♡ Add to Favorites",
        command=toggle_favorite,
        font=("Segoe UI", 10),
        fg_color="#d32f2f",
        hover_color="#b71c1c",
        text_color="white",
        corner_radius=8,
        width=150
    )
    favorite_button.pack(pady=5)

    # Feature Buttons Frame
    feature_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    feature_frame.pack(pady=8, padx=10, fill="x")
    
    ctk.CTkButton(
        feature_frame,
        text="📊 Compare",
        command=add_city_to_comparison,
        font=("Segoe UI", 9),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        width=95,
        corner_radius=6,
        height=28
    ).pack(side="left", padx=2)
    
    ctk.CTkButton(
        feature_frame,
        text="📈 History",
        command=show_weather_history_info,
        font=("Segoe UI", 9),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        width=95,
        corner_radius=6,
        height=28
    ).pack(side="left", padx=2)
    
    ctk.CTkButton(
        feature_frame,
        text="📅 Forecast",
        command=show_forecast_dialog,
        font=("Segoe UI", 9),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        width=95,
        corner_radius=6,
        height=28
    ).pack(side="left", padx=2)
    
    ctk.CTkButton(
        feature_frame,
        text="🌫️ AQI",
        command=show_air_quality_dialog,
        font=("Segoe UI", 9),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        width=95,
        corner_radius=6,
        height=28
    ).pack(side="left", padx=2)
    
    ctk.CTkButton(
        feature_frame,
        text="☀️ Sun Info",
        command=show_sunrise_sunset_info,
        font=("Segoe UI", 9),
        fg_color="#1f6aa5",
        hover_color="#0d47a1",
        width=95,
        corner_radius=6,
        height=28
    ).pack(side="left", padx=2)
    
    ctk.CTkButton(
        feature_frame,
        text="⚙️ Settings",
        command=show_settings_dialog,
        font=("Segoe UI", 9),
        fg_color="#555555",
        hover_color="#666666",
        width=80,
        corner_radius=6,
        height=28
    ).pack(side="right", padx=2)

    # Icon
    icon_label = ctk.CTkLabel(main_container, text="")
    icon_label.pack(pady=PADDING_ICON_Y)

    # Results Frame with scrollable content
    results_frame = ctk.CTkFrame(
        main_container,
        fg_color="#1e1e1e",
        corner_radius=12,
        border_width=2,
        border_color="#1f6aa5"
    )
    results_frame.pack(
        pady=PADDING_FRAME_Y,
        padx=PADDING_FRAME_X,
        fill="both",
        expand=True
    )

    # Scrollable results container
    results_scroll = ctk.CTkScrollableFrame(
        results_frame,
        fg_color="#1e1e1e"
    )
    results_scroll.pack(
        fill="both",
        expand=True,
        padx=0,
        pady=0
    )

    result_label = ctk.CTkLabel(
        results_scroll,
        text="",
        font=("Segoe UI", 11),
        justify="left",
        wraplength=DEFAULT_WRAPLENGTH,
        text_color="white"
    )
    result_label.pack(
        padx=PADDING_RESULT_X,
        pady=PADDING_RESULT_Y,
        fill="x",
        anchor="nw"
    )

    # Last Updated Timestamp
    last_updated_label = ctk.CTkLabel(
        results_scroll,
        text="",
        font=("Segoe UI", 10),
        text_color="#1f6aa5"
    )
    last_updated_label.pack(padx=PADDING_RESULT_X, pady=(0, PADDING_RESULT_Y), anchor="w")

    # Forecast Display (hidden - shown via dialog instead)
    forecast_label = ctk.CTkLabel(
        results_scroll,
        text="",
        font=("Segoe UI", 11),
        justify="left",
        wraplength=DEFAULT_WRAPLENGTH,
        text_color="white"
    )
    # forecast_label not packed - shown via dialog

    # Forecast Button Frame (not shown)
    forecast_button_frame = ctk.CTkFrame(
        results_scroll,
        fg_color="transparent"
    )
    # forecast_button_frame not packed - shown via dialog

    # Bind window resize event
    root.bind("<Configure>", update_wraplength)

    return root
