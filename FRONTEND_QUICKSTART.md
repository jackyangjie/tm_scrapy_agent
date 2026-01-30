# 前端快速开始

## 📦 安装依赖

```bash
cd frontend
npm install
```

## 🚀 启动前端

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动

## 🔗 连接后端

确保后端在 `http://127.0.0.1:8080` 运行：

```bash
cd backend
python main.py
```

## 💬 发送消息

### 方式一：使用 React 界面

1. 打开浏览器访问 `http://localhost:5173`
2. 在输入框输入消息
3. 点击"发送"按钮或按 Enter 键

### 方式二：使用测试页面

```bash
cd frontend
# 在浏览器中打开 test-api.html
```

### 方式三：使用 cURL

```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/ag-ui' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "context": [],
  "messages": [{"content": "你是谁", "id": "msg_2", "role": "user"}],
  "runId": "run_456",
  "threadId": "thread_123",
  "tools": []
}'
```

## 📝 API 配置

前端配置文件：`frontend/src/services/api.js`

```javascript
const API_BASE_URL = 'http://127.0.0.1:8080';
```

## 🎯 常见使用场景

### 1. 简单对话

```javascript
chatAPI.sendMessage('你是谁');
```

### 2. 搜索信息

```javascript
chatAPI.sendMessage('帮我搜索最新的 AI 新闻');
```

### 3. 数据采集

```javascript
chatAPI.sendMessage('采集一下百度的首页信息');
```

## 📊 响应处理

### 响应类型

| 类型 | 说明 | 示例 |
|------|------|------|
| String | 简单文本响应 | "你好，我是智能采集助手" |
| Object (status) | 状态消息 | {"status": "processing", "message": "处理中..."} |
| Array | AgentScope 消息数组 | [{"content": [...], "role": "assistant"}] |

### 示例代码

```javascript
const response = await chatAPI.sendMessage('你好');

if (typeof response === 'string') {
  console.log('简单文本:', response);
} else if (response?.status === 'processing') {
  console.log('处理状态:', response.message);
} else if (Array.isArray(response)) {
  response.forEach(msg => {
    if (msg?.content) {
      const text = msg.content
        .filter(c => c?.type === 'text')
        .map(c => c?.text)
        .join('');
      console.log('消息内容:', text);
    }
  });
}
```

## 🐛 故障排除

### 问题：无法连接后端

**检查清单**：
- [ ] 后端是否启动？（查看 `python main.py` 终端）
- [ ] 端口是否正确？（应为 8080）
- [ ] 地址是否正确？（应为 `http://127.0.0.1:8080`）
- [ ] 防火墙是否阻止连接？

**解决方案**：
1. 确认后端运行：访问 `http://127.0.0.1:8080/docs`
2. 检查前端配置：`frontend/src/services/api.js`
3. 查看浏览器控制台：F12 → Console

### 问题：消息发送失败

**检查清单**：
- [ ] 输入内容是否为空？
- [ ] 网络是否正常？
- [ ] 后端是否报错？

**解决方案**：
1. 查看后端日志输出
2. 检查 Network 标签请求详情
3. 尝试使用测试页面 `test-api.html`

### 问题：没有响应

**可能原因**：
- Agent 正在处理复杂任务
- MCP 工具调用失败
- LLM API 超时

**解决方案**：
1. 等待更长时间（部分任务需要 1-2 分钟）
2. 查看后端日志了解进度
3. 重启后端服务

## 📚 更多资源

- [完整对接文档](./FRONTEND_BACKEND_INTEGRATION.md)
- [AgentScope 文档](./backend/AGENT_SCOPE_SKILL_GUIDE.md)
- [后端架构说明](./AGENTS.md)
