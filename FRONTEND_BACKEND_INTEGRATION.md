# 前后端对接说明

## 后端接口

### 端点：`/ag-ui`

**方法**：POST

**URL**：`http://127.0.0.1:8080/ag-ui`

**请求格式**：
```json
{
  "context": [],
  "messages": [
    {
      "content": "你是谁",
      "id": "msg_2",
      "role": "user"
    }
  ],
  "runId": "run_456",
  "threadId": "thread_123",
  "tools": []
}
```

**响应格式**：
```json
{
  "status": "processing",
  "message": "正在处理请求..."
}
```

## 前端调用

### API 配置

```javascript
// src/services/api.js
const API_BASE_URL = 'http://127.0.0.1:8080';
```

### 发送消息

```javascript
const response = await chatAPI.sendMessage(message);
```

### 请求参数说明

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| context | Array | 上下文信息 | [] |
| messages | Array | 消息列表 | [{"content": "你是谁", "id": "msg_2", "role": "user"}] |
| messages[*].content | String | 消息内容 | "你是谁" |
| messages[*].id | String | 消息ID | "msg_2" |
| messages[*].role | String | 角色 | "user" |
| runId | String | 运行ID | "run_456" |
| threadId | String | 线程ID | "thread_123" |
| tools | Array | 工具列表 | [] |

## 启动服务

### 后端

```bash
cd backend
python main.py
```

服务将在 `http://127.0.0.1:8080` 启动

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:5173` 启动

## 测试接口

### 使用 curl

```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/ag-ui' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "context": [],
  "messages": [
    {
      "content": "你是谁",
      "id": "msg_2",
      "role": "user"
    }
  ],
  "runId": "run_456",
  "threadId": "thread_123",
  "tools": []
}'
```

### 使用测试脚本

```bash
cd backend
./test_agui.sh
```

## 数据流程

```
用户输入 → 前端 ChatInterface
    ↓
chatAPI.sendMessage()
    ↓
POST /ag-ui
    ↓
后端 convert_frontend_messages_to_agent_request()
    ↓
AgentRequest (session_id=threadId, id=runId)
    ↓
agent._runner.query_handler()
    ↓
ReActAgent (scrapy_agent.py)
    ↓
MCP 工具 + Skills
    ↓
流式响应
    ↓
前端更新 UI
```

## 前端组件说明

### ChatInterface.jsx

**主要功能**：
- 发送消息到后端
- 显示对话历史
- 处理加载状态
- 显示系统状态

**关键函数**：
- `handleSendMessage()`: 发送消息并处理响应
- `handleClearChat()`: 清空对话
- `scrollToBottom()`: 自动滚动到底部

**响应处理**：
```javascript
if (typeof response === 'string') {
  assistantContent = response;
} else if (response?.status === 'processing') {
  assistantContent = response.message || '处理中...';
} else if (response?.status === 'error') {
  assistantContent = response.message || '出错了';
} else if (Array.isArray(response)) {
  // 处理 AgentScope Message 格式
}
```

## 常见问题

### Q: 前端无法连接后端

A: 检查以下几点：
1. 后端是否在 8080 端口运行
2. 前端 API_BASE_URL 是否正确（应为 `http://127.0.0.1:8080`）
3. 是否有防火墙阻止连接
4. 浏览器控制台是否有 CORS 错误

### Q: 消息发送后没有响应

A: 检查：
1. 后端日志是否有错误
2. Agent 是否正确初始化
3. MCP 服务器是否正常连接（ddg-search, playwright）
4. 环境变量是否正确配置（.env 文件）

### Q: 如何查看详细日志

A:
- 后端日志：运行 `python main.py` 的终端输出
- 前端日志：浏览器开发者工具 Console 标签
- 网络：浏览器开发者工具 Network 标签查看请求/响应

## 环境变量配置

### backend/.env

```
base_url=https://open.bigmodel.cn/api/coding/paas/v4
api_key=your_api_key
model_name=glm-4.7
```

## MCP 服务器配置

### config.py

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
    "playwright": {
        "command": "npx",
        "args": ["@playwright/mcp@latest"],
        "env": {
            "https_proxy": "http://127.0.0.1:5081",
            "http_proxy": "http://127.0.0.1:5081"
        }
    }
}
```
