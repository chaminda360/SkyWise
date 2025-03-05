import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")

client = OpenAI(api_key=openai_key)

# Default emoji mapping
emoji_mapping = {
    "clear": "☀️",  # Sunny
    "rain": "🌧️",  # Rainy
    "cloud": "☁️",  # Cloudy
    "snow": "❄️",  # Snowy
    "thunderstorm": "⛈️",  # Thunderstorm
    "mist": "🌫️",  # Foggy
    "fog": "🌫️",  # Foggy
    "hot": "🔥",  # Hot temperature
    "cold": "🧊",  # Cold temperature
    "humid": "💦",  # High humidity
    "windy": "🍃",  # Windy conditions
}

# Function to fetch real-time weather data
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
            "temperature": data["main"]["temp"],
            "temperature_feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "unit": "Celsius" if unit == "metric" else "Fahrenheit",
            "description": data["weather"][0]["description"],
        }
        return json.dumps(weather_info)
    
    else:
        return json.dumps({"error": f"Could not fetch weather for {location}"})


# Function Calling Implementation
def ask_weather(question, use_emojis=True):
    """Handles the conversation and function calling."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that provides weather information. "
                "When describing the weather, always include an appropriate emoji to represent the conditions. "
                "For example, use ☀️ for sunny, 🌧️ for rain, ☁️ for cloudy, ❄️ for snow, ⛈️ for thunderstorms, and 🌫️ for fog."
            )
        },
        {
            "role": "user", 
            "content": question
        }
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name, e.g., Colombo"},
                        "unit": {"type": "string", "enum": ["celsius", "imperial"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    # Step 1: Ask OpenAI if it wants to call the function or not 
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {"get_current_weather": get_current_weather}
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            if function_to_call:
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit", "metric"),
                )

                weather_data = json.loads(function_response)
                description = weather_data.get("description", "").lower()

                # Determine primary emoji based on weather description
                emoji = next((emoji_mapping[key] for key in emoji_mapping if key in description), "🌤️")

                # Add secondary emojis based on additional parameters
                if weather_data["temperature"] > 30:
                    emoji += " 🔥"  # Hot temperature
                elif weather_data["temperature"] < 0:
                    emoji += " 🧊"  # Cold temperature
                if weather_data["humidity"] > 80:
                    emoji += " 💦"  # High humidity
                if weather_data["wind_speed"] > 15:
                    emoji += " 🍃"  # Windy conditions

                # Append emoji to the weather data
                weather_data["emoji"] = emoji
                function_response_with_emoji = json.dumps(weather_data)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response_with_emoji,
                    }
                )

        # Step 3: Call OpenAI again with the results
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )

        response_message = second_response.choices[0].message

        # Extract the final response and ensure it includes the emoji
        final_response = response_message.content
        weather_data = json.loads(messages[-1]["content"])
        emoji = weather_data.get("emoji", "🌤️")

        if use_emojis:
            return f"{final_response} {emoji}"
        else:
            return final_response

    return "Sorry, I couldn't process your request. 😔"


# Streamlit UI
st.title("🌤 SkyWise – AI Weather Assistant")
st.write("Ask about the weather in any city!")

# User input field
user_question = st.text_input("Enter your weather question:", "")

# Toggle for enabling/disabling emojis
use_emojis = st.checkbox("Enable Emojis in Responses", value=True)

if st.button("Get Weather"):
    if user_question:
        with st.spinner("Fetching weather..."):
            response = ask_weather(user_question, use_emojis)
        st.markdown(f"**Response:** {response}")
    else:
        st.error("Please enter a question.")