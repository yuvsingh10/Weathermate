import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io

API_KEY = "06c921750b9a82d8f5d1294e1586276f"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
ICON_URL = "http://openweathermap.org/img/wn/{}@2x.png"

def get_coordinates(city):
    params = {
        "q": city,
        "appid": API_KEY
    }
    response = requests.get(WEATHER_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["coord"]["lat"], data["coord"]["lon"]
    return None, None

def get_air_quality(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }
    response = requests.get(AIR_QUALITY_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        aqi = data["list"][0]["main"]["aqi"]
        aqi_levels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        return f"{aqi} ({aqi_levels.get(aqi, 'Unknown')})"
    return "Unavailable"

def get_current_weather(city, units):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }
    response = requests.get(WEATHER_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"].title()
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        icon_code = data["weather"][0]["icon"]
        return temp, condition, humidity, wind_speed, icon_code
    return None

def get_5_day_forecast(city, units):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }
    response = requests.get(FORECAST_URL, params=params)
    forecast_text = "\n"
    if response.status_code == 200:
        data = response.json()
        temp_unit = "Celsius" if units == "metric" else "Fahrenheit"
        for i in range(0, 40, 8):  # 8 intervals = 1 per day (3-hour intervals)
            entry = data["list"][i]
            date = entry["dt_txt"].split(" ")[0]
            temp = entry["main"]["temp"]
            condition = entry["weather"][0]["description"].title()
            forecast_text += f"{date}: {condition}, {temp} {temp_unit}\n"
        return forecast_text
    return "Forecast unavailable."

def show_weather():
    city = city_entry.get().strip()
    units = "metric" if unit_var.get() == "Celsius" else "imperial"
    temp_unit = "Celsius" if units == "metric" else "Fahrenheit"
    wind_unit = "meters/second" if units == "metric" else "miles/hour"
    if not city:
        messagebox.showwarning("Input Error", "Please enter a city name.")
        return

    lat, lon = get_coordinates(city)
    if lat is None or lon is None:
        messagebox.showerror("Error", "City not found.")
        return

    weather = get_current_weather(city, units)
    if weather:
        temp, condition, humidity, wind_speed, icon_code = weather
        air_quality = get_air_quality(lat, lon)
        forecast = get_5_day_forecast(city, units)

        result = (
            f"Current Weather for {city}:\n"
            f"Condition: {condition}\n"
            f"Temperature: {temp} {temp_unit}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} {wind_unit}\n"
            f"Air Quality Index: {air_quality}\n\n"
            f"5-Day Forecast:{forecast}"
        )
        result_label.config(text=result)

        # Weather icon
        try:
            icon_url = ICON_URL.format(icon_code)
            icon_response = requests.get(icon_url)
            if icon_response.status_code == 200:
                img_data = icon_response.content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((80, 80), Image.LANCZOS)
                icon_img = ImageTk.PhotoImage(img)
                icon_label.config(image=icon_img)
                icon_label.image = icon_img
            else:
                icon_label.config(image="")
        except Exception:
            icon_label.config(image="")
    else:
        result_label.config(text="Could not retrieve weather data.")
        icon_label.config(image="")

# --- GUI Setup ---
root = tk.Tk()
root.title("Weather Mate")
root.geometry("470x600")
root.resizable(False, False)
root.configure(bg="#e3f2fd")

# Header
header = tk.Label(root, text="Weather Mate", font=("Arial Rounded MT Bold", 24, "bold"), fg="#1976d2", bg="#e3f2fd")
header.pack(pady=(18, 8))

# Entry Frame
entry_frame = tk.Frame(root, bg="#e3f2fd")
entry_frame.pack(pady=8)
tk.Label(entry_frame, text="Enter City Name:", font=("Arial", 13), bg="#e3f2fd", fg="#1976d2").pack(side="left", padx=(0, 8))
city_entry = tk.Entry(entry_frame, font=("Arial", 13), width=22, relief="groove", bd=2)
city_entry.pack(side="left")

# Unit selection
unit_var = tk.StringVar(value="Celsius")
unit_frame = tk.Frame(root, bg="#e3f2fd")
unit_frame.pack(pady=5)
tk.Label(unit_frame, text="Units:", font=("Arial", 11, "bold"), bg="#e3f2fd", fg="#1976d2").pack(side="left", padx=(0, 5))
tk.Radiobutton(unit_frame, text="Celsius", variable=unit_var, value="Celsius", font=("Arial", 11), bg="#e3f2fd", fg="#1976d2", selectcolor="#bbdefb").pack(side="left")
tk.Radiobutton(unit_frame, text="Fahrenheit", variable=unit_var, value="Fahrenheit", font=("Arial", 11), bg="#e3f2fd", fg="#1976d2", selectcolor="#bbdefb").pack(side="left")

# Button
tk.Button(root, text="Get Weather", command=show_weather, font=("Arial", 13, "bold"), bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white", relief="raised", bd=3, cursor="hand2").pack(pady=14)

# Icon
icon_label = tk.Label(root, bg="#e3f2fd")
icon_label.pack(pady=5)

# Results Frame
results_frame = tk.Frame(root, bg="#bbdefb", bd=2, relief="groove")
results_frame.pack(pady=10, padx=16, fill="both", expand=True)

result_label = tk.Label(results_frame, text="", font=("Arial", 12), justify="left", wraplength=410, bg="#bbdefb", fg="#0d47a1")
result_label.pack(padx=10, pady=12, fill="both", expand=True)

root.mainloop()
