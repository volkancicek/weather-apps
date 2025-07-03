# MCP Client & Weather Server Example

This example demonstrates how to use the MCP Python SDK to build an MCP client that connects to a local MCP server and integrates with LLMs via [LangChain](https://python.langchain.com/). The included server exposes a weather forecast tool using the free Open-Meteo API (no API key required). The client uses a free, local LLM via Ollama.

## Features
- **Weather MCP Server**: Exposes a tool to get weather forecasts for any city.
- **Client**: Connects to the MCP server, lists tools, and uses a local LLM (Ollama) to select and call the weather tool.
- **No paid APIs required**: All components are free and run locally (except for the weather API call).

## Prerequisites
- Python 3.10+
- MCP Python SDK (`mcp[cli]`)
- LangChain (`langchain`, `langchain-community`)
- [Ollama](https://ollama.com/) (for local LLM)
- (Optional) `requests` (auto-installed by the server)

## Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

## Setting up Ollama (for the LLM)
1. Download and install Ollama: https://ollama.com/download
2. Pull a model (e.g. llama3):
   ```bash
   ollama pull llama3
   ```
3. Make sure Ollama is running (it runs as a background service by default).

## Running the Weather MCP Server
From the `ollama` directory:
```bash
python src/weather_server.py
```
This will start an MCP server exposing a `get_weather` tool.

## Using the MCP Client
In a separate terminal, run:
```bash
python src/client.py --server-cmd src/weather_server.py
```
- The client will connect to the local MCP server, list available tools, and use the local LLM to select and call the weather tool.
- You can modify the client to prompt for a city name or pass arguments as needed.

## Example: How it works
- The server exposes a tool: `get_weather(city: str)`
- The client lists tools, asks the LLM which tool to use, and calls it (by default, with empty arguments; you can extend this to prompt for a city).
- The weather tool uses the Open-Meteo API to fetch the forecast for the given city.

## Extending
- Modify the client to prompt the user for a city name and pass it to the weather tool.
- Add more tools to the server as needed.
- Swap out the LLM for any other LangChain-supported local model.

## References
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [LangChain Python](https://python.langchain.com/)
- [Ollama](https://ollama.com/)
- [Open-Meteo API](https://open-meteo.com/)

---

**This is a template. See `src/weather_server.py` and `src/client.py` for working examples.** 