# 修复导入错误

## 问题

```
Uncaught SyntaxError: The requested module '/node_modules/.vite/deps/@agentscope-ai_chat.js?v=c33a28ba' does not provide an export named 'useChatAnywhereInput'
```

## 原因

`useChatAnywhereInput` 和 `useChatAnywhereMessages` 不在主入口导出中，而是在子路径中。

## 正确的导入路径

### ❌ 错误的导入

```tsx
import { useChatAnywhereInput, useChatAnywhereMessages } from '@agentscope-ai/chat';
```

### ✅ 正确的导入

```tsx
import { useChatAnywhereInput } from '@agentscope-ai/chat/AgentScopeRuntimeWebUI/core/Context/ChatAnywhereInputContext';
import { useChatAnywhereMessages } from '@agentscope-ai/chat/AgentScopeRuntimeWebUI/core/Context/ChatAnywhereMessagesContext';
```

## 修复的文件

- ✅ `useDirectCancelListener.ts` - 已修复导入路径
- ✅ `Chat/index.tsx` - 删除未使用的导入

## 完整示例

```tsx
import { AgentScopeRuntimeWebUI, IAgentScopeRuntimeWebUIRef } from '@agentscope-ai/chat';
import { useChatAnywhereInput } from '@agentscope-ai/chat/AgentScopeRuntimeWebUI/core/Context/ChatAnywhereInputContext';
import { useChatAnywhereMessages } from '@agentscope-ai/chat/AgentScopeRuntimeWebUI/core/Context/ChatAnywhereMessagesContext';
import { useMessageStatusChange } from './useDirectCancelListener';

function ChatComponent() {
  const loading = useChatAnywhereInput((v) => v.loading);
  const getMessages = useChatAnywhereMessages((v) => v.getMessages);

  useMessageStatusChange(() => {
    console.log('Cancel detected!');
  });

  return <AgentScopeRuntimeWebUI options={options} />;
}
```

## 验证

运行应用，不应该再出现导入错误。
