# MCP Example

This project demonstrates a simple MCP (Model-Context-Provider) implementation for weather information retrieval using a client-server architecture and Google Gemini LLM integration.

## Overview

- **Server (`weather_server.py`)**: Provides a REST API endpoint to fetch real-time weather data for a given location using the OpenWeatherMap API.
- **Client (`client.py`)**: Interacts with the user, leverages Google Gemini LLM to interpret queries, and calls the weather server as a tool when weather information is requested.

---

## How It Works

1. **User Input**: The user types a question or request about the weather (e.g., "What's the weather in Paris?").
2. **LLM Processing**: The client uses Gemini LLM to interpret the request. If weather data is needed, the LLM triggers a function call to fetch weather information.
3. **Weather API Call**: The client calls the local weather server, which in turn queries the OpenWeatherMap API for the requested location.
4. **Response**: The weather data is returned to the client, which then uses the LLM to generate a natural language response for the user.

---

## File Structure

- `src/weather_server.py`: Flask server providing `/api/v1/getWeather` endpoint.
- `src/client.py`: Command-line client using Gemini LLM and calling the weather server as a tool.
- `requirements.txt`: Python dependencies.

---

## Setup & Running

### 1. Clone the Repository

```
git clone <this-repo-url>
cd weather-apps/genai
```

### 2. Install Dependencies

It's recommended to use a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the `src/` directory with the following content:

```
# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Weather Server
WEATHER_API_URL=http://localhost:8080/api/v1/getWeather

# OpenWeatherMap API (for the server)
OPENWEATHER_API_KEY=your-openweathermap-api-key
```

- Get a [Google Gemini API key](https://aistudio.google.com/app/apikey) and an [OpenWeatherMap API key](https://openweathermap.org/api).

### 4. Run the Weather Server

```
cd src
python weather_server.py
```

The server will start on `http://localhost:8080` by default.

### 5. Run the Client

In a new terminal (with the virtual environment activated and `.env` present):

```
cd src
python client.py
```

Type your weather questions at the prompt. Type `exit` or `quit` to stop.

---

## Notes

- The client uses Google Gemini LLM to interpret user queries and decide when to call the weather API.
- The server fetches real weather data from OpenWeatherMap and returns it in a simple JSON format.
- Both client and server require their respective API keys set in the `.env` file.

---

## License

MIT License 