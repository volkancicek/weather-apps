from flask import Flask, request, jsonify
from typing import Dict, Any
import os
import requests

app = Flask(__name__)

@app.route('/api/v1/getWeather', methods=['POST'])
def get_weather() -> Any:
    """Endpoint to get weather for a given location."""
    data: Dict[str, Any] = request.get_json(force=True, silent=True) or {}
    location = data.get('location')
    if not location:
        return jsonify({"error": "Missing location"}), 400
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        return jsonify({"error": "Missing OpenWeatherMap API key in environment variable 'OPENWEATHER_API_KEY'"}), 500
    try:
        # Call OpenWeatherMap API for current weather by city name
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return jsonify({"error": f"Weather API error: {resp.status_code}", "details": resp.json()}), 502
        weather_json = resp.json()
        weather_data = {
            "location": weather_json.get("name", location),
            "forecast": weather_json["weather"][0]["description"] if weather_json.get("weather") else "N/A",
            "temperature": f"{weather_json['main']['temp']}°C" if weather_json.get("main") else "N/A",
            "humidity": weather_json['main'].get('humidity', 'N/A') if weather_json.get("main") else "N/A",
            "wind_speed": weather_json['wind'].get('speed', 'N/A') if weather_json.get("wind") else "N/A",
        }
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({"error": "Failed to fetch weather data", "details": str(e)}), 500

def main() -> None:
    """Run the Flask weather server."""
    port = int(os.getenv('PORT', 8080))
    print(f"Weather server listening on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()
