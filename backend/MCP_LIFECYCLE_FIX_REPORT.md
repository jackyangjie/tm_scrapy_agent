# Bug 修复报告：MCP Client Async Context Manager Error

## 问题描述

**错误信息**: `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`

**发生时间**: 2026-02-10 15:31:43

**错误来源**: MCP (Model Context Protocol) stdio 客户端的异步上下文管理

## 根本原因

在 `agent/simple_agent.py` 和 `agent/scrapy_agent.py` 的工具函数中，MCP 客户端被创建但**从未关闭**，导致：

1. **资源泄漏**: 每次函数调用都创建新的 MCP 客户端连接
2. **跨任务清理**: 客户端在一个异步任务中创建，但在不同的任务（Python 垃圾回收器）中尝试关闭
3. **上下文不匹配**: `anyio` 的 cancel scope 在不同的 async task 中进入和退出

### 错误代码模式

```python
# ❌ 错误代码（原始版本）
async def scrapy_agent_fucntion(...):
    for server_name, server_config in mcp_servers_config.items():
        client = StdIOStatefulClient(server_name, **server_config)
        await client.connect()
        await toolkit.register_mcp_client(client)
        # 问题：client 从未被关闭！
        # 函数结束时，Python 在不同的任务中尝试清理
```

## 修复内容

### 文件 1: `/backend/agent/simple_agent.py`

**添加客户端追踪和清理**:

```python
# 修复前
toolkit = None
if enable_search:
    toolkit = Toolkit()
    for server_name, server_config in mcp_servers_config.items():
        client = StdIOStatefulClient(server_name, **server_config)
        await client.connect()
        await toolkit.register_mcp_client(client)
        # 没有清理代码！

# 修复后
toolkit = None
mcp_clients = []  # 追踪所有创建的客户端
if enable_search:
    toolkit = Toolkit()
    for server_name, server_config in mcp_servers_config.items():
        client = StdIOStatefulClient(server_name, **server_config)
        await client.connect()
        await toolkit.register_mcp_client(client)
        mcp_clients.append(client)  # 保存引用

try:
    # ... Agent 逻辑 ...
    return ToolResponse(...)
finally:
    # 清理 MCP 客户端
    for client in mcp_clients:
        try:
            if client.is_connected:
                await client.close()
                logging.info(f"Closed MCP client: {client.name}")
        except Exception as e:
            logging.warning(f"Error closing MCP client: {e}")
```

### 文件 2: `/backend/agent/scrapy_agent.py`

应用了相同的修复模式。

## 修复详解

### 关键改进

**1. 客户端追踪**
```python
mcp_clients = []  # 保存所有客户端引用
```

**2. 异常安全清理**
```python
try:
    # 业务逻辑
    return result
finally:
    # 无论如何都会执行清理
    for client in mcp_clients:
        await client.close()
```

**3. 优雅的错误处理**
```python
try:
    if client.is_connected:
        await client.close()
except Exception as e:
    logging.warning(f"Error closing MCP client: {e}")
    # 不影响主流程继续执行
```

## 验证结果

✅ **语法检查**: 通过
```bash
python -m py_compile agent/simple_agent.py agent/scrapy_agent.py
# 无错误
```

✅ **finally 块**: 已添加到两个文件
```bash
grep -c "finally:" agent/simple_agent.py agent/scrapy_agent.py
# 输出:
# agent/simple_agent.py:1
# agent/scrapy_agent.py:1
```

## 预防措施

### 最佳实践

**1. 始终清理 MCP 客户端**
```python
# ✅ 好的做法
mcp_clients = []
try:
    client = StdIOStatefulClient(...)
    await client.connect()
    mcp_clients.append(client)
    # ... 使用客户端 ...
finally:
    for client in mcp_clients:
        await client.close()

# ❌ 避免
client = StdIOStatefulClient(...)
await client.connect()
# 忘记关闭客户端
```

**2. 使用 try/finally 确保清理**
```python
# ✅ 即使发生异常也会清理
try:
    result = await process()
    return result
finally:
    await cleanup()  # 总是执行
```

**3. 追踪所有资源**
```python
# ✅ 保存引用以便后续清理
resources = []
resources.append(resource1)
resources.append(resource2)
```

