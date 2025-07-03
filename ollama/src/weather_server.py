# MCP Weather Server Example
# This server exposes a weather forecast tool using the Open-Meteo API (no API key required)
# Usage: python weather_server.py

from mcp.server.fastmcp import FastMCP
import requests
from typing import Dict, Any

mcp = FastMCP("WeatherServer", dependencies=["requests"])

@mcp.tool(title="Get Weather Forecast", description="Get the weather forecast for a city (powered by Open-Meteo)")
def get_weather(city: str) -> Dict[str, Any]:
    """
    Get the weather forecast for a city using the Open-Meteo API.
    Args:
        city: Name of the city (e.g., 'London')
    Returns:
        A dictionary with the forecast or an error message.
    """
    # Geocoding to get latitude/longitude
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_resp = requests.get(geo_url, timeout=10)
    geo_data = geo_resp.json()
    if not geo_data.get("results"):
        return {"error": f"City '{city}' not found."}
    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]
    # Get weather forecast (current and next 24h hourly)
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current_weather=true&hourly=temperature_2m,precipitation,weathercode&forecast_days=1"
    )
    weather_resp = requests.get(weather_url, timeout=10)
    weather_data = weather_resp.json()
    # Format a simple summary
    current = weather_data.get("current_weather", {})
    summary = {
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "current": current,
        "hourly": weather_data.get("hourly", {})
    }
    return summary

if __name__ == "__main__":
    mcp.run() 