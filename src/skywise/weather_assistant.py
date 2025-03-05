import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from weather_service import WeatherService
import streamlit as st

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
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

class WeatherAssistant:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant specializing in weather information. "
                    "Your responses should be clear, engaging, and tailored to help users plan their day effectively. "
                    "Follow these guidelines: "
                    "- Use appropriate emojis to represent weather conditions (e.g., ☀️ for sunny, 🌧️ for rain, ☁️ for cloudy, ❄️ for snow, ⛈️ for thunderstorms, 🌫️ for fog). "
                    "- Provide actionable insights and practical advice based on the weather data. For example, suggest clothing, activities, or precautions. "
                    "- Leverage all available weather data (e.g., temperature, humidity, wind speed, UV index, air quality, visibility, sunrise/sunset times) to craft detailed, human-friendly responses. "
                    "- Tailor your tone and recommendations to the user's query and context. For instance, if they ask about outdoor activities, focus on relevant factors like wind, precipitation, or visibility. "
                    "- Ensure your response is easy to read by using bullet points, short sentences, and clear language."
                )
            }
        ]

    def ask_weather(self, question, use_emojis=True):
        """Handles the conversation and function calling."""
        self.messages.append({"role": "user", "content": question})

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
            messages=self.messages,
            tools=tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {"get_current_weather": WeatherService.get_current_weather}
            self.messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                if function_to_call:
                    function_response = function_to_call(
                        location=function_args.get("location"),
                        unit=st.session_state.unit,  # Use the selected unit from session state
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

                    # Pass the weather data to the LLM for crafting the response
                    self.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(weather_data),
                        }
                    )

            # Step 3: Call OpenAI again with the results
            second_response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
            )

            response_message = second_response.choices[0].message

            # Extract the final response and ensure it includes the emoji
            final_response = response_message.content
            weather_data = json.loads(self.messages[-1]["content"])
            emoji = weather_data.get("emoji", "🌤️")

            if use_emojis:
                return f"{final_response} {emoji}"
            else:
                return final_response

        return "Sorry, I couldn't process your request. 😔"
