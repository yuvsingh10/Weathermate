# WeatherMate

A simple, clean Python weather application that displays real-time weather information for any city.

## Features

- **Real-time Weather**: Current temperature, humidity, wind speed, and weather conditions
- **Air Quality Index**: Air quality data for the selected location
- **5-Day Forecast**: Weather predictions for the next 5 days
- **Unit Selection**: View temperature in Celsius or Fahrenheit
- **Weather Icons**: Visual weather condition icons
- **Clean GUI**: Simple and responsive Tkinter interface

## Requirements

- Python 3.8 or higher
- An OpenWeatherMap API key (get a free one at https://openweathermap.org/api)

## Installation

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
   copy .env.example .env
   
   # Edit .env and add your OpenWeatherMap API key
   OPENWEATHER_API_KEY=your_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## How to Use

1. Enter a city name in the search field
2. Choose your preferred temperature unit (°C or °F)
3. Click "Get Weather" to fetch the data
4. View current weather, air quality, and forecast information

## Project Structure

```
Weathermate/
├── main.py              # Entry point
├── config.py            # Configuration and constants
├── api.py               # OpenWeatherMap API functions
├── ui.py                # GUI components
├── models.py            # Data models
├── validation.py        # Response validation
├── requirements.txt     # Dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Dependencies

- `requests` - HTTP library for API calls
- `Pillow` - Image processing for weather icons
- `python-dotenv` - Environment variable management

## Configuration

All settings can be customized in `config.py`:
- API endpoints and timeouts
- Window size and appearance
- Font sizes and colors
- Error messages and labels

## Logging

The application logs all activities to `weathermate.log` including:
- API requests and responses
- User actions
- Errors and warnings

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Make sure `.env` file exists and contains your API key |
| "City not found" | Check the spelling or try a different city name |
| "Connection error" | Check your internet connection |
| "Rate limit exceeded" | Wait a few minutes and try again |

## License

This project is for educational purposes.  
