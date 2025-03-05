# SkyWise AI Weather Assistant

SkyWise is an AI-powered weather assistant built using Streamlit and OpenAI's language model. It provides real-time weather information and insights for any city, helping users plan their day effectively.

## Features

- **Real-Time Weather Data**: Fetches live weather data using the OpenWeather API.
- **AI-Powered Insights**: Utilizes OpenAI's language model to provide actionable insights and practical advice based on weather conditions.
- **User-Friendly Interface**: Built with Streamlit for an intuitive and interactive user experience.
- **Emoji Representations**: Uses emojis to visually represent weather conditions, making the information more engaging.
- **Temperature Unit Selection**: Allows users to switch between Celsius and Fahrenheit.


## How It Works

1. **WeatherService**: Handles fetching real-time weather data from the OpenWeather API.
2. **CityExtractor**: Utilizes OpenAI to extract city names from user input.
3. **WeatherAssistant**: Manages the conversation flow, calls the necessary functions, and crafts responses using OpenAI's language model.
4. **Streamlit UI**: Provides an interactive interface for users to input their queries and view responses.

## How to Run the Application

Follow these steps to run the SkyWise AI Weather Assistant on your local machine:

### Prerequisites

- Python 3.7 or higher
- Virtual environment (optional but recommended)

### Steps

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd skywise

2. **set up virtual enviourment**
  
   ```bash
   python -m venv venv

   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

   ```
3. **Set Up Environment Variables**

    ***Rename  .env.example to .env file in the root directory and add your OpenAI API key and OpenWeather API key:***
   ```bash
    OPENAI_API_KEY=your_openai_api_key
    WEATHER_API_KEY=your_openweather_api_key
   ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**

   ```bash
   streamlit run app.py
   
6. **Access the Application**

  Open your web browser and go to http://localhost:8501 to interact with the SkyWise AI Weather Assistant.
 

## License
This project is licensed under the MIT License. See the LICENSE file for more details.