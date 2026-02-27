# WeatherMate 🌤️

A modern, feature-rich Python weather application with a beautiful dark-themed GUI. Get real-time weather, forecasts, air quality data, and more for any city in the world.

## ✨ Features

### Core Weather
- 🌡️ **Real-time Weather** - Current temperature, humidity, wind speed, and conditions
- 📊 **5-Day Forecast** - Interactive hourly forecast with clickable day details
- 🎨 **Weather Icons** - 24 emoji-based weather condition icons
- ⚠️ **Smart Alerts** - Color-coded warnings for extreme weather

### Advanced Features
- 🌫️ **Air Quality Details** - AQI levels (1-5) with health recommendations and precautions
- ☀️ **Sunrise/Sunset Info** - Exact sunrise/sunset times and UV index estimation
- 📊 **Weather Comparison** - Compare weather side-by-side for up to 3 cities simultaneously
- 📈 **Weather History** - Track temperature trends (last 30 records per city)
- ⚙️ **Settings & Preferences** - Customize theme, notification, and auto-refresh options

### User Experience
- 💎 **Modern UI** - CustomTkinter dark theme with smooth animations and hover effects
- 🕐 **Live Clock** - Real-time clock display
- ❤️ **Favorites** - Save and quickly access your favorite cities
- 📋 **Recent Searches** - Auto-tracks your weather search history
- 📱 **Responsive Design** - Scales beautifully on any screen size
- 🌙 **Dark Theme** - Easy on the eyes with sleek blue accents

## 🛠️ Technical Stack

- **Language**: Python 3.8+
- **GUI Framework**: CustomTkinter (modern Tkinter wrapper)
- **APIs**: OpenWeatherMap (weather, forecast, air quality) + Sunrise-Sunset API
- **Type System**: Full type hints throughout all modules
- **Architecture**: Modular design with 14 independent Python modules
- **Data**: Session-only (in-memory), with optional persistent search history

## 📋 Requirements

- Python 3.8 or higher
- OpenWeatherMap API key (free tier available at https://openweathermap.org/api)

## 🚀 Installation

1. **Clone or download the project**
   ```bash
   cd Weathermate
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   ```bash
   # Copy the example file
   copy .env.example .env  # Windows
   # OR
   cp .env.example .env    # macOS/Linux
   
   # Edit .env and add your OpenWeatherMap API key
   OPENWEATHER_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## 📖 How to Use

1. **Search Weather** - Enter a city name and click "Get Weather"
2. **Choose Units** - Select Celsius or Fahrenheit
3. **View Details** - See current weather and 5-day forecast
4. **Explore Features**:
   - 📊 **Compare** (up to 3 cities)
   - 📈 **History** (temperature trends)
   - 🌫️ **AQI** (air quality & health tips)
   - ☀️ **Sun Info** (sunrise/sunset/UV index)
   - ⚙️ **Settings** (user preferences)
5. **Save Favorites** - Click the ♡ button to add to favorites

## 📁 Project Structure

```
Weathermate/
├── main.py                    # Entry point
├── modern_ui.py              # CustomTkinter GUI (950+ lines)
├── api.py                    # OpenWeatherMap API functions
├── config.py                 # Constants & configuration
├── models.py                 # Data structures
├── validation.py             # Response validation
├── forecast_processor.py      # 5-day forecast processing
├── history.py                # Search history manager
│
├── weather_comparison.py      # Multi-city comparison
├── weather_history.py         # Temperature trend tracking
├── air_quality_details.py     # AQI health data
├── sunrise_sunset.py          # Sun time & UV info
├── settings.py                # User preferences (session-only)
├── settings_dialog.py         # Settings UI
│
├── requirements.txt           # Python dependencies
├── .env.example              # API key template
├── search_history.json       # Persistent search history
└── README.md                 # This file
```

## 📦 Dependencies

- `requests` - HTTP requests for API calls
- `Pillow` - Image processing for weather icons
- `customtkinter` - Modern GUI framework
- `python-dotenv` - Environment variable management

## ⚙️ Configuration

All settings can be customized in `config.py`:
- API endpoints, timeouts, and intervals
- Window dimensions and appearance
- Font sizes, colors, and themes
- 24 emoji weather condition mappings
- Error messages and labels

## 🔑 API Key Setup

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Generate an API key
4. Add it to `.env` file:
   ```
   OPENWEATHER_API_KEY=your_key_here
   ```

## 📊 Module Overview

| Module | Purpose | Lines |
|--------|---------|-------|
| `modern_ui.py` | Main GUI with all features | 950+ |
| `api.py` | Weather/forecast/air quality fetching | 277 |
| `weather_comparison.py` | 2-3 city comparison logic | 150+ |
| `weather_history.py` | Temperature trend tracking | 115 |
| `air_quality_details.py` | Health recommendations by AQI level | 200+ |
| `sunrise_sunset.py` | Sun times & UV index calculation | 150+ |
| `settings.py` | User preference management (session) | 180 |
| `settings_dialog.py` | Settings UI dialog | 300+ |
| `forecast_processor.py` | Forecast data organization | 178 |
| `validation.py` | API response validation | 303 |

## 🐛 Logging

The app logs all activities for debugging:
- API requests and responses
- User actions and settings changes
- Errors and network issues

Check the logs for troubleshooting.

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Verify `.env` file exists with your API key |
| "City not found" | Check spelling or try a major city name |
| "Connection error" | Check your internet connection |
| "No forecast data" | Try a different city (some regions may lack forecast data) |
| "Dialogs don't open" | Ensure CustomTkinter is installed: `pip install customtkinter` |

## 🎓 Learning Resources

This project demonstrates:
- Modern Python GUI development with CustomTkinter
- REST API integration and error handling
- Type hints and validation patterns
- Modular architecture and separation of concerns
- JSON data persistence
- User interface design best practices

## 📝 License

Educational project - Free to use and modify.

---

**Made with ❤️ using Python & CustomTkinter**
