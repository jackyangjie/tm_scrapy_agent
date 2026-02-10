# SimpleAgent 实现文档

## 概述

SimpleAgent 是一个轻量级的对话代理，专门用于处理简单的问答任务，不需要复杂的推理过程。

## 主要特性

### 1. 基础问答功能
- 直接回答用户问题
- 无需复杂的多步推理
- 保持对话上下文
- 支持自定义系统提示词

### 2. 可选的搜索工具
- DuckDuckGo 搜索集成（通过 MCP）
- 获取最新信息
- 支持网络搜索查询

### 3. 灵活的配置
- 启用/禁用搜索工具
- 自定义系统提示词
- 简洁的 API 接口

## 文件结构

```
backend/
├── agent/
│   ├── simple_agent.py          # SimpleAgent 核心实现
│   ├── agent_factory.py          # Agent 工厂
│   └── ...
├── config.py                     # 配置文件（包含 MCP 配置）
├── test_simple_agent.py          # 测试文件
└── examples/
    └── simple_agent_examples.py  # 使用示例
```

## 配置

### MCP 服务器配置（config.py）

```python
mcp_servers_config = {
    "ddg-search": {
        "command": "uvx",
        "args": ["duckduckgo-mcp-server"],
        "env": {
            "https_proxy": "http://127.0.0.1:5081",
            "http_proxy": "http://127.0.0.1:5081"
        }
    },
    # 其他 MCP 服务器...
}
```

### 系统提示词配置

```python
simple_agent_sys_prompt = """你是一个友好、专业的AI助手，擅长回答各类问题。

你的能力：
1. 回答常识性问题
2. 提供信息和解释概念
3. 进行简单的推理和分析
4. 使用搜索工具获取最新信息（如果可用）
...
"""
```

## 使用方法

### 方法 1：直接使用 SimpleAgent

```python
from agent.simple_agent import SimpleAgent
from agentscope.model import OpenAIChatModel

# 初始化模型
model = OpenAIChatModel(
    model_name="glm-4.7",
    api_key="your-api-key",
    client_kwargs={"base_url": "your-base-url"},
)

# 创建 SimpleAgent
agent = SimpleAgent(
    name="qa_bot",
    model=model,
    toolkit=None,  # 不使用工具
)

# 进行问答
from agentscope.message import Msg

question = Msg(role="user", content="什么是人工智能？")
answer = agent.forward([question])

print(answer.content)
```

### 方法 2：使用工厂函数创建

```python
import asyncio
from agent.simple_agent import create_simple_agent

async def main():
    # 创建带搜索功能的 SimpleAgent
    agent = await create_simple_agent(
        name="search_bot",
        enable_search=True,
    )

    # 问答
    question = Msg(role="user", content="今天北京的天气怎么样？")
    answer = agent.forward([question])

    print(answer.content)

asyncio.run(main())
```

### 方法 3：使用 Agent 工厂

```python
from agent.agent_factory import create_simple_agent, get_agent_type

# 根据任务自动选择 Agent 类型
task = "什么是Python？"
agent_type = get_agent_type(task)  # 返回 "simple" 或 "react"

if agent_type == "simple":
    # 使用 SimpleAgent
    agent = await create_simple_agent()
else:
    # 使用 ReActAgent
    agent = await create_react_agent()
```

## 与 ReActAgent 的对比

| 特性 | SimpleAgent | ReActAgent |
|------|-------------|------------|
| **适用场景** | 简单问答、直接回答 | 复杂推理、多步骤任务 |
| **推理过程** | 无 | 有（ReAct 循环） |
| **工具使用** | 可选（通常用于搜索） | 丰富（爬虫、数据库等） |
| **响应速度** | 快 | 较慢（需要推理步骤） |
| **系统提示词** | 简洁、直接 | 详细、包含工具说明 |
| **内存管理** | 基础 | BoundedMemory（高级） |

## 选择指南

### 使用 SimpleAgent 的场景：

- ✅ 简单的知识问答
- ✅ 概念解释
- ✅ 一般性咨询
- ✅ 需要快速响应
- ✅ 基础信息检索

### 使用 ReActAgent 的场景：

- ✅ 数据采集
- ✅ 网页爬取
- ✅ 复杂分析
- ✅ 多步骤任务
- ✅ 需要使用多种工具

## 测试

运行测试文件：

```bash
cd backend
python test_simple_agent.py
```

测试内容包括：
1. 基础问答功能（无工具）
2. 带搜索工具的问答
3. Agent 工厂集成测试
4. 多轮对话测试

## API 参考

### SimpleAgent 类

```python
class SimpleAgent(Agent):
    def __init__(
        self,
        name: str,
        model: OpenAIChatModel,
        toolkit: Optional[Toolkit] = None,
        sys_prompt: Optional[str] = None,
    )
```

**参数：**
- `name`: Agent 名称
- `model`: 语言模型实例
- `toolkit`: 可选的工具包
- `sys_prompt`: 可选的自定义系统提示词

**方法：**
- `forward(msgs: list[Msg]) -> Msg`: 处理消息并返回回复

### 工厂函数

```python
async def create_simple_agent(
    name: str = "simple_agent",
    enable_search: bool = True,
    custom_prompt: Optional[str] = None,
) -> SimpleAgent
```

**参数：**
- `name`: Agent 名称
- `enable_search`: 是否启用搜索工具
- `custom_prompt`: 自定义系统提示词

**返回：**
- 配置好的 SimpleAgent 实例

### Agent 类型检测

```python
def get_agent_type(task_type: str) -> str
```

**参数：**
- `task_type`: 任务描述

**返回：**
- `"simple"`: 适合 SimpleAgent
- `"react"`: 适合 ReActAgent

## 扩展建议

### 添加新的 MCP 工具

1. 在 `config.py` 中添加 MCP 服务器配置
2. 在 `create_simple_agent()` 中注册新的 MCP 客户端
3. 根据需要调整系统提示词

### 自定义系统提示词

```python
custom_prompt = """你是一个专业的领域助手。
请专注于回答与[特定领域]相关的问题。
...
"""

agent = SimpleAgent(
    name="specialist",
    model=model,
    sys_prompt=custom_prompt,
)
```

## 常见问题

### Q1: SimpleAgent 能使用所有 MCP 工具吗？

A: 可以，但建议只使用搜索类工具（如 ddg-search）。对于复杂的工具使用场景，推荐使用 ReActAgent。

### Q2: 如何在 Web 应用中使用 SimpleAgent？

A: 可以创建类似于 `main_agent.py` 的 AgentApp 端点，使用 SimpleAgent 替代 ReActAgent。

### Q3: SimpleAgent 支持多轮对话吗？

A: 支持。需要手动维护对话历史，在每次调用时传入完整的消息列表。

### Q4: 如何调整 SimpleAgent 的回答风格？

A: 通过 `sys_prompt` 参数自定义系统提示词，可以改变 Agent 的回答风格和侧重点。

## 更新日志

- **2025-02-10**: 初始实现
  - ✅ SimpleAgent 基础类
  - ✅ DuckDuckGo 搜索 MCP 集成
  - ✅ Agent 工厂模式
  - ✅ 测试和示例代码

## 许可证

与主项目保持一致
