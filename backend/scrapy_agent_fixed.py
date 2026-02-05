"""
修复后的 query_func - 支持客户端断开检测

将此代码替换 backend/agent/scrapy_agent.py 中的 query_func 函数
"""


async def query_func_fixed(
    self,
    msgs,
    request: AgentRequest = None,
    **kwargs,
):
    """Handle query requests for the agent with client disconnect detection.

    Args:
        msgs: Messages to process
        request: Agent request containing session and user info
        **kwargs: Additional keyword arguments (may contain raw_request for disconnect check)

    Yields:
        Tuple of (message, is_last) from agent execution
    """
    assert kwargs is not None, "kwargs is Required for query_func"
    session_id = request.session_id
    user_id = request.user_id

    # ✅ 获取原始 FastAPI Request 对象（用于断开检测）
    raw_request = kwargs.get("raw_request")  # 需要在调用时传入

    logging.info(f"收到查询请求 - SessionID: {session_id}, UserID: {user_id}")

    await _load_agent_state(self, session_id, user_id)

    msgs = _process_messages(msgs, session_id)

    logging.info(f"开始执行 agent 任务 - SessionID: {session_id}")

    try:
        # ✅ 创建 agent 任务但不直接执行
        agent_task = self.agent(msgs)

        # ✅ 使用 stream_printing_messages 但添加断开检测
        async for msg, last in stream_printing_messages(
            agents=[self.agent],
            coroutine_task=agent_task,
        ):
            # ✅ 每次yield前检查客户端是否断开
            if raw_request and hasattr(raw_request, "is_disconnected"):
                is_disconnected = await raw_request.is_disconnected()
                if is_disconnected:
                    logging.warning(f"客户端已断开 - SessionID: {session_id}")
                    # ✅ 取消 agent 任务
                    agent_task.close()
                    break

            yield msg, last

        logging.info(f"agent 任务执行完成 - SessionID: {session_id}")

    except asyncio.CancelledError:
        logging.warning(f"Agent 任务被取消 - SessionID: {session_id}")
        # ✅ 清理并退出
        raise
    except Exception as e:
        logging.error(
            f"agent 任务执行失败 - SessionID: {session_id}, Error: {e}", exc_info=True
        )
        raise

    await _save_agent_state(self, session_id, user_id)

    logging.info(f"查询请求处理完成 - SessionID: {session_id}")
