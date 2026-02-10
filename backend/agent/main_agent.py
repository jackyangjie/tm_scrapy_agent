import asyncio
import logging
import os
from typing import Optional

from agentscope_runtime.engine.schemas.agent_schemas import (
    AgentRequest,
    FileContent,
    TextContent,
)
from agent.simple_agent import simple_agent_fucntion
from agent.scrapy_agent import scrapy_agent_fucntion
from config import mcp_servers_config, main_agent_sys_prompt
from agentscope.tool import Toolkit
from agentscope.formatter import OpenAIChatFormatter
from agentscope.mcp import StdIOStatefulClient
from agentscope_runtime.engine.app import AgentApp
from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel
from agentscope.plan import PlanNotebook
from .bounded_memory import BoundedMemory
from agentscope.pipeline import stream_printing_messages
from agentscope_runtime.engine.services.agent_state import (
    InMemoryStateService,
)

from agentscope_runtime.engine.services.session_history.session_history_service import (  # pylint: disable=line-too-long
    InMemorySessionHistoryService,  # pylint: disable=line-too-long
)

# Import file utilities and API handlers
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from util.file_util import process_file_content, process_messages
from api.file_api import UploadRequest, upload_file_handler, serve_file_handler

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "../skills")


agent_app = AgentApp(
    app_name="scrapy_agent",
    app_description="Scrapy agent for web scraping",
    app_version="1.0.0",
)


@agent_app.init
async def init_func(self):
    logging.info("初始化 scrapy_agent 应用...")
    self.state_service = InMemoryStateService()
    self.session_service = InMemorySessionHistoryService()

    await self.state_service.start()
    await self.session_service.start()

    # 初始化信号量，控制 MCP 客户端并发访问
    self.mcp_semaphore = asyncio.Semaphore(1)

    # 初始化 MCP 客户端（应用启动时一次性创建）
    self.mcp_clients: dict[str, StdIOStatefulClient] = {}
    await _init_mcp_clients(self.mcp_clients)

    # 初始化全局 Agent（复用以减少开销）
    await _init_agent(self)

    logging.info("初始化完成")


@agent_app.shutdown
async def shutdown_func(self):
    logging.info("关闭 scrapy_agent 应用...")
    await self.state_service.stop()
    for name, client in self.mcp_clients.items():
        if client.is_connected:
            logging.info(f"关闭 MCP 客户端: {name}")
            await client.close()
    self.mcp_clients.clear()
    await self.session_service.stop()
    self.agent = None
    logging.info("应用已关闭")


async def _init_agent(app_instance) -> None:
    """Initialize global ReActAgent instance."""
    toolkit = Toolkit()

    async with app_instance.mcp_semaphore:
        for name, client in app_instance.mcp_clients.items():
            logging.info(f"注册 MCP 客户端: {name}")
            try:
                await toolkit.register_mcp_client(client)
                logging.info(f"MCP 工具 {name} 注册成功")
            except Exception as e:
                logging.warning(f"MCP 客户端 {name} 注册失败: {e}")

    for skill_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        if os.path.isdir(skill_path) and os.path.exists(
            os.path.join(skill_path, "SKILL.md")
        ):
            toolkit.register_agent_skill(skill_path)
            logging.info(f"Skill {skill_name} 注册成功 !")

    notebook = PlanNotebook()
    model_name = os.getenv("model_name")
    logging.info(f"创建全局 ReActAgent - Model: {model_name}")

    max_tokens = int(os.getenv("MAX_CONTEXT_TOKENS", "150000"))
    memory = BoundedMemory(
        max_tokens=max_tokens, reserve_ratio=0.6, max_single_message_tokens=50000
    )
    logging.info(
        f"初始化 BoundedMemory - Max: {max_tokens}, Effective: {int(max_tokens * 0.7)}"
    )

    toolkit.register_tool_function(scrapy_agent_fucntion)

    app_instance.agent = ReActAgent(
        name="main_agent",
        sys_prompt=main_agent_sys_prompt,
        model=OpenAIChatModel(
            model_name=model_name,
            api_key=os.getenv("api_key"),
            client_kwargs={"base_url": os.getenv("base_url")},
        ),
        max_iters=90,
        toolkit=toolkit,
        memory=memory,
        # plan_notebook=notebook,
        formatter=OpenAIChatFormatter(),
    )


