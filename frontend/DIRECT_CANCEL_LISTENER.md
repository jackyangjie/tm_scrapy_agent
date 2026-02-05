# 直接监听取消事件 - 总结

## 问题

`@agentscope-ai/chat` 库的 `useChatController` 中，`handleCancel` 不触发任何可监听的事件。

## 解决方案

提供了 **6 种直接监听取消事件的方法**：

### 方案对比

| 方案 | 可靠性 | 性能 | 复杂度 | 推荐度 |
|------|--------|------|--------|--------|
| 1. 监听 loading 状态 | ⭐⭐⭐ | 高 | 简单 | ⭐⭐⭐ |
| 2. 监听消息状态 | ⭐⭐⭐⭐⭐ | 高 | 简单 | ⭐⭐⭐⭐⭐ |
| 3. DOM MutationObserver | ⭐⭐ | 低 | 中等 | ⭐⭐ |
| 4. 拦截函数调用 | ⭐⭐⭐⭐ | 中 | 复杂 | ⭐⭐⭐ |
| 5. 键盘监听 | ⭐⭐ | 高 | 简单 | ⭐⭐ |
| 6. 组合监听 | ⭐⭐⭐⭐⭐ | 中 | 简单 | ⭐⭐⭐⭐⭐ |

### 推荐：方案 2（监听消息状态变化）

**原理**：取消时，最后一条消息的 `msgStatus` 会被设置为 `'interrupted'`

```tsx
import { useMessageStatusChange } from './useDirectCancelListener';

function ChatComponent() {
  useMessageStatusChange(() => {
    console.log('🚫 Cancel detected!');
    // 执行你的取消逻辑
  });

  return <AgentScopeRuntimeWebUI options={options} />;
}
```

### 已实现

✅ `Chat/index.tsx` - 已集成 `useMessageStatusChange`
✅ `useDirectCancelListener.ts` - 6 种监听方案

### 测试方法

1. 发送一条消息
2. 在响应过程中点击停止按钮
3. 观察控制台输出：
   ```
   🎯 Direct cancel listener triggered!
   🚫 Cancelling current request...
   ```

### 其他方案示例

```tsx
import {
  useLoadingStateChange,
  useMessageStatusChange,
  useDOMMutationObserver,
  useInterceptFinishResponse,
  useKeyboardCancel,
  useCombinedCancelListener
} from './useDirectCancelListener';

// 方案 1：监听 loading 状态
useLoadingStateChange(() => {
  console.log('Loading changed');
});

// 方案 2：监听消息状态（推荐）
useMessageStatusChange(() => {
  console.log('Message status changed');
});

// 方案 6：组合监听（最可靠）
useCombinedCancelListener(() => {
  console.log('Cancel detected (combined)');
});
```

## 原理解释

### 库的取消流程

```javascript
// useChatController.js
handleCancel() {
  finishResponse('interrupted');  // 只改变状态，不触发事件
}

finishResponse(status) {
  currentQARef.current.response.msgStatus = status;  // 设置状态
  setLoading(false);                                    // 改变 loading
  messageHandler.updateMessage(...);                    // 更新消息
}
```

### 监听点的变化

| 监听点 | 变化前 | 变化后 |
|--------|--------|--------|
| loading | `true` | `false` |
| msgStatus | `'streaming'` | `'interrupted'` |
| 消息列表 | `[{...}]` | `[{..., msgStatus: 'interrupted'}]` |

## 相关文件

- `Chat/index.tsx` - 主组件（已集成监听）
- `Chat/Sender/index.ts` - Sender 配置
- `useDirectCancelListener.ts` - 6 种监听方案
- `useCancelController.ts` - 高级控制方案
- `CANCEL_IMPLEMENTATION.md` - 详细文档
