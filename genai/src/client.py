import os
import sys
import logging
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
MODEL_NAME = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
WEATHER_API_URL = os.getenv('WEATHER_API_URL', 'http://localhost:8080/api/v1/getWeather')

genai.configure(api_key=GEMINI_API_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Define the weather tool
get_weather_func = {
    "name": "getWeather",
    "description": "Get the weather forecast for a location",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "location": {
                "type": "STRING",
                "description": "The location to get the weather for",
            }
        },
        "required": ["location"],
    },
}

def get_weather(location: str) -> Optional[Dict[str, Any]]:
    """Call the weather API and return the weather data."""
    try:
        response = requests.post(
            WEATHER_API_URL,
            json={"location": location},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error calling weather server: {e}")
        return None

def handle_llm_response(response: Any) -> Optional[Dict[str, Any]]:
    """Check for function call in LLM response and return function call details if present."""
    try:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call is not None:
                return part.function_call
    except Exception as e:
        logging.error(f"Error parsing LLM response: {e}")
    return None

def print_llm_text(response: Any) -> bool:
    """Print the text part of the LLM response."""
    printed = False
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'text') and part.text.strip():
            print(part.text)
            printed = True
    return printed

def main() -> None:
    """Main loop for user interaction with the LLM and weather API."""
    system_instruction = "You are a helpful assistant. Always reply to the user in natural language after using a tool."
    model = genai.GenerativeModel(
        MODEL_NAME,
        tools=[get_weather_func],
        system_instruction=system_instruction,
    )
    history: List[Dict[str, Any]] = []
    print("Type 'exit' or 'quit' to end the session.")
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        history.append({"role": "user", "parts": [user_input]})
        response = model.generate_content(history, stream=False)
        function_call = handle_llm_response(response)
        if function_call and function_call.name == "getWeather":
            location = function_call.args["location"]
            weather_data = get_weather(location)
            if weather_data is not None:
                logging.info(f"Weather API called. Response: {weather_data}")
                history.append({
                    "role": "tool",
                    "parts": [{
                        "function_response": {
                            "name": "getWeather",
                            "response": weather_data
                        }
                    }]
                })
                response = model.generate_content(history, stream=False)
            else:
                print("Failed to get weather data.")
                continue
        if not print_llm_text(response):
            logging.warning("No text response from LLM.")
            # Fallback: print weather data if available in last tool call
            if function_call and function_call.name == "getWeather" and weather_data is not None:
                print(f"Weather in {location}: {weather_data.get('forecast', '')}, {weather_data.get('temperature', '')}")
        # Add model response to history
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text.strip():
                history.append({"role": "model", "parts": [part.text]})

if __name__ == "__main__":
    main()
