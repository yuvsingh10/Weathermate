"""GUI components for Weather Mate application."""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import requests
import logging
from typing import Optional

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
    get_default_fonts, FONTS,
    logger
)
from api import (
    validate_city_input, get_coordinates, get_air_quality,
    get_current_weather, get_5_day_forecast
)


# Global GUI variables (will be initialized in create_gui)
root: tk.Tk
city_entry: tk.Entry
unit_var: tk.StringVar
result_label: tk.Label
icon_label: tk.Label
results_frame: tk.Frame


def update_wraplength(event: Optional[tk.Event] = None) -> None:
    """Update text wraplength when window is resized.
    
    Args:
        event: Tkinter event object (optional, called by bind)
    """
    # Calculate wraplength as 90% of available width minus padding
    available_width = results_frame.winfo_width() - FRAME_PADDING_WIDTH
    new_wraplength = max(MIN_WRAPLENGTH, available_width)  # Minimum wrap width
    result_label.config(wraplength=new_wraplength)


def show_weather() -> None:
    """Fetch and display weather information for the user's city."""
    try:
        city = city_entry.get().strip()
        units = UNITS_METRIC if unit_var.get() == UNIT_CELSIUS else UNITS_IMPERIAL
        temp_unit = TEMP_UNIT_METRIC if units == UNITS_METRIC else TEMP_UNIT_IMPERIAL
        wind_unit = WIND_UNIT_METRIC if units == UNITS_METRIC else WIND_UNIT_IMPERIAL
        
        logger.info(f"User requested weather for: {city} (Units: {temp_unit})")
        
        # Validate city input
        is_valid, error_message = validate_city_input(city)
        if not is_valid:
            messagebox.showwarning(TITLE_INPUT_ERROR, error_message)
            logger.warning(f"Invalid city input: {city} - {error_message}")
            return

        try:
            lat, lon = get_coordinates(city)
        except Exception as e:
            messagebox.showerror(TITLE_NETWORK_ERROR, f"{ERROR_NETWORK_SERVICE}\n{str(e)}")
            logger.error(f"Failed to get coordinates for {city}: {str(e)}")
            icon_label.config(image="")
            return

        if lat is None or lon is None:
            messagebox.showerror(TITLE_ERROR, ERROR_CITY_NOT_FOUND.format(city))
            logger.warning(f"City not found: {city}")
            icon_label.config(image="")
            return

        try:
            weather = get_current_weather(city, units)
        except Exception as e:
            messagebox.showerror(TITLE_NETWORK_ERROR, f"{ERROR_FETCH_WEATHER}\n{str(e)}")
            logger.error(f"Failed to get weather for {city}: {str(e)}")
            icon_label.config(image="")
            return

        if weather:
            temp, condition, humidity, wind_speed, icon_code = weather
            air_quality = get_air_quality(lat, lon)
            forecast = get_5_day_forecast(city, units)

            result = WEATHER_DISPLAY_FORMAT.format(
                city=city,
                condition=condition,
                temp=temp,
                temp_unit=temp_unit,
                humidity=humidity,
                wind_speed=wind_speed,
                wind_unit=wind_unit,
                air_quality=air_quality,
                forecast=forecast
            )
            result_label.config(text=result)
            logger.info(f"Weather displayed successfully for {city}")

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


def create_gui() -> tk.Tk:
    """Create and configure the GUI.
    
    Returns:
        The root Tkinter window
    """
    global root, city_entry, unit_var, result_label, icon_label, results_frame
    
    # --- GUI Setup ---
    root = tk.Tk()
    root.title(TITLE_MAIN)

    # Set minimum window size (470x600) and allow resizing
    root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    root.resizable(True, True)
    root.configure(bg=BG_COLOR_PRIMARY)

    # Set initial window size (can now be resized by user)
    root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
    
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

    # Button
    tk.Button(
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
    ).pack(pady=PADDING_BUTTON_Y)

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

    # Bind window resize event to update wraplength
    root.bind("<Configure>", update_wraplength)

    return root
