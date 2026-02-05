# 通过监听输入框上下文状态实现取消监听

## 核心思路

由于无法直接导入 `ChatAnywhereInputContext`，我们通过**观察 UI 变化**来间接监听 Context 状态。

## 原理

```
ChatAnywhereInputContext.loading = true  →  UI 更新  →  停止按钮出现
                                              →  发送按钮禁用
                                              →  输入框只读

ChatAnywhereInputContext.loading = false →  UI 更新  →  停止按钮消失
                                              →  发送按钮启用
                                              →  输入框可编辑
```

通过监听这些 UI 变化，我们可以推断出 Context 的状态变化。

## 实现方案

### 方案对比

| 方案 | 可靠性 | 性能 | 复杂度 | 推荐度 |
|------|--------|------|--------|--------|
| `useAgentScopeStateListener` | ⭐⭐⭐⭐⭐ | 中 | 中 | ⭐⭐⭐⭐⭐ |
| `useSimpleStateListener` | ⭐⭐⭐⭐ | 高 | 低 | ⭐⭐⭐⭐ |
| `useAdvancedStateListener` | ⭐⭐⭐⭐⭐ | 中 | 中 | ⭐⭐⭐⭐⭐ |

### 推荐：useAgentScopeStateListener

**监听以下 UI 指标**：
1. 停止按钮出现/消失
2. 发送按钮禁用/启用
3. Loading spinner
4. 输入框只读状态

**组合使用**：
- MutationObserver - 监听 DOM 变化
- 定时检查 - 作为备选方案

## 使用方法

```tsx
import { useAgentScopeStateListener } from './useAgentScopeListener';

function ChatComponent() {
  useAgentScopeStateListener(() => {
    console.log('🚫 Cancel detected via context state!');
    senderOptions.onCancel();
  });

  return <AgentScopeRuntimeWebUI options={options} />;
}
```

## 其他方案

### 1. 简化版（性能更好）

```tsx
import { useSimpleStateListener } from './useAgentScopeListener';

useSimpleStateListener(() => {
  console.log('Cancel detected!');
});
```

只监听关键元素（停止按钮和发送按钮），性能更好。

### 2. 高级版（含键盘支持）

```tsx
import { useAdvancedStateListener } from './useAgentScopeListener';

useAdvancedStateListener(() => {
  console.log('Cancel detected!');
});
```

包含：
- DOM 监听
- ESC 键监听
- 定时检查

## 优势

- ✅ 不依赖库的内部 API
- ✅ 不需要复杂的导入路径
- ✅ 通过 UI 变化准确反映状态
- ✅ 多重保障（DOM + 定时 + 键盘）
- ✅ 性能可控（可调整监听范围）

## 工作流程

```
用户点击停止按钮
    ↓
库调用 handleCancel()
    ↓
库设置 loading = false
    ↓
React 更新 UI
    ↓
MutationObserver 检测到变化
    ↓
触发你的 onCancel 回调
    ↓
执行自定义取消逻辑（abortController.abort()）
```

## 测试

1. 发送一条消息
2. 在响应过程中点击停止按钮
3. 观察控制台：
   ```
   🎯 AgentScope state listener triggered!
   🚫 Cancelling current request...
   🚫 Request was cancelled
   ```

## 相关文件

- `useAgentScopeListener.ts` - Context 状态监听实现
- `useSimpleCancelListener.ts` - 通用 DOM 监听
- `useDirectCancelListener.ts` - 直接监听（需要修复导入）
