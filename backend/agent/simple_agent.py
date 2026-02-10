"""SimpleAgent for basic Q&A functionality.

This module provides a simple conversational agent that:
- Answers basic questions without complex reasoning
- Can optionally use search tools for information retrieval
- Maintains conversation context
- Suitable for general Q&A tasks
"""

import logging
import os
from typing import Optional

from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel
from agentscope.formatter import OpenAIChatFormatter
from agentscope.tool import Toolkit, ToolResponse
from agentscope.mcp import StdIOStatefulClient

from config import mcp_servers_config, simple_agent_sys_prompt


SKILLS_DIR = os.path.join(os.path.dirname(__file__), "../skills")


async def simple_agent_fucntion(
    custom_prompt: str, name: str = "simple_agent", enable_search: bool = True
) -> ToolResponse:
    """
    Create a simple agent for basic Q&A functionality.

    Args:
        custom_prompt (str): Custom prompt for the agent.
        name (str, optional): Name of the agent. Defaults to "simple_agent".
        enable_search (bool, optional): Whether to enable search tools. Defaults to True.

    Returns:
        ToolResponse: Response from the agent.
    """
    # Initialize model
    model_name = os.getenv("model_name")
    logging.info(f"Creating SimpleAgent '{name}' with model: {model_name}")

    chat_model = OpenAIChatModel(
        model_name=model_name,
        api_key=os.getenv("api_key"),
        client_kwargs={"base_url": os.getenv("base_url")},
    )

    # Initialize toolkit if search is enabled
    toolkit = None
    mcp_clients = []
    if enable_search:
        toolkit = Toolkit()

        # Register MCP clients for search tools
        for server_name, server_config in mcp_servers_config.items():
            # Only register search-related MCP servers
            if "search" in server_name.lower():
                try:
                    client = StdIOStatefulClient(server_name, **server_config)
                    await client.connect()
                    await toolkit.register_mcp_client(client)
                    mcp_clients.append(client)
                    logging.info(f"Registered search MCP: {server_name}")
                except Exception as e:
                    logging.warning(f"Failed to register {server_name}: {e}")

    try:
        # Create agent
        simple_agent = ReActAgent(
            name="scrapy_agent",
            sys_prompt=simple_agent_sys_prompt,
            model=chat_model,
            max_iters=90,
            toolkit=toolkit,
            formatter=OpenAIChatFormatter(),
        )
        res = await simple_agent(Msg("user", custom_prompt, "user"))

        logging.info(f"SimpleAgent '{name}' created successfully")
        return ToolResponse(content=res.get_content_blocks("text"))
    finally:
        # Clean up MCP clients
        for client in mcp_clients:
            try:
                if client.is_connected:
                    await client.close()
                    logging.info(f"Closed MCP client: {client.name}")
            except Exception as e:
                logging.warning(f"Error closing MCP client: {e}")
