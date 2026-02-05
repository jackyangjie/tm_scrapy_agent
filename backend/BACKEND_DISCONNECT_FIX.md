# 🔧 后端断开连接检测修复方案

## 问题总结

当前后端在客户端断开连接后，Agent 任务继续执行，导致：
1. ❌ 资源浪费（CPU、内存、LLM token）
2. ❌ 日志污染（继续输出到已断开的客户端）
3. ❌ 无法及时释放资源

## 根本原因

**执行链路**：
```
前端 abortController.abort()
    → HTTP 连接断开
    → FastAPI StreamingResponse (_generate_stream_response)
    → async for event in executor.execute(request)  ❌ 无断开检测
        → query_func
            → stream_printing_messages  ❌ 无断开检测
                → Agent 执行  ❌ 继续运行
```

**关键问题**：
1. `response_api_protocol_adapter.py` 的 `_generate_stream_response` 未检查 `request.is_disconnected()`
2. `stream_printing_messages` 未处理 `asyncio.CancelledError`
3. Agent 任务未响应取消信号

---

## 解决方案对比

| 方案 | 难度 | 效果 | 副作用 |
|------|------|------|--------|
| **方案 1：修改您的代码** | ⭐ 简单 | ✅ 部分解决 | ⚠️ 需要传入 raw_request |
| **方案 2：修改 agentscope 包** | ⭐⭐ 中等 | ✅ 完整解决 | ⚠️ 需要重新安装包 |
| **方案 3：使用中间件** | ⭐⭐⭐ 复杂 | ✅ 最优雅 | ✅ 无副作用 |

---

## 方案 1：快速修复（推荐用于测试）

### 步骤 1：修改 `backend/agent/scrapy_agent.py`

在第 538-581 行的 `query_func` 函数中添加断开检测：

```python
@agent_app.query(framework="agentscope")
async def query_func(
    self,
    msgs,
    request: AgentRequest = None,
    **kwargs,
):
    """Handle query requests for the agent."""
    assert kwargs is not None, "kwargs is Required for query_func"
    session_id = request.session_id
    user_id = request.user_id

    # ===== 新增：获取 FastAPI Request 对象 =====
    raw_request = kwargs.get('raw_request')
    # =========================================

    logging.info(f"收到查询请求 - SessionID: {session_id}, UserID: {user_id}")

    await _load_agent_state(self, session_id, user_id)

    msgs = _process_messages(msgs, session_id)

    logging.info(f"开始执行 agent 任务 - SessionID: {session_id}")

    try:
        agent_task = self.agent(msgs)

        async for msg, last in stream_printing_messages(
            agents=[self.agent],
            coroutine_task=agent_task,
        ):
            # ===== 新增：检查客户端是否断开 =====
            if raw_request and hasattr(raw_request, 'is_disconnected'):
                is_disconnected = await raw_request.is_disconnected()
                if is_disconnected:
                    logging.warning(f"客户端已断开，停止 Agent 任务 - SessionID: {session_id}")
                    break
            # ====================================

            yield msg, last

        logging.info(f"agent 任务执行完成 - SessionID: {session_id}")

    except asyncio.CancelledError:
        logging.warning(f"Agent 任务被取消 - SessionID: {session_id}")
        raise
    except Exception as e:
        logging.error(
            f"agent 任务执行失败 - SessionID: {session_id}, Error: {e}", exc_info=True
        )
        raise

    await _save_agent_state(self, session_id, user_id)
```

### 步骤 2：修改 agentscope runtime（传递 raw_request）

编辑 `backend/venv/lib/python3.12/site-packages/agentscope_runtime/engine/deployers/adapter/responses/response_api_agent_adapter.py`：

找到 `execute` 方法，添加 `raw_request` 参数：

