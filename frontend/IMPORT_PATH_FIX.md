# 修复导入路径问题

## 问题

```
Failed to resolve import "@agentscope-ai/chat/AgentScopeRuntimeWebUI/core/Context/ChatAnywhereInputContext"
```

## 原因

Vite 无法正确解析 `@agentscope-ai/chat` 的子路径导入，即使文件存在于 `node_modules` 中。

## 解决方案

创建了**不依赖内部 hook** 的简化版监听器。

### 修改的文件

1. **`useSimpleCancelListener.ts`** - 新建
   - 不使用 `useChatAnywhereInput` 和 `useChatAnywhereMessages`
   - 使用纯 DOM API 和事件监听

2. **`Chat/index.tsx`**
   - 替换 `useMessageStatusChange` 为 `useCombinedCancelListener`

### 提供的监听方案

| 方案 | 说明 |
|------|------|
| `useDOMCancelListener` | 通过 DOM MutationObserver 监听 |
| `useKeyboardCancel` | 监听 ESC 键 |
| `useCustomCancelEvent` | 监听自定义事件 |
| `usePollingCancelListener` | 定时轮询检查状态 |
| `useCombinedCancelListener` | ⭐ 组合以上所有方案 |

## 使用示例

```tsx
import { useCombinedCancelListener } from './useSimpleCancelListener';

function ChatComponent() {
  useCombinedCancelListener(() => {
    console.log('🚫 Cancel detected!');
    senderOptions.onCancel();
  });

  return <AgentScopeRuntimeWebUI options={options} />;
}
```

## 优势

- ✅ 不依赖库的内部 API
- ✅ 不需要复杂的导入路径
- ✅ 更稳定，不受库更新影响
- ✅ 多种监听方式组合，更可靠

## 测试

1. 发送一条消息
2. 在响应过程中：
   - 点击停止按钮
   - 或按 ESC 键
3. 观察控制台输出

```
🎯 Combined cancel listener triggered!
🚫 Cancelling current request...
```
