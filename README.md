# weather-apps

Demonstrates simple MCP (Model-Context-Provider) implementations for weather information retrieval using a client-server architecture and LLM integrations.

---

## Projects Overview

This repository contains two example projects, each demonstrating a different approach to integrating LLMs and weather APIs using the MCP pattern:

- [`genai/`](./genai): Uses Google Gemini LLM and OpenWeatherMap API.
- [`ollama/`](./ollama): Uses a local LLM via Ollama and the Open-Meteo API.

---

## Project Details

### 1. `genai/` — Gemini LLM + OpenWeatherMap
- **Server:** Flask REST API (`src/weather_server.py`) provides `/api/v1/getWeather` endpoint, fetching real-time weather from OpenWeatherMap.
- **Client:** Command-line tool (`src/client.py`) uses Google Gemini LLM to interpret user queries and call the weather server as a tool.
- **LLM:** Google Gemini (API key required).
- **Weather API:** OpenWeatherMap (API key required).
- **Setup:**
  - Install Python dependencies from `requirements.txt`.
  - Set up a `.env` file with Gemini and OpenWeatherMap API keys.
  - Start the server, then run the client.
- **See [`genai/README.md`](./genai/README.md) for full setup and usage.**

### 2. `ollama/` — Local LLM (Ollama) + Open-Meteo
- **Server:** Python MCP server (`src/weather_server.py`) exposes a weather tool using the free Open-Meteo API (no API key required).
- **Client:** Command-line tool (`src/client.py`) uses a local LLM via Ollama (LangChain integration) to select and call the weather tool.
- **LLM:** Local LLM via Ollama (e.g., llama3, runs on your machine).
- **Weather API:** Open-Meteo (no API key required).
- **Setup:**
  - Install Python dependencies from `requirements.txt`.
  - Install and run Ollama, pull a model (e.g., `ollama pull llama3`).
  - Start the server, then run the client.
- **See [`ollama/README.md`](./ollama/README.md) for full setup and usage.**

---

## Comparison

| Feature         | genai                | ollama                |
|----------------|----------------------|-----------------------|
| LLM            | Google Gemini (cloud)| Local (Ollama, e.g. llama3) |
| Weather Source | OpenWeatherMap (API key) | Open-Meteo (free)    |
| API Keys       | Required             | Not required (for weather) |
| Runs Locally   | Partially (LLM is cloud) | Fully local (LLM & server) |
| Client-Server  | Yes                  | Yes                   |

---

## Getting Started

- Choose a subproject based on your requirements (cloud vs. local, API key needs, etc.).
- Follow the setup instructions in the respective subproject's README.

For more details, see [`genai/README.md`](./genai/README.md) and [`ollama/README.md`](./ollama/README.md).