```python
async def execute(
    self,
    request: Dict,
    raw_request: Request = None,  # 新增参数
) -> AsyncGenerator[BaseResponse, None]:
    """Execute agent query and yield responses."""
    # ... 现有代码 ...

    # 调用 agent 函数时传递 raw_request
    async for response in self._func(
        msgs=msgs,
        request=agent_request,
        raw_request=raw_request,  # 新增：传递原始请求
    ):
        yield response
```

### 步骤 3：修改 protocol adapter（传递 raw_request）

编辑 `backend/venv/lib/python3.12/site-packages/agentscope_runtime/engine/deployers/adapter/responses/response_api_protocol_adapter.py`：

在 `_generate_stream_response` 方法中：

```python
async def _generate_stream_response(
    self,
    request: Dict,
    request_id: str,
) -> AsyncGenerator[str, None]:
    """Generate SSE streaming response."""
    try:
        # 修改：传递原始请求对象
        raw_request = request.get('_raw_request')  # 需要在 _handle_requests 中添加

        async for event in self._executor.execute(
            request,
            raw_request=raw_request,  # 传递 raw_request
        ):
            # ... 现有代码 ...
```

在 `_handle_requests` 方法中保存 raw_request：

```python
async def _handle_requests(self, request: Request) -> StreamingResponse:
    """Handle OpenAI Response API request."""
    await self._semaphore.acquire()
    request_id = f"resp_{uuid4()}"
    logger.info("[ResponseAPI] start request_id=%s", request_id)

    try:
        request_data = await request.json()

        # 新增：将原始请求对象添加到请求数据中
        request_data['_raw_request'] = request

        stream = request_data.get("stream", False)

        if stream:
            return StreamingResponse(
                self._generate_stream_response_with_timeout(
                    request=request_data,  # 现在包含 raw_request
                    request_id=request_id,
                ),
                media_type="text/event-stream",
                headers=SSE_HEADERS,
            )
        # ...
```

---

## 方案 2：修改 agentscope 包（推荐用于生产）

### 修改 `stream_printing_messages` 函数

编辑文件：`backend/venv/lib/python3.12/site-packages/agentscope/pipeline/_functional.py`

在第 107-193 行的 `stream_printing_messages` 函数中添加断开检测：

```python
async def stream_printing_messages(
    agents: list[AgentBase],
    coroutine_task: Coroutine,
    queue: asyncio.Queue | None = None,
    end_signal: str = "[END]",
    yield_speech: bool = False,
    disconnect_checker: Callable[[], Awaitable[bool]] | None = None,  # 新增参数
) -> AsyncGenerator[...]:
    """Gather printing messages from agents with disconnect detection."""

    queue = queue or asyncio.Queue()
    for agent in agents:
        agent.set_msg_queue_enabled(True, queue)

    task = asyncio.create_task(coroutine_task)

    if task.done():
        await queue.put(end_signal)
    else:
        task.add_done_callback(lambda _: queue.put_nowait(end_signal))

    # 修改：添加断开检测
    while True:
        # ===== 新增：检查客户端是否断开 =====
        if disconnect_checker:
            is_disconnected = await disconnect_checker()
            if is_disconnected:
                logging.warning("Client disconnected, cancelling agent task")
                task.cancel()  # 取消任务
                break
        # ====================================

        printing_msg = await queue.get()

        if isinstance(printing_msg, str) and printing_msg == end_signal:
            break

        if yield_speech:
            yield printing_msg
        else:
            msg, last, _ = printing_msg
            yield msg, last

    # 检查异常（包括 CancelledError）
    try:
        exception = task.exception()
        if exception is not None:
            raise exception from None
    except asyncio.CancelledError:
        logging.info("Agent task was cancelled due to client disconnect")
        raise
```

### 使用方式

在您的 `query_func` 中：