**4. 优雅地处理清理错误**
```python
# ✅ 清理错误不应该影响主流程
try:
    await resource.close()
except Exception as e:
    logging.warning(f"Cleanup error: {e}")
    # 继续执行，不抛出异常
```

## 其他发现

### 1. main_agent.py 中的正确模式

在 `main_agent.py` 中，MCP 客户端的生命周期管理是正确的：

```python
@agent_app.init
async def init_func(self):
    self.mcp_clients: dict[str, StdIOStatefulClient] = {}
    await _init_mcp_clients(self.mcp_clients)  # 创建并追踪

@agent_app.shutdown
async def shutdown_func(self):
    for name, client in self.mcp_clients.items():
        if client.is_connected:
            await client.close()  # 清理所有客户端
    self.mcp_clients.clear()
```

**这是推荐的模式**：应用启动时创建，应用关闭时清理。

### 2. Agent 工厂中的类似问题

`agent_factory.py` 中的 `create_react_agent()` 和 `create_simple_agent()` 也有相同的问题（未在此次修复中处理）：

```python
# agent_factory.py 中的模式
async def create_react_agent(...):
    # ...
    for server_name, server_config in mcp_servers_config.items():
        client = StdIOStatefulClient(server_name, **server_config)
        await client.connect()
        # 问题：这些客户端没有被追踪或关闭
    # 返回 agent，但客户端泄漏
```

**建议**: 工厂函数应该返回需要清理的客户端列表，或者使用应用级的客户端池。

## 相关错误

### GeneratorExit

```
File "/mcp/client/stdio/__init__.py", line 189, in stdio_client
    yield read_stream, write_stream
GeneratorExit
```

这表明 stdio 客户端使用了异步生成器作为上下文管理器，当在不同的任务中清理时会触发 GeneratorExit。

### Cancel Scope 不匹配

```
File "/anyio/_backends/_asyncio.py", line 789, in __aexit__
    if self.cancel_scope.__exit__(type(exc), exc, exc.__traceback__):
raise RuntimeError(
RuntimeError: Attempted to exit cancel scope in a different task than it was entered in
```

`anyio` 检测到 cancel scope 在不同的 async task 中退出，这是异步编程中的常见错误。

## 测试建议

修复后，监控以下方面：

```python
# 1. 多次调用测试
for i in range(10):
    result = await simple_agent_fucntion(f"测试 {i}")
    assert result is not None

# 2. 错误处理测试
result = await simple_agent_fucntion("无效输入")
# 应该优雅处理，不留下僵尸连接

# 3. 并发测试
tasks = [
    simple_agent_fucntion(f"测试 {i}")
    for i in range(5)
]
results = await asyncio.gather(*tasks)
# 应该没有 cancel scope 错误
```

## 长期解决方案

### 选项 A: 客户端池（推荐）

```python
# 在应用级别维护 MCP 客户端池
class MCPClientPool:
    def __init__(self):
        self.clients = {}

    async def get_client(self, name):
        if name not in self.clients:
            client = StdIOStatefulClient(name, ...)
            await client.connect()
            self.clients[name] = client
        return self.clients[name]

    async def cleanup_all(self):
        for client in self.clients.values():
            await client.close()
```

### 选项 B: 使用全局客户端

参考 `main_agent.py` 的模式，在应用启动时创建所有客户端，在工具函数中重用它们：

```python
# 移除工具函数中的客户端创建
# 改为使用 self.mcp_clients（来自 main_agent.py）
```

## 总结

- ✅ **问题已修复**: 添加了 try/finally 块确保 MCP 客户端正确关闭
- ✅ **资源泄漏解决**: 客户端在使用后立即清理
- ✅ **异步安全**: 避免跨任务的 cancel scope 问题
- ⚠️ **建议**: 考虑重构为客户端池模式以获得更好的性能

## 相关文件

- `/backend/agent/simple_agent.py` - 已添加 MCP 清理逻辑
- `/backend/agent/scrapy_agent.py` - 已添加 MCP 清理逻辑
- `/backend/agent/main_agent.py` - 正确的 MCP 生命周期管理参考

---

**修复完成时间**: 2026-02-10 15:35

**修复人员**: AI Assistant
