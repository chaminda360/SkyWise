import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

class CityExtractor:
    @staticmethod
    def extract_cities_from_input(input_text):
        """Use OpenAI to extract city names from the input."""
        refine_prompt = (
            f"Extract all city names from the following input: '{input_text}'. "
            "Return the city names as a comma-separated list."
        )

        refine_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts city names."},
                {"role": "user", "content": refine_prompt},
            ],
        )

        city_list = refine_response.choices[0].message.content.strip().split(", ")
        return city_list