async def _init_mcp_clients(mcp_clients_dict: dict) -> None:
    """Initialize all MCP clients at application startup."""
    for name, config in mcp_servers_config.items():
        logging.info(f"初始化 MCP 服务器: {name}")
        try:
            client = StdIOStatefulClient(name, **config)
            await client.connect()
            mcp_clients_dict[name] = client
            logging.info(f"MCP 客户端 {name} 连接成功")
        except Exception as e:
            logging.error(f"MCP 客户端 {name} 连接失败: {e}", exc_info=True)


async def _load_agent_state(self, session_id: str, user_id: str) -> bool:
    """Load agent state from state service.

    Args:
        session_id: Session identifier
        user_id: User identifier

    Returns:
        True if state was loaded, False if no state existed
    """
    state = await self.state_service.export_state(
        session_id=session_id,
        user_id=user_id,
    )
    if state:
        logging.info(f"加载历史状态成功 - SessionID: {session_id}")
        self.agent.load_state_dict(state)
        logging.info(f"恢复 agent 状态 - SessionID: {session_id}")
        return True
    else:
        logging.info(f"无历史状态，创建新会话 - SessionID: {session_id}")
        return False


async def _save_agent_state(self, session_id: str, user_id: str) -> None:
    """Save current agent state to state service.

    Args:
        session_id: Session identifier
        user_id: User identifier
    """
    state = self.agent.state_dict()
    await self.state_service.save_state(
        user_id=user_id,
        session_id=session_id,
        state=state,
    )
    logging.info(f"保存状态成功 - SessionID: {session_id}")


@agent_app.endpoint("/files/{file_id}")
async def file_handler(file_id: str):
    """Serve uploaded files by file_id.

    Args:
        file_id: UUID of the uploaded file

    Yields:
        File content with appropriate Content-Type header
        or 404 error if file not found
    """
    result = await serve_file_handler(file_id)
    if "status" in result and result["status"] != 200:
        yield {"error": result.get("error"), "status": result.get("status")}
    else:
        yield result


@agent_app.endpoint("/upload")
async def upload_handler(body: UploadRequest):
    """Handle file upload from base64-encoded data.

    Args:
        body: Request body containing 'filename' and 'file_data' (base64 or data URL)

    Yields:
        dict with file_id, file_url, filename, size on success
        dict with error and status on failure
    """
    result = await upload_file_handler(body)
    if "status" in result and result["status"] != 200:
        yield {"error": result.get("error"), "status": result.get("status")}
    else:
        yield result


@agent_app.query(framework="agentscope")
async def query_func(
    self,
    msgs,
    request: AgentRequest = None,
    **kwargs,
):
    """Handle query requests for the agent.

    Args:
        msgs: Messages to process
        request: Agent request containing session and user info
        **kwargs: Additional keyword arguments

    Yields:
        Tuple of (message, is_last) from agent execution
    """
    assert kwargs is not None, "kwargs is Required for query_func"
    session_id = request.session_id
    user_id = request.user_id

    logging.info(f"收到查询请求 - SessionID: {session_id}, UserID: {user_id}")

    await _load_agent_state(self, session_id, user_id)

    msgs = process_messages(msgs, session_id)

    logging.info(f"开始执行 agent 任务 - SessionID: {session_id}")
    try:
        async for msg, last in stream_printing_messages(
            agents=[self.agent],
            coroutine_task=self.agent(msgs),
        ):
            yield msg, last
        logging.info(f"agent 任务执行完成 - SessionID: {session_id}")
    except Exception as e:
        logging.error(
            f"agent 任务执行失败 - SessionID: {session_id}, Error: {e}", exc_info=True
        )
        raise

    await _save_agent_state(self, session_id, user_id)

    logging.info(f"查询请求处理完成 - SessionID: {session_id}")
