# To use this script, you need Ollama running locally.
# 1. Install Ollama: https://ollama.com/download
# 2. Pull a model, e.g.: ollama pull llama3
# 3. Start Ollama (it runs as a background service by default)
# This script uses LangChain's Ollama integration for a free, local LLM.

# Requires: pip install -U langchain-ollama
from langchain_ollama import OllamaLLM
import argparse
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
import json
import re
import ast
from typing import Any, Dict, List, Optional

# Use a free local LLM via Ollama (e.g., llama3)
llm = OllamaLLM(model="llama3.2")

def build_tools_prompt(tools: List[Any], user_input: str) -> str:
    """
    Build a prompt for the LLM that describes all available tools and their arguments.
    """
    tool_descriptions = []
    for tool in tools:
        args_schema = tool.inputSchema
        required_args = args_schema.get('required', [])
        arg_descriptions = []
        for arg in required_args:
            prop = args_schema['properties'][arg]
            arg_title = prop.get('title', arg)
            arg_type = prop.get('type', 'string')
            arg_descriptions.append(f"'{arg}' (type: {arg_type}, description: {arg_title})")
        arg_desc_str = ', '.join(arg_descriptions) if arg_descriptions else 'no arguments'
        tool_descriptions.append(f"Tool: '{tool.name}' - {tool.description}. Required arguments: {arg_desc_str}.")
    tools_str = '\n'.join(tool_descriptions)
    example_json = '{"use_tool": true, "tool_name": "<tool_name>", "arguments": {"arg1": "value1", ...}}'
    prompt = (
        f"You are a helpful AI assistant. You have access to the following tools:\n{tools_str}\n"
        f"User input: '{user_input}'\n"
        f"If the user's input can be answered by using one of the tools, reply with ONLY a JSON object in this format: {example_json}.\n"
        f"If you choose not to use any tool, reply with your normal answer (not JSON), and do not mention the tools.\n"
        f"Examples:\n"
        f"User input: 'how is the weather in Berlin?'\n"
        f'{{"use_tool": true, "tool_name": "Get Weather Forecast", "arguments": {{"city": "Berlin"}}}}\n'
        f"User input: 'tell me a joke'\n"
        f"Why did the scarecrow win an award? Because he was outstanding in his field!\n"
    )
    return prompt

def repair_llm_response(resp: str) -> str:
    """Attempt to repair malformed JSON from the LLM."""
    # Remove trailing unmatched braces
    while resp.count('{') < resp.count('}'):
        resp = resp.rstrip('}')
    # Replace single-quoted keys/values with double quotes
    resp = re.sub(r"(?<=[:{,])\s*'([^']+)'\s*:", r'"\1":', resp)
    resp = re.sub(r":\s*'([^']+)'", r': "\1"', resp)
    resp = resp.replace("True", "true").replace("False", "false")
    return resp

def parse_llm_response(resp: str) -> Optional[Dict[str, Any]]:
    """Parse the LLM's response, returning a dict if it's valid JSON, else None."""
    try:
        norm_response = repair_llm_response(resp)
        return json.loads(norm_response)
    except Exception:
        try:
            return ast.literal_eval(resp)
        except Exception:
            return None

def get_tool_by_name(tools: List[Any], name: str) -> Optional[Any]:
    for tool in tools:
        if tool.name == name:
            return tool
    return None

def get_user_input() -> str:
    return input("You: ")

async def interact_with_server(session: ClientSession) -> None:
    """Main interaction loop: gets user input, queries LLM, calls tools if needed."""
    tools_response = await session.list_tools()
    tools = tools_response.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])
    print("Type 'exit' or 'quit' to end the chat.\n")
    while True:
        user_input = get_user_input()
        if user_input.strip().lower() in ("exit", "quit"):
            print("Exiting chat.")
            break
        llm_prompt = build_tools_prompt(tools, user_input)
        llm_response = llm.invoke(llm_prompt)
        llm_decision = parse_llm_response(llm_response)
        if isinstance(llm_decision, dict) and llm_decision.get('use_tool'):
            tool_name = llm_decision.get('tool_name')
            arguments = llm_decision.get('arguments', {})
            tool_obj = get_tool_by_name(tools, tool_name)
            if not tool_obj:
                print(f"Tool '{tool_name}' not found.")
                continue
            try:
                result = await session.call_tool(tool_name, arguments=arguments)
            except Exception as e:
                print(f"Error calling tool '{tool_name}': {e}")
                continue
            # Prepare a prompt for the LLM to summarize the tool result
            if hasattr(result, 'model_dump'):
                result_data = result.model_dump()
            elif hasattr(result, 'dict'):
                result_data = result.dict()
            else:
                result_data = vars(result)
            summary_prompt = (
                f"You are a helpful assistant. Here is the result of the tool '{tool_name}':\n"
                f"{json.dumps(result_data, ensure_ascii=False, indent=2)}\n"
                "Please summarize this information in a friendly, concise way for the user."
            )
            summary = llm.invoke(summary_prompt)
            print(summary.strip())
        else:
            print(llm_decision.get('message', llm_response) if isinstance(llm_decision, dict) else llm_response)

async def run_with_stdio(server_cmd: str) -> None:
    params = StdioServerParameters(command="python", args=[server_cmd])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await interact_with_server(session)

async def run_with_http(server_url: str) -> None:
    async with streamablehttp_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await interact_with_server(session)

def main() -> None:
    parser = argparse.ArgumentParser(description="MCP-LangChain Client Example (Ollama)")
    parser.add_argument("--server-cmd", type=str, help="Path to MCP server script (for stdio mode)")
    parser.add_argument("--server-url", type=str, help="URL of remote MCP server (for HTTP mode)")
    args = parser.parse_args()
    if args.server_cmd:
        asyncio.run(run_with_stdio(args.server_cmd))
    elif args.server_url:
        asyncio.run(run_with_http(args.server_url))
    else:
        print("Please specify either --server-cmd or --server-url.")

if __name__ == "__main__":
    main() 