# SSE 流式响应对接完成

## ✅ 已完成的修改

### 后端

**文件**：`backend/main.py`

已新增：
- `convert_frontend_messages_to_agent_request()` - 转换请求格式
- `/ag-ui` 端点 - 接收前端请求并返回 SSE 流式响应

### 前端

**文件**：`frontend/src/components/ChatInterface.jsx`

已更新：
- 添加 `currentMessage` state 实时跟踪流式内容
- 实现 SSE 流式解析和事件处理
- 添加 `streaming` 标识显示流式状态
- 优化消息显示逻辑

**文件**：`frontend/src/services/api.js`

已更新：
- 修改为使用原生 `fetch` API（支持 SSE）
- 添加 `accept: text/event-stream` 请求头
- 添加 `onChunk` 回调处理流式数据

## 📊 SSE 响应格式

### 事件类型

| 类型 | 说明 | 字段 |
|------|------|------|
| RUN_STARTED | 运行开始 | threadId, runId |
| TEXT_MESSAGE_START | 消息开始 | messageId, role |
| TEXT_MESSAGE_CONTENT | 增量内容 | messageId, delta |
| TEXT_MESSAGE_END | 消息结束 | messageId, finalContent |
| ERROR | 错误消息 | message |

### 响应示例

```
data: {"type": "RUN_STARTED", "threadId": "thread_123", "runId": "run_456"}
data: {"type": "TEXT_MESSAGE_START", "messageId": "msg_xxx", "role": "assistant"}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "msg_xxx", "delta": "用户"}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "msg_xxx", "delta": "在"}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "msg_xxx", "delta": "问"}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "msg_xxx", "delta": "\""}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "msg_xxx", "delta": "你是"}
data: {"type": "TEXT_MESSAGE_CONTENT", "messageId": "msg_xxx", "delta": "谁"}
```

完整内容："用户在问\"你是谁"

## 🚀 启动服务

### 后端

```bash
cd backend
python main.py
```

输出：
```
🚀 Deploying AgentApp in detached process mode...
✅ Deployment successful: http://127.0.0.1:8080
📍 Deployment ID: deploy_xxx
```

### 前端

```bash
cd frontend
npm install  # 首次运行
npm run dev
```

输出：
```
➜  Vite v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

## 🧪 测试

### 方式一：浏览器界面

1. 访问 `http://localhost:5173`
2. 输入消息："你是谁"
3. 点击"发送"按钮
4. 观察流式响应（逐字显示）

### 方式二：测试页面

```bash
cd frontend
# 在浏览器打开 test-api.html
```

### 方式三：curl

```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/ag-ui' \
  -H 'Content-Type: application/json' \
  -H 'accept: text/event-stream' \
  -d '{
    "context": [],
    "messages": [{"content": "你是谁", "id": "msg_1", "role": "user"}],
    "runId": "run_456",
    "threadId": "thread_123",
    "tools": []
  }'
```

## 📖 相关文档

| 文档 | 说明 |
|------|------|
| `SSE_STREAMING.md` | SSE 流式处理完整指南 |
| `FRONTEND_BACKEND_INTEGRATION.md` | 前后端对接说明 |
| `FRONTEND_QUICKSTART.md` | 前端快速开始 |
| `frontend/src/services/streaming-example.js` | SSE 处理代码示例 |
| `frontend/test-api.html` | 可视化测试页面 |

## 🔍 数据流图

