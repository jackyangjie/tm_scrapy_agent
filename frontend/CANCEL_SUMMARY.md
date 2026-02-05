# 重写 useChatController.handleCancel 总结

## 问题

`@agentscope-ai/chat` 库的 `useChatController` 中，`handleCancel` 方法直接调用 `finishResponse('interrupted')`，无法直接修改其行为。

## 解决方案

已实现 **方案 1 + 方案 2**：

### 1. 监听自定义事件

```tsx
useEffect(() => {
  const handleCustomCancel = (event: Event) => {
    const customEvent = event as CustomEvent;
    senderOptions.onCancel();
  };

  document.addEventListener('handleCustomCancel', handleCustomCancel);

  return () => {
    document.removeEventListener('handleCustomCancel', handleCustomCancel);
  };
}, []);
```

### 2. SenderOptions 实现

```tsx
class SenderOptions implements IAgentScopeRuntimeWebUISenderOptions {
  abortController: AbortController | null = null;

  async onSubmit(data: { query: string; fileList?: any[] }) {
    this.abortController = new AbortController();
    const response = await fetch('/api/chat', {
      signal: this.abortController.signal
    });
  }

  async onCancel() {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }
}
```

## 测试方法

1. 启动应用
2. 发送消息
3. 点击右下角测试按钮：
   - "触发自定义取消事件" - 触发 DOM 事件
   - "直接调用 onCancel" - 直接调用方法
4. 观察控制台输出

## 其他方案

详见 `useCancelController.ts` 和 `CANCEL_IMPLEMENTATION.md`
