"""GUI components for Weather Mate application."""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import requests
import logging
from typing import Optional
from datetime import datetime
import config

from config import (
    TITLE_MAIN, LABEL_CITY, LABEL_UNITS, UNIT_CELSIUS, UNIT_FAHRENHEIT, BUTTON_GET_WEATHER,
    UNITS_METRIC, UNITS_IMPERIAL, TEMP_UNIT_METRIC, TEMP_UNIT_IMPERIAL,
    WIND_UNIT_METRIC, WIND_UNIT_IMPERIAL,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT,
    FONT_HEADER_SIZE, FONT_LABEL_SIZE, FONT_SMALL_SIZE, FONT_RESULT_SIZE,
    BG_COLOR_PRIMARY, BG_COLOR_SECONDARY, COLOR_HEADER, COLOR_BUTTON_HOVER, COLOR_TEXT_PRIMARY,
    PADDING_HEADER_Y, PADDING_ENTRY_Y, PADDING_UNIT_Y, PADDING_BUTTON_Y, PADDING_ICON_Y,
    PADDING_FRAME_Y, PADDING_FRAME_X, PADDING_LABEL_X, PADDING_RESULT_X, PADDING_RESULT_Y,
    ENTRY_WIDTH, MIN_WRAPLENGTH, DEFAULT_WRAPLENGTH, FRAME_PADDING_WIDTH, ICON_SIZE, API_TIMEOUT,
    ICON_URL, WEATHER_DISPLAY_FORMAT,
    TITLE_INPUT_ERROR, TITLE_NETWORK_ERROR, TITLE_ERROR, TITLE_UNEXPECTED_ERROR,
    ERROR_NETWORK_SERVICE, ERROR_FETCH_WEATHER, ERROR_CITY_NOT_FOUND, ERROR_UNEXPECTED,
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


# Global GUI variables (will be initialized in create_gui)
root: tk.Tk
city_entry: tk.Entry
unit_var: tk.StringVar
result_label: tk.Label
icon_label: tk.Label
results_frame: tk.Frame
loading_label: tk.Label
get_weather_button: tk.Button
favorite_button: tk.Button
search_history: SearchHistory
current_city: str = ""
last_weather_data: Optional[dict] = None  # Store last weather for unit conversion
clock_label: tk.Label
last_updated_label: tk.Label
forecast_data: list = []  # Store forecast day objects
forecast_label: tk.Label  # Display forecast
forecast_button_frame: tk.Frame  # Frame for forecast expansion buttons
expanded_forecast_date: Optional[str] = None  # Track which date is expanded


def update_wraplength(event: Optional[tk.Event] = None) -> None:
    """Update text wraplength when window is resized.
    
    Args:
        event: Tkinter event object (optional, called by bind)
    """
    # Calculate wraplength as 90% of available width minus padding
    available_width = results_frame.winfo_width() - FRAME_PADDING_WIDTH
    new_wraplength = max(MIN_WRAPLENGTH, available_width)  # Minimum wrap width
    result_label.config(wraplength=new_wraplength)


def show_recent_searches() -> None:
    """Display recent cities in a menu.
    
    Creates a popup menu with recently searched cities.
    """
    recent = search_history.get_recent()
    if not recent:
        messagebox.showinfo("Recent Searches", "No recent searches yet.")
        return
    
    # Create a simple dialog showing recent searches
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
        favorite_button.config(text="♡ Add to Favorites")
        messagebox.showinfo(
            "Removed",
            f"'{current_city}' removed from favorites."
        )
    else:
        search_history.add_favorite(current_city)
        favorite_button.config(text="♥ Remove from Favorites")
        messagebox.showinfo(
            "Added",
            f"'{current_city}' added to favorites."
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
    """Display weather with appropriate unit labels and emoji.
    
    Args:
        city: City name
        units: Units ('metric' or 'imperial')
        temp: Temperature value
        condition: Weather condition
        humidity: Humidity percentage
        wind_speed: Wind speed value
        air_quality: Air quality string
        forecast: Forecast data
        icon_code: OpenWeatherMap icon code for emoji
    """
    temp_unit = TEMP_UNIT_METRIC if units == UNITS_METRIC else TEMP_UNIT_IMPERIAL
    wind_unit = WIND_UNIT_METRIC if units == UNITS_METRIC else WIND_UNIT_IMPERIAL
    emoji = get_weather_emoji(icon_code)
    
    # Generate weather alerts
    alerts = generate_weather_alerts(
        temp, wind_speed, air_quality, units
    )
    
    # Format with emoji at the beginning
    result = (
        f"{emoji} {condition.upper()}\n\n"
        f"City: {city}\n"
        f"Temperature: {temp} {temp_unit}\n"
        f"Humidity: {humidity}%\n"
        f"Wind Speed: {wind_speed} {wind_unit}\n"
        f"Air Quality Index: {air_quality}\n"
    )
    
    # Add alerts if any
    if alerts:
        result += f"\n⚠️ ALERTS:\n{alerts}\n"
    
    result += f"\n5-Day Forecast:{forecast}"
    result_label.config(text=result)


def generate_weather_alerts(
    temp: float,
    wind_speed: float,
    air_quality: str,
    units: str
) -> str:
    """Generate weather alert messages based on conditions.
    
    Args:
        temp: Temperature value
        wind_speed: Wind speed
        air_quality: Air quality string
        units: Unit system ('metric' or 'imperial')
        
    Returns:
        Alert messages or empty string if no alerts
    """
    alerts = []
    
    # Temperature alerts (extreme heat/cold)
    if units == UNITS_METRIC:
        if temp >= 40:
            alerts.append("🔴 Extreme heat warning!")
        elif temp >= 35:
            alerts.append("🟠 High temperature alert")
        elif temp <= -20:
            alerts.append("🔴 Extreme cold warning!")
        elif temp <= -10:
            alerts.append("🟠 Low temperature alert")
    else:  # Fahrenheit
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
    else:  # mph
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
        clock_label.config(text=f"🕐 {current_time}")
        # Schedule next update
        clock_label.after(1000, update_clock)
    except:
        pass  # Stop if widget is destroyed


def toggle_forecast_expansion(date: str) -> None:
    """Toggle the detailed view for a specific forecast date.
    
    Args:
        date: The date to expand/collapse (YYYY-MM-DD format)
    """
    global expanded_forecast_date
    
    # Toggle expand/collapse
    if expanded_forecast_date == date:
        expanded_forecast_date = None
    else:
        expanded_forecast_date = date
    
    # Redraw forecast
    update_forecast_display()


def reset_forecast_view() -> None:
    """Reset forecast view to summary."""
    global expanded_forecast_date
    expanded_forecast_date = None
    update_forecast_display()


def update_forecast_display() -> None:
    """Update forecast label with current expansion state."""
    global forecast_data, expanded_forecast_date
    
    if not forecast_data:
        forecast_label.config(text="")
        # Clear buttons
        for widget in forecast_button_frame.winfo_children():
            widget.destroy()
        return
    
    # Create forecast view
    forecast_text = create_forecast_view(
        forecast_data,
        expanded_forecast_date
    )
    
    forecast_label.config(text=forecast_text)
    
    # Clear previous buttons
    for widget in forecast_button_frame.winfo_children():
        widget.destroy()
    
    # Create buttons for each day (only show if not expanded)
    if not expanded_forecast_date:
        for day in forecast_data[:5]:  # Limit to 5 days
            btn = tk.Button(
                forecast_button_frame,
                text=f"📅 {day.date}",
                command=lambda d=day.date: toggle_forecast_expansion(d),
                font=config.FONTS["small"],
                bg=COLOR_HEADER,
                fg="white",
                activebackground=COLOR_BUTTON_HOVER,
                activeforeground="white",
                relief="raised",
                bd=1,
                padx=5
            )
            btn.pack(side="left", padx=2, pady=3)
    else:
        # Show back button when viewing details
        back_btn = tk.Button(
            forecast_button_frame,
            text="⬅️ Back to Summary",
            command=reset_forecast_view,
            font=config.FONTS["small"],
            bg=COLOR_HEADER,
            fg="white",
            activebackground=COLOR_BUTTON_HOVER,
            activeforeground="white",
            relief="raised",
            bd=1,
            padx=5
        )
        back_btn.pack(side="left", padx=2, pady=3)


def show_weather() -> None:
    """Fetch and display weather information for the user's city."""
    global current_city, forecast_data
    try:
        # Show loading indicator
        loading_label.config(text="Fetching...")
        get_weather_button.config(state="disabled")
        root.update()
        
        city = city_entry.get().strip()
        current_city = city
        units = UNITS_METRIC if unit_var.get() == UNIT_CELSIUS else UNITS_IMPERIAL
        temp_unit = TEMP_UNIT_METRIC if units == UNITS_METRIC else TEMP_UNIT_IMPERIAL
        wind_unit = WIND_UNIT_METRIC if units == UNITS_METRIC else WIND_UNIT_IMPERIAL
        
        logger.info(f"User requested weather for: {city} (Units: {temp_unit})")
        
        # Validate city input
        is_valid, error_message = validate_city_input(city)
        if not is_valid:
            messagebox.showwarning(TITLE_INPUT_ERROR, error_message)
            logger.warning(f"Invalid city input: {city} - {error_message}")
            loading_label.config(text="")
            get_weather_button.config(state="normal")
            return

        try:
            lat, lon = get_coordinates(city)
        except Exception as e:
            messagebox.showerror(
                TITLE_NETWORK_ERROR,
                f"Failed to fetch coordinates: {str(e)}"
            )
            logger.error(f"Failed to get coordinates for {city}: {str(e)}")
            icon_label.config(image="")
            loading_label.config(text="")
            get_weather_button.config(state="normal")
            return

        if lat is None or lon is None:
            messagebox.showerror(
                TITLE_ERROR,
                f"City '{city}' not found. Try another spelling."
            )
            logger.warning(f"City not found: {city}")
            icon_label.config(image="")
            loading_label.config(text="")
            get_weather_button.config(state="normal")
            return

        try:
            weather = get_current_weather(city, units)
        except Exception as e:
            messagebox.showerror(
                TITLE_NETWORK_ERROR,
                f"Failed to fetch weather data: {str(e)}"
            )
            logger.error(f"Failed to get weather for {city}: {str(e)}")
            icon_label.config(image="")
            loading_label.config(text="")
            get_weather_button.config(state="normal")
            return

        if weather:
            temp, condition, humidity, wind_speed, icon_code = weather
            air_quality = get_air_quality(lat, lon)
            forecast_raw = get_5_day_forecast(city, units)

            # Store for unit conversion
            global last_weather_data
            last_weather_data = {
                "city": city,
                "temp": temp,
                "condition": condition,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "air_quality": air_quality,
                "forecast": forecast_raw,
                "units": units
            }

            # Process forecast data
            if isinstance(forecast_raw, str):
                # If it's a text summary, use as-is
                forecast = forecast_raw
                forecast_data = []
            else:
                # Try to parse forecast data as structured
                try:
                    forecast_data = process_forecast_data(
                        forecast_raw if isinstance(forecast_raw, list) else [],
                        units
                    )
                    forecast = ""  # Let display_weather_with_unit use processed data
                except Exception as e:
                    logger.error(f"Error processing forecast data: {str(e)}")
                    forecast = str(forecast_raw)
                    forecast_data = []

            # Display with current units
            display_weather_with_unit(
                city, units, temp, condition,
                humidity, wind_speed, air_quality,
                forecast if forecast_data else forecast,
                icon_code
            )
            logger.info(f"Weather displayed successfully for {city}")
            loading_label.config(text="")
            get_weather_button.config(state="normal")
            
            # Update forecast display
            if forecast_data:
                update_forecast_display()
            elif forecast:
                forecast_label.config(text=forecast)
            
            # Update "last updated" timestamp
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_updated_label.config(text=f"Last updated: {now}")
            
            # Add to search history
            search_history.add_recent(city)
            
            # Update favorite button state
            if search_history.is_favorite(city):
                favorite_button.config(text="♥ Remove from Favorites")
            else:
                favorite_button.config(text="♡ Add to Favorites")

            # Weather icon
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
                        icon_label.config(image=icon_img)
                        icon_label.image = icon_img
                        logger.info(MSG_ICON_LOADED)
                    except IOError as e:
                        icon_label.config(image="")
                        logger.error(f"Failed to read/process image file: {str(e)}")
                    except ValueError as e:
                        icon_label.config(image="")
                        logger.error(f"Invalid image data or format: {str(e)}")
                    except MemoryError:
                        icon_label.config(image="")
                        logger.error("Out of memory while processing weather icon")
                    except Exception as e:
                        icon_label.config(image="")
                        logger.error(
                            f"Unexpected error while processing weather icon: "
                            f"{type(e).__name__}: {str(e)}",
                            exc_info=True
                        )
                else:
                    icon_label.config(image="")
                    logger.warning(
                        f"Failed to fetch weather icon: HTTP {icon_response.status_code}"
                    )
            except requests.Timeout:
                icon_label.config(image="")
                logger.warning(f"Weather icon request timed out ({API_TIMEOUT} second timeout)")
            except requests.ConnectionError as e:
                icon_label.config(image="")
                logger.warning(f"Connection error while fetching weather icon: {str(e)}")
            except requests.RequestException as e:
                icon_label.config(image="")
                logger.warning(f"Network error while fetching weather icon: {str(e)}")
            except Exception as e:
                icon_label.config(image="")
                logger.error(
                    f"Unexpected error while fetching weather icon: "
                    f"{type(e).__name__}: {str(e)}",
                    exc_info=True
                )
        else:
            result_label.config(text=MSG_NO_WEATHER_DATA)
            icon_label.config(image="")
            logger.error(f"No weather data returned for {city}")
    except Exception as e:
        messagebox.showerror(TITLE_UNEXPECTED_ERROR, f"{ERROR_UNEXPECTED}\n{str(e)}")
        logger.error(f"Unexpected error in show_weather: {str(e)}", exc_info=True)
        icon_label.config(image="")
        loading_label.config(text="")
        get_weather_button.config(state="normal")


def create_gui() -> tk.Tk:
    """Create and configure the GUI.
    
    Returns:
        The root Tkinter window
    """
    global root, city_entry, unit_var, result_label, icon_label, results_frame, loading_label, get_weather_button, favorite_button, search_history, clock_label, last_updated_label, forecast_label, forecast_button_frame
    
    # --- GUI Setup ---
    root = tk.Tk()
    root.title(TITLE_MAIN)

    # Set minimum window size (470x600) and allow resizing
    root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    root.resizable(True, True)
    root.configure(bg=BG_COLOR_PRIMARY)

    # Set initial window size (can now be resized by user)
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
    
    # Initialize search history
    search_history = SearchHistory()
    
    # Initialize system-independent fonts (AFTER root is created)
    import config
    config.FONTS = get_default_fonts()

    # Main container frame for responsive layout
    main_container = tk.Frame(root, bg=BG_COLOR_PRIMARY)
    main_container.pack(fill="both", expand=True)

    # Header
    header = tk.Label(
        main_container,
        text=TITLE_MAIN,
        font=config.FONTS["header"],
        fg=COLOR_HEADER,
        bg=BG_COLOR_PRIMARY
    )
    header.pack(pady=PADDING_HEADER_Y)

    # Clock Display
    clock_label = tk.Label(
        main_container,
        text="🕐 --:--:--",
        font=config.FONTS["small"],
        fg=COLOR_HEADER,
        bg=BG_COLOR_PRIMARY
    )
    clock_label.pack(pady=2)
    
    # Start the clock update
    update_clock()

    # Entry Frame
    entry_frame = tk.Frame(main_container, bg=BG_COLOR_PRIMARY)
    entry_frame.pack(pady=PADDING_ENTRY_Y, padx=10)
    tk.Label(
        entry_frame,
        text=LABEL_CITY,
        font=config.FONTS["label"],
        bg=BG_COLOR_PRIMARY,
        fg=COLOR_HEADER
    ).pack(side="left", padx=PADDING_LABEL_X)
    city_entry = tk.Entry(
        entry_frame,
        font=config.FONTS["label"],
        width=ENTRY_WIDTH,
        relief="groove",
        bd=2
    )
    city_entry.pack(side="left", fill="x", expand=True)

    # Unit selection
    unit_var = tk.StringVar(value=UNIT_CELSIUS)
    unit_frame = tk.Frame(main_container, bg=BG_COLOR_PRIMARY)
    unit_frame.pack(pady=PADDING_UNIT_Y)
    tk.Label(
        unit_frame,
        text=LABEL_UNITS,
        font=config.FONTS["label_bold"],
        bg=BG_COLOR_PRIMARY,
        fg=COLOR_HEADER
    ).pack(side="left", padx=(0, 5))
    tk.Radiobutton(
        unit_frame,
        text=UNIT_CELSIUS,
        variable=unit_var,
        value=UNIT_CELSIUS,
        font=config.FONTS["small"],
        bg=BG_COLOR_PRIMARY,
        fg=COLOR_HEADER,
        selectcolor=BG_COLOR_SECONDARY
    ).pack(side="left")
    tk.Radiobutton(
        unit_frame,
        text=UNIT_FAHRENHEIT,
        variable=unit_var,
        value=UNIT_FAHRENHEIT,
        font=config.FONTS["small"],
        bg=BG_COLOR_PRIMARY,
        fg=COLOR_HEADER,
        selectcolor=BG_COLOR_SECONDARY
    ).pack(side="left")

    # Recent Searches Button
    recent_frame = tk.Frame(main_container, bg=BG_COLOR_PRIMARY)
    recent_frame.pack(pady=5)
    tk.Button(
        recent_frame,
        text="📋 Recent",
        command=show_recent_searches,
        font=config.FONTS["small"],
        bg=COLOR_HEADER,
        fg="white",
        activebackground=COLOR_BUTTON_HOVER,
        activeforeground="white",
        relief="raised",
        bd=2,
        padx=8
    ).pack(side="left", padx=5)

    # Button
    get_weather_button = tk.Button(
        main_container,
        text=BUTTON_GET_WEATHER,
        command=show_weather,
        font=config.FONTS["label"],
        bg=COLOR_HEADER,
        fg="white",
        activebackground=COLOR_BUTTON_HOVER,
        activeforeground="white",
        relief="raised",
        bd=3,
        cursor="hand2"
    )
    get_weather_button.pack(pady=PADDING_BUTTON_Y)

    # Loading Indicator
    loading_label = tk.Label(
        main_container,
        text="",
        font=config.FONTS["small"],
        fg=COLOR_HEADER,
        bg=BG_COLOR_PRIMARY
    )
    loading_label.pack(pady=2)

    # Favorite Button
    favorite_button = tk.Button(
        main_container,
        text="♡ Add to Favorites",
        command=toggle_favorite,
        font=config.FONTS["small"],
        bg="#d32f2f",
        fg="white",
        activebackground="#b71c1c",
        activeforeground="white",
        relief="raised",
        bd=2,
        padx=8
    )
    favorite_button.pack(pady=2)

    # Icon
    icon_label = tk.Label(main_container, bg=BG_COLOR_PRIMARY)
    icon_label.pack(pady=PADDING_ICON_Y)

    # Results Frame
    results_frame = tk.Frame(main_container, bg=BG_COLOR_SECONDARY, bd=2, relief="groove")
    results_frame.pack(pady=PADDING_FRAME_Y, padx=PADDING_FRAME_X, fill="both", expand=True)

    result_label = tk.Label(
        results_frame,
        text="",
        font=config.FONTS["result"],
        justify="left",
        wraplength=DEFAULT_WRAPLENGTH,
        bg=BG_COLOR_SECONDARY,
        fg=COLOR_TEXT_PRIMARY
    )
    result_label.pack(padx=PADDING_RESULT_X, pady=PADDING_RESULT_Y, fill="both", expand=True)

    # Last Updated Timestamp
    last_updated_label = tk.Label(
        results_frame,
        text="",
        font=config.FONTS["small"],
        fg=COLOR_HEADER,
        bg=BG_COLOR_SECONDARY
    )
    last_updated_label.pack(padx=PADDING_RESULT_X, pady=(0, PADDING_RESULT_Y))

    # Forecast Display
    forecast_label = tk.Label(
        results_frame,
        text="",
        font=config.FONTS["result"],
        justify="left",
        wraplength=DEFAULT_WRAPLENGTH,
        bg=BG_COLOR_SECONDARY,
        fg=COLOR_TEXT_PRIMARY
    )
    forecast_label.pack(padx=PADDING_RESULT_X, pady=PADDING_RESULT_Y, fill="both", expand=True)

    # Forecast Button Frame (for day expansion buttons)
    forecast_button_frame = tk.Frame(results_frame, bg=BG_COLOR_SECONDARY)
    forecast_button_frame.pack(padx=PADDING_RESULT_X, pady=5, fill="x")

    # Bind window resize event to update wraplength
    root.bind("<Configure>", update_wraplength)

    return root
