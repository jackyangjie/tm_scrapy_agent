"""Agent factory for creating different agent types.

This module provides factory functions to create various agent instances:
- SimpleAgent: For basic Q&A without complex reasoning
- ReActAgent: For complex multi-step reasoning tasks
- Custom configurations as needed
"""

import asyncio
import logging
import os
from typing import Optional

from agentscope.agent import ReActAgent
from agentscope.formatter import OpenAIChatFormatter
from agentscope.model import OpenAIChatModel
from agentscope.plan import PlanNotebook
from agentscope.tool import Toolkit
from agentscope.mcp import StdIOStatefulClient

from config import mcp_servers_config, scrapy_agent_sys_prompt
from .simple_agent import SimpleAgent
from .bounded_memory import BoundedMemory


SKILLS_DIR = os.path.join(os.path.dirname(__file__), "../skills")


async def create_react_agent(
    name: str = "react_agent",
    enable_tools: bool = True,
    max_iters: int = 90,
    max_tokens: Optional[int] = None,
    custom_prompt: Optional[str] = None,
    mcp_semaphore: Optional[asyncio.Semaphore] = None,
) -> ReActAgent:
    """Create a ReActAgent instance for complex reasoning tasks.

    Args:
        name: Agent name
        enable_tools: Whether to enable tools
        max_iters: Maximum iterations for reasoning
        max_tokens: Maximum context tokens
        custom_prompt: Optional custom system prompt
        mcp_semaphore: Semaphore for MCP client concurrency control

    Returns:
        Configured ReActAgent instance
    """
    logging.info(f"Creating ReActAgent '{name}'")

    # Initialize model
    model_name = os.getenv("model_name")
    model = OpenAIChatModel(
        model_name=model_name,
        api_key=os.getenv("api_key"),
        client_kwargs={"base_url": os.getenv("base_url")},
    )

    # Initialize toolkit
    toolkit = Toolkit()
    if enable_tools:
        # Register skills
        for skill_name in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, skill_name)
            if os.path.isdir(skill_path) and os.path.exists(
                os.path.join(skill_path, "SKILL.md")
            ):
                toolkit.register_agent_skill(skill_path)
                logging.info(f"Skill {skill_name} registered successfully")

        # Register MCP clients
        if mcp_semaphore:
            async with mcp_semaphore:
                for server_name, server_config in mcp_servers_config.items():
                    logging.info(f"Registering MCP server: {server_name}")
                    try:
                        client = StdIOStatefulClient(server_name, **server_config)
                        await client.connect()
                        await toolkit.register_mcp_client(client)
                        logging.info(f"MCP tool {server_name} registered successfully")
                    except Exception as e:
                        logging.warning(
                            f"MCP client {server_name} registration failed: {e}"
                        )

    # Configure memory
    max_tokens_config = max_tokens or int(os.getenv("MAX_CONTEXT_TOKENS", "150000"))
    memory = BoundedMemory(
        max_tokens=max_tokens_config, reserve_ratio=0.6, max_single_message_tokens=50000
    )
    logging.info(
        f"Initialized BoundedMemory - Max: {max_tokens_config}, "
        f"Effective: {int(max_tokens_config * 0.7)}"
    )

    # Create notebook for planning
    notebook = PlanNotebook()

    # Create agent
    agent = ReActAgent(
        name=name,
        sys_prompt=custom_prompt or scrapy_agent_sys_prompt,
        model=model,
        max_iters=max_iters,
        toolkit=toolkit,
        memory=memory,
        plan_notebook=notebook,
        formatter=OpenAIChatFormatter(),
    )

    logging.info(f"ReActAgent '{name}' created successfully")
    return agent


async def create_simple_agent(
    name: str = "simple_agent",
    enable_search: bool = True,
    custom_prompt: Optional[str] = None,
) -> SimpleAgent:
    """Create a SimpleAgent instance for basic Q&A tasks.

    Args:
        name: Agent name
        enable_search: Whether to enable search tools
        custom_prompt: Optional custom system prompt

    Returns:
        Configured SimpleAgent instance
    """
    logging.info(f"Creating SimpleAgent '{name}'")

    # Initialize model
    model_name = os.getenv("model_name")
    model = OpenAIChatModel(
        model_name=model_name,
        api_key=os.getenv("api_key"),
        client_kwargs={"base_url": os.getenv("base_url")},
    )

    # Initialize toolkit if search is enabled
    toolkit = None
    if enable_search:
        toolkit = Toolkit()

        # Register only search-related MCP servers
        for server_name, server_config in mcp_servers_config.items():
            if "search" in server_name.lower():
                try:
                    client = StdIOStatefulClient(server_name, **server_config)
                    await client.connect()
                    await toolkit.register_mcp_client(client)
                    logging.info(f"Registered search MCP: {server_name}")
                except Exception as e:
                    logging.warning(f"Failed to register {server_name}: {e}")

    # Create agent
    agent = SimpleAgent(
        name=name,
        model=model,
        toolkit=toolkit,
        sys_prompt=custom_prompt,
    )

    logging.info(f"SimpleAgent '{name}' created successfully")
    return agent


def get_agent_type(task_type: str) -> str:
    """Determine appropriate agent type based on task.

    Args:
        task_type: Description of the task

    Returns:
        'simple' for basic Q&A, 'react' for complex tasks
    """
    # Keywords that indicate need for complex reasoning
    complex_keywords = [
        "采集",
        "爬取",
        "搜索",
        "提取",
        "分析",
        "处理",
        "scrape",
        "crawl",
        "extract",
        "analyze",
        "process",
        "复杂",
        "多步",
        "工具",
        "tool",
    ]

    task_lower = task_type.lower()
    for keyword in complex_keywords:
        if keyword in task_lower:
            return "react"

    return "simple"
