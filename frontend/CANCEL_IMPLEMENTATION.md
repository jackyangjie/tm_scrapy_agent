# 重写 useChatController 中的 handleCancel

`useChatController` 中的 `handleCancel` 方法位于库的源码中，无法直接修改。以下是几种替代方案：

---

## 方案 1：监听自定义事件（推荐）

**原理**：库使用 DOM CustomEvent 事件系统

**实现**：

```tsx
// Chat/index.tsx
useEffect(() => {
  const handleCustomCancel = (event: Event) => {
    const customEvent = event as CustomEvent;
    console.log('🚫 Custom cancel handler:', customEvent.detail);

    // 执行自定义取消逻辑
    senderOptions.onCancel();

    // 可以添加：
    // - 发送取消请求到后端
    // - 清理资源
    // - 记录日志
  };

  document.addEventListener('handleCustomCancel', handleCustomCancel);

  return () => {
    document.removeEventListener('handleCustomCancel', handleCustomCancel);
  };
}, []);
```

**触发**：
```tsx
document.dispatchEvent(new CustomEvent('handleCustomCancel', {
  detail: { reason: 'user_cancelled' }
}));
```

---

## 方案 2：直接在 sender.onCancel 中实现

**原理**：利用你已经配置的 `senderOptions`

**实现**：

```tsx
// Sender/index.ts
class SenderOptions implements IAgentScopeRuntimeWebUISenderOptions {
  abortController: AbortController | null = null;

  async onCancel() {
    console.log('🚫 Cancelling request...');

    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }

    // 添加额外逻辑
    this.cleanup();
    this.notifyBackend();
  }

  private cleanup() {
    console.log('🧹 Cleaning up resources...');
  }

  private async notifyBackend() {
    console.log('📡 Notifying backend about cancellation...');
    // await fetch('/api/cancel', { method: 'POST' });
  }
}
```

---

## 方案 3：使用 chatRef 手动控制

**原理**：通过 ref 直接操作组件内部状态

**实现**：

```tsx
// Chat/index.tsx
const chatRef = useRef<IAgentScopeRuntimeWebUIRef>(null);

const cancelRequest = useCallback(() => {
  console.log('🚫 Manual cancellation via ref');

  // 禁用输入
  chatRef.current?.input.setDisabled(true);

  // 执行取消逻辑
  senderOptions.onCancel();

  // 重新启用输入
  setTimeout(() => {
    chatRef.current?.input.setDisabled(false);
  }, 500);
}, [chatRef]);

return (
  <>
    <AgentScopeRuntimeWebUI options={options} ref={chatRef} />
    <button onClick={cancelRequest}>取消请求</button>
  </>
);
```

---

## 方案 4：拦截库的内部事件

**原理**：监听库内部的所有 CustomEvent

**实现**：

```tsx
useEffect(() => {
  const logAllEvents = (e: Event) => {
    if (e instanceof CustomEvent) {
      console.log('📡 Event:', e.type, e.detail);
    }
  };

  // 监听所有事件（用于调试）
  document.addEventListener('handleSubmit', logAllEvents);
  document.addEventListener('handleReplace', logAllEvents);

  // 如果库有 handleCancel 事件，也可以监听
  // document.addEventListener('handleCancel', logAllEvents);

  return () => {
    document.removeEventListener('handleSubmit', logAllEvents);
    document.removeEventListener('handleReplace', logAllEvents);
  };
}, []);
```

---

## 方案 5：修改库源码（不推荐）

**文件位置**：
```
frontend/node_modules/@agentscope-ai/chat/lib/AgentScopeRuntimeWebUI/core/Chat/hooks/useChatController.js
```

**修改**：
```javascript
// 原始代码
var handleCancel = useCallback(function () {
  finishResponse('interrupted');
}, [finishResponse]);

// 修改为
var handleCancel = useCallback(function () {
  console.log('🚫 Cancelled from useChatController');

  // 发送自定义事件
  document.dispatchEvent(new CustomEvent('handleCustomCancel', {
    detail: { source: 'useChatController' }
  }));

  finishResponse('interrupted');
}, [finishResponse]);
```

⚠️ **缺点**：npm install 后会被覆盖

---

## 方案 6：创建 fork 的库（最彻底）

如果需要大量自定义，可以：

1. Fork `@agentscope-ai/chat` 仓库
2. 修改 `useChatController` 的实现
3. 发布到私有 npm 或使用 Git 引用

```bash
# package.json
{
  "dependencies": {
    "@agentscope-ai/chat": "git+https://github.com/your-fork/chat.git#custom-branch"
  }
}
```

---

## 推荐方案

根据需求选择：

| 需求 | 推荐方案 |
|------|---------|
| 简单取消逻辑 | 方案 2：直接在 sender.onCancel 中实现 |
| 需要监听库的取消 | 方案 1：监听自定义事件 |
| 复杂的取消流程 | 方案 3：使用 chatRef |
| 长期维护 | 方案 6：Fork 库并修改 |

---

## 当前实现

你的项目已经实现了 **方案 1 + 方案 2**：

1. ✅ `Sender/index.ts` 中实现了 `onCancel`
2. ✅ `Chat/index.tsx` 中监听了自定义事件
3. ✅ 添加了测试按钮验证功能

测试步骤：
1. 发送一条消息
2. 点击"触发自定义取消事件"或"直接调用 onCancel"
3. 观察控制台输出