```
用户输入消息
    ↓
ChatInterface.handleSendMessage()
    ↓
创建用户消息 → setMessages()
    ↓
创建临时助手消息 (streaming: true)
    ↓
fetch('http://127.0.0.1:8080/ag-ui')
    ↓
Headers: { 'accept': 'text/event-stream' }
    ↓
后端 /ag-ui 端点
    ↓
convert_frontend_messages_to_agent_request()
    ↓
AgentRequest (session_id=threadId, id=runId)
    ↓
agent_app._runner.query_handler()
    ↓
ReActAgent (scrapy_agent.py)
    ↓
stream_printing_messages()
    ↓
SSE 流式响应
    ↓
前端逐行解析
    ↓
for (line of lines) {
    if (line.startsWith('data: ')) {
        const event = JSON.parse(line);
        handleEvent(event);
    }
}
    ↓
TEXT_MESSAGE_START → 重置 accumulatedContent
    ↓
TEXT_MESSAGE_CONTENT (多次)
    accumulatedContent += delta
    setCurrentMessage(accumulatedContent)  ← 实时显示
    ↓
TEXT_MESSAGE_END
    setMessages(完整内容)
    setLoading(false)
    ↓
UI 更新完成
```

## ⚙️ 关键配置

### 后端

**环境变量** (`.env`)：
```env
base_url=https://open.bigmodel.cn/api/coding/paas/v4
api_key=your_api_key
model_name=glm-4.7
```

**MCP 服务器** (`config.py`)：
- ddg-search: 搜索工具
- playwright: 浏览器自动化

### 前端

**API 地址** (`src/services/api.js`)：
```javascript
const API_BASE_URL = 'http://127.0.0.1:8080';
```

**请求头**：
```javascript
headers: {
    'Content-Type': 'application/json',
    'accept': 'text/event-stream'  // 必须设置
}
```

## 🐛 常见问题

### Q: 消息不显示流式效果

**检查清单**：
- [ ] 请求头包含 `accept: text/event-stream`？
- [ ] 正确解析 SSE 数据？
- [ ] 实时更新 UI (`setCurrentMessage`)？

**解决方案**：
```javascript
// 确保请求头正确
headers: {
    'accept': 'text/event-stream'  // 关键！
}

// 实时更新消息
if (event.type === 'TEXT_MESSAGE_CONTENT') {
    accumulatedContent += event.delta;
    setCurrentMessage(accumulatedContent);  // 立即更新
}
```

### Q: 消息内容不完整

**原因**：只显示了增量内容，没有等待 `TEXT_MESSAGE_END`

**解决方案**：
```javascript
let accumulatedContent = '';

if (event.type === 'TEXT_MESSAGE_START') {
    accumulatedContent = '';  // 重置
} else if (event.type === 'TEXT_MESSAGE_CONTENT') {
    accumulatedContent += event.delta;  // 累积
} else if (event.type === 'TEXT_MESSAGE_END') {
    accumulatedContent += event.finalContent;  // 最终内容
    setMessages([...messages, {
        content: accumulatedContent,  // 完整内容
        streaming: false
    }]);
}
```

### Q: JSON 解析失败

**原因**：SSE 数据跨多行

**解决方案**：使用缓冲区处理
```javascript
let buffer = '';

const lines = buffer.split('\n');
buffer = lines.pop() || '';  // 保留未完成的行

for (const line of lines) {
    if (line.startsWith('data: ')) {
        const event = JSON.parse(line.substring(6));
        // 处理事件
    }
}
```

## 📚 技术细节

### Server-Sent Events (SSE)

**特点**：
- 单向通信（服务器 → 客户端）
- 基于 HTTP 持久连接
- 文本格式：`data: {JSON}`
- 自动重连机制

**优点**：
- 实时推送
- 比轮询更高效
- 浏览器原生支持

### 流式处理要点

1. **正确解析**：逐行解析，处理缓冲区
2. **增量更新**：每次 delta 都要更新 UI
3. **状态管理**：区分开始、进行中、结束状态
4. **错误处理**：捕获解析错误和连接错误

## 🎯 下一步

1. ✅ 基础 SSE 流式对接完成
2. 🔄 测试各种场景（长消息、错误处理、网络中断）
3. 📊 添加消息历史管理
4. 🎨 优化 UI 流式显示效果（打字机效果）
5. 🔐 添加用户认证和会话管理
