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
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "temperature_feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_gust": data["wind"].get("gust", "N/A"),
                "visibility": data.get("visibility", "N/A"),
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"],
                "unit": "Celsius" if unit == "metric" else "Fahrenheit",
                "description": data["weather"][0]["description"],
                "cloudiness": data["clouds"]["all"],
                "precipitation_probability": data.get("pop", "N/A"),
            }
            return json.dumps(weather_info)
        else:
            return json.dumps({"error": f"Could not fetch weather for {location}"})

    @staticmethod
    def get_custom_forecast(location, days, unit="metric"):
        """Fetch customizable weather forecast from OpenWeather API"""
        base_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": weather_api_key,
            "units": unit,
            "cnt": days * 8  # Request 8 results per day
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            forecast_info = []

            for i in range(days):
                day_data = data["list"][i*8:(i+1)*8]  # Get 8 results for each day
                avg_temp = sum(item["main"]["temp"] for item in day_data) / 8
                avg_humidity = sum(item["main"]["humidity"] for item in day_data) / 8
                description = day_data[0]["weather"][0]["description"]

                forecast_info.append({
                    "day": i + 1,
                    "temperature": avg_temp,
                    "humidity": avg_humidity,
                    "description": description,
                })

            return json.dumps(forecast_info)
        else:
            return json.dumps({"error": f"Could not fetch forecast for {location}"})