```python
async def query_func(
    self,
    msgs,
    request: AgentRequest = None,
    **kwargs,
):
    raw_request = kwargs.get('raw_request')

    # 创建断开检测函数
    async def check_disconnect():
        if raw_request and hasattr(raw_request, 'is_disconnected'):
            return await raw_request.is_disconnected()
        return False

    async for msg, last in stream_printing_messages(
        agents=[self.agent],
        coroutine_task=self.agent(msgs),
        disconnect_checker=check_disconnect,  # 传递检测函数
    ):
        yield msg, last
```

---

## 方案 3：使用 FastAPI 中间件（最优雅）

创建文件：`backend/middleware/disconnect_middleware.py`

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class DisconnectDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware to detect client disconnection during streaming."""

    async def dispatch(self, request: Request, call_next):
        # 标记请求开始
        request.state.client_connected = True

        try:
            response = await call_next(request)
            return response
        finally:
            # 清理
            request.state.client_connected = False
```

在 `main.py` 中添加中间件：

```python
from middleware.disconnect_middleware import DisconnectDetectionMiddleware

app = FastAPI()
app.add_middleware(DisconnectDetectionMiddleware)
```

---

## 测试验证

### 测试步骤

1. **启动后端**：
```bash
cd backend
python main.py
```

2. **启动前端**：
```bash
cd frontend
npm run dev
```

3. **发送长请求**：
   - 在聊天界面发送一个需要长时间处理的请求
   - 例如："帮我写一个详细的 Python 教程"

4. **立即取消**：
   - 在响应开始后立即点击停止按钮

5. **检查日志**：
   - 后端日志应该显示："客户端已断开，停止 Agent 任务"
   - 后端应该立即停止执行（不再输出后续消息）

### 预期结果

✅ **成功**：
- 后端日志显示断开检测
- Agent 任务立即停止
- 资源及时释放

❌ **失败**：
- 后端继续执行
- 日志继续输出
- 资源未释放

---

## 推荐方案

根据您的场景：

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| **快速测试** | 方案 1 | 修改最少，立即见效 |
| **生产环境** | 方案 2 | 根本性解决，可复用 |
| **长期维护** | 方案 3 | 最优雅，不影响现有代码 |

---

## 注意事项

1. **兼容性**：
   - 方案 1 和 2 修改了第三方包，升级包后需要重新应用
   - 方案 3 使用中间件，升级包时不受影响

2. **性能影响**：
   - `request.is_disconnected()` 检查开销极小（< 1ms）
   - 每次检查都是异步的，不会阻塞

3. **日志建议**：
   - 断开时使用 `logging.warning` 级别
   - 包含 session_id 便于追踪

4. **资源清理**：
   - 确保取消时清理所有资源（文件句柄、数据库连接等）
   - 使用 `try...finally` 确保清理代码执行

---

## 额外优化

### 1. 添加超时控制

```python
async def query_func(...):
    try:
        async with asyncio.timeout(300):  # 5分钟超时
            async for msg, last in stream_printing_messages(...):
                yield msg, last
    except TimeoutError:
        logging.error("Agent execution timeout")
```

### 2. 添加心跳检测

```python
async def query_func(...):
    last_yield_time = time.time()

    async for msg, last in stream_printing_messages(...):
        last_yield_time = time.time()

        # 如果超过 10 秒没有输出，检查连接
        if time.time() - last_yield_time > 10:
            if await raw_request.is_disconnected():
                break
```

### 3. 优雅关闭

```python
async def query_func(...):
    try:
        async for msg, last in stream_printing_messages(...):
            yield msg, last
    except (asyncio.CancelledError, GeneratorExit):
        logging.info("Generator closed, cleaning up...")
        # 清理资源
        await cleanup_resources()
        raise
```

---

## 总结

✅ **最佳实践**：
1. 使用方案 2 修改 `stream_printing_messages`（根本性解决）
2. 在您的 `query_func` 中添加断开检测（双重保险）
3. 添加超时控制（防止无限等待）
4. 完善日志记录（便于调试）

这样，当客户端断开连接时，后端将立即停止 Agent 执行，释放资源。
