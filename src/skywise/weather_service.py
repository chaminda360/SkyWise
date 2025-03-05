import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

weather_api_key = os.getenv("WEATHER_API_KEY")

class WeatherService:
    @staticmethod
    def get_current_weather(location, unit="metric"):
        """Fetch live weather data from OpenWeather API"""
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": weather_api_key,
            "units": unit,
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            weather_info = {
                "location": data["name"],
                "country": data["sys"]["country"],  # Include country code
                "temperature": data["main"]["temp"],
                "temperature_feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],  # Add atmospheric pressure
                "wind_speed": data["wind"]["speed"],
                "wind_gust": data["wind"].get("gust", "N/A"),  # Add wind gusts
                "visibility": data.get("visibility", "N/A"),  # Add visibility
                "sunrise": data["sys"]["sunrise"],  # Add sunrise time
                "sunset": data["sys"]["sunset"],  # Add sunset time
                "unit": "Celsius" if unit == "metric" else "Fahrenheit",
                "description": data["weather"][0]["description"],
                "cloudiness": data["clouds"]["all"],  # Add cloud coverage percentage
                "precipitation_probability": data.get("pop", "N/A"),  # Add precipitation probability
            }
            return json.dumps(weather_info)
        else:
            return json.dumps({"error": f"Could not fetch weather for {location}"})
