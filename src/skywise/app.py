import os
import json
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")  

llm_name = "gpt-4o"
model = ChatOpenAI(api_key=openai_key, model=llm_name)
client = OpenAI(api_key=openai_key)


# Function to fetch real-time weather data
def get_current_weather(location, unit="metric"):
    """Fetch live weather data from OpenWeather API"""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": weather_api_key,  # Use your API key from OpenWeatherMap
        "units": unit  # Can be "metric" (Celsius) or "imperial" (Fahrenheit)
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "location": data["name"],
            "temperature": data["main"]["temp"],
            "unit": "Celsius" if unit == "metric" else "Fahrenheit",
            "description": data["weather"][0]["description"]
        }
        return json.dumps(weather_info)
    
    else:
        return json.dumps({"error": f"Could not fetch weather for {location}"})


# Function Calling Implementation
def run_conversation():
    messages = [
        {
            "role": "user",
            "content": "What's the weather like in New York, Tokyo, and London?",
        }
    ]

    # Define the function OpenAI can call
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name, e.g., New York",
                        },
                        "unit": {"type": "string", "enum": ["metric", "imperial"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    # Step 1: Ask OpenAI if it wants to call the function
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: If OpenAI suggests a function call, execute it
    if tool_calls:
        available_functions = {"get_current_weather": get_current_weather}
        messages.append(response_message)  # Store OpenAI's tool request

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions.get(function_name)

            if function_to_call:
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit", "metric"),
                )

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

        # Step 3: Call OpenAI again with the results
        second_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return second_response


# Run the conversation
print(run_conversation().model_dump_json(indent=2))
