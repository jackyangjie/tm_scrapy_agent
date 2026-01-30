# SSE 流式响应处理

## 响应格式

后端使用 **Server-Sent Events (SSE)** 返回流式数据。每个数据块以 `data:` 前缀。

### 事件类型

| 类型 | 说明 | 示例 |
|------|------|------|
| RUN_STARTED | 运行开始 | `{"type": "RUN_STARTED", "threadId": "...", "runId": "..."}` |
| TEXT_MESSAGE_START | 文本消息开始 | `{"type": "TEXT_MESSAGE_START", "messageId": "...", "role": "assistant"}` |
| TEXT_MESSAGE_CONTENT | 文本内容增量 | `{"type": "TEXT_MESSAGE_CONTENT", "messageId": "...", "delta": "用户"}` |
| TEXT_MESSAGE_END | 文本消息结束 | `{"type": "TEXT_MESSAGE_END", "messageId": "...", "finalContent": "完整内容"}` |
| ERROR | 错误消息 | `{"type": "ERROR", "message": "错误描述"}` |

### 示例响应流

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

完整消息内容："用户在问\"你是谁"

## 前端处理

### JavaScript/React

```javascript
async function sendMessage(message, onChunk) {
    const response = await fetch('http://127.0.0.1:8080/ag-ui', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'accept': 'text/event-stream'
        },
        body: JSON.stringify({
            context: [],
            messages: [{ content: message, id: 'msg_xxx', role: 'user' }],
            runId: 'run_456',
            threadId: 'thread_123',
            tools: []
        })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const event = JSON.parse(line.substring(6).trim());
                    handleSSEEvent(event, onChunk);
                } catch (e) {
                    console.error('解析 SSE 失败:', e);
                }
            }
        }
    }
}

function handleSSEEvent(event, onChunk) {
    switch (event.type) {
        case 'RUN_STARTED':
            console.log('运行开始:', event.runId);
            break;

        case 'TEXT_MESSAGE_START':
            console.log('消息开始:', event.messageId);
            break;

        case 'TEXT_MESSAGE_CONTENT':
            console.log('增量内容:', event.delta);
            onChunk?.(event.delta);
            break;

        case 'TEXT_MESSAGE_END':
            console.log('消息结束:', event.finalContent);
            break;

        case 'ERROR':
            console.error('错误:', event.message);
            break;
    }
}
```

### React 组件示例

```javascript
function ChatInterface() {
    const [currentMessage, setCurrentMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSendMessage = async () => {
        setLoading(true);
        setCurrentMessage('');

        await chatAPI.sendMessage(inputValue, (event) => {
            if (event.type === 'TEXT_MESSAGE_START') {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: '',
                    timestamp: new Date().toISOString()
                }]);
            } else if (event.type === 'TEXT_MESSAGE_CONTENT') {
                setCurrentMessage(prev => prev + (event.delta || ''));
            } else if (event.type === 'TEXT_MESSAGE_END') {
                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.role === 'assistant') {
                        lastMessage.content = event.finalContent || currentMessage;
                    }
                    return newMessages;
                });
                setLoading(false);
            }
        });
    };

    return (
        <div>
            {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                    {loading && index === messages.length - 1 && msg.role === 'assistant'
                        ? currentMessage || msg.content
                        : msg.content}
                </div>
            ))}
        </div>
    );
}
```

## 使用 Axios 处理 SSE

```javascript
const api = axios.create({
    baseURL: 'http://127.0.0.1:8080',
    headers: {
        'Content-Type': 'application/json',
    },
});

export async function sendMessage(message, onChunk) {
    const response = await api.post('/ag-ui', {
        context: [],
        messages: [{ content: message, id: 'msg_xxx', role: 'user' }],
        runId: 'run_456',
        threadId: 'thread_123',
        tools: []
    }, {
        responseType: 'text',
        transformResponse: (data) => {
            const lines = data.split('\n');
            const events = [];

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const event = JSON.parse(line.substring(6).trim());
                        events.push(event);
                        onChunk?.(event);
                    } catch (e) {
                        console.error('解析 SSE 失败:', e);
                    }
                }
            }

            return events;
        },
    });

    return response.data;
}
```

## 测试工具

### curl 测试

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

### Python 测试

```python
import requests
import json

response = requests.post(
    'http://127.0.0.1:8080/ag-ui',
    headers={
        'Content-Type': 'application/json',
        'accept': 'text/event-stream'
    },
    json={
        'context': [],
        'messages': [{'content': '你是谁', 'id': 'msg_1', 'role': 'user'}],
        'runId': 'run_456',
        'threadId': 'thread_123',
        'tools': []
    },
    stream=True
)

for line in response.iter_lines():
    if line.startswith('data: '):
        event = json.loads(line[6:])
        print(f"Event: {event['type']}")
        if 'delta' in event:
            print(f"  Delta: {event['delta']}")
```

## 关键点

1. **设置正确的请求头**
   ```javascript
   headers: {
       'Content-Type': 'application/json',
       'accept': 'text/event-stream'
   }
   ```

2. **逐行解析 SSE 数据**
   ```javascript
   for (const line of lines) {
       if (line.startsWith('data: ')) {
           const event = JSON.parse(line.substring(6));
           handleEvent(event);
       }
   }
   ```

3. **增量构建消息内容**
   ```javascript
   let accumulatedContent = '';
   if (event.type === 'TEXT_MESSAGE_CONTENT') {
       accumulatedContent += event.delta || '';
       updateUI(accumulatedContent);
   }
   ```

4. **处理缓冲区**
   - SSE 可能跨多行
   - 使用 buffer 拼接不完整的数据
   - 每次只处理完整的行

## 故障排除

### 问题：无法接收流式数据

**原因**：
- 请求头缺少 `accept: text/event-stream`
- 响应类型不正确

**解决**：
```javascript
headers: {
    'accept': 'text/event-stream'
}
```

### 问题：JSON 解析失败

**原因**：
- SSE 事件不完整（跨多行）
- 数据包含特殊字符

**解决**：
```javascript
const lines = buffer.split('\n');
buffer = lines.pop() || ''; // 保留未完成的行

for (const line of lines) {
    if (line.startsWith('data: ') && line.trim()) {
        try {
            const event = JSON.parse(line.substring(6).trim());
            handleEvent(event);
        } catch (e) {
            console.error('解析失败，跳过:', line);
        }
    }
}
```

### 问题：消息内容不完整

**原因**：
- 没有等待 TEXT_MESSAGE_END 事件
- 只显示了增量内容

**解决**：
- 跟踪 TEXT_MESSAGE_START 开始
- 累积所有 TEXT_MESSAGE_CONTENT 的 delta
- 在 TEXT_MESSAGE_END 时完成消息
- 显示 `accumulatedContent + finalContent`
