# 前端任务状态面板 - 工作计划

## TL;DR

> **快速摘要**: 创建前端 TaskStatusPanel 组件，通过 SSE 接收并实时显示任务状态
>
> **交付物**:
> - SSE 解析器 (`sseParser.ts`)
> - 任务状态面板组件 (`TaskStatusPanel/index.tsx`)
> - Chat 组件集成
>
> **预估工作量**: 短期 (Short)
> **并行执行**: 否（顺序执行）
> **关键路径**: sseParser.ts → TaskStatusPanel → Chat 集成

---

## Context

### Original Request
用户希望在对话框右侧添加任务状态信息显示面板，使用 SSE 进行实时更新。

### Interview Summary
**关键讨论**:
- 后端会自己处理 SSE 事件推送，前端只需接收和显示
- 使用现有的 SSE 架构（复用 `/process` 端点）
- 需要实时进度更新和状态持久化

**Research Findings**:
- 前端使用 React 18 + TypeScript
- UI 库：Ant Design 5.29.1 + @agentscope-ai/design
- 样式方案：antd-style (CSS-in-JS)
- 已有 OptionsPanel 作为右侧抽屉参考实现
- 使用 useLocalStorageState 进行状态持久化

---

## Work Objectives

### Core Objective
创建任务状态面板组件，实时接收并显示后端通过 SSE 推送的任务状态信息。

### Concrete Deliverables
- `/frontend/src/utils/sseParser.ts` - SSE 流解析器
- `/frontend/src/components/Chat/TaskStatusPanel/index.tsx` - 任务状态面板组件
- `/frontend/src/components/Chat/index.tsx` - 集成修改

### Definition of Done
- [ ] TaskStatusPanel 显示在聊天界面右侧头部
- [ ] 点击徽章按钮打开右侧抽屉
- [ ] 任务列表显示（类型、状态、进度、时间）
- [ ] 状态标签正确显示（等待中/运行中/已完成/失败）
- [ ] 进度条实时更新（running 状态）
- [ ] 删除任务功能正常
- [ ] localStorage 持久化工作（刷新不丢失）
- [ ] 浏览器控制台测试通过

### Must Have
- ✅ 使用现有的 Drawer 模式（与 OptionsPanel 一致）
- ✅ 使用 CustomEvent 机制进行组件间通信
- ✅ 使用 useLocalStorageState 持久化任务列表
- ✅ 识别 TASK_* 开头的 SSE 事件类型

### Must NOT Have (Guardrails)
- ❌ 不要修改后端代码（后端会自己实现）
- ❌ 不要使用 WebSocket（使用现有 SSE）
- ❌ 不要创建新的状态管理库（使用 useLocalStorageState）
- ❌ 不要添加不必要的依赖包

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO
- **User wants tests**: Manual-only
- **Framework**: None

### Manual Verification

**前端代码验证**:
```bash
# TypeScript 编译检查
cd frontend
npx tsc --noEmit
```

**浏览器测试**:
```javascript
// 1. 在浏览器控制台模拟任务事件
document.dispatchEvent(new CustomEvent('sse-task-event', {
  detail: {
    type: 'TASK_CREATED',
    task_id: 'test-123',
    task_type: '测试任务',
    status: 'pending',
    progress: 0,
    message: '开始执行',
    timestamp: Date.now() / 1000
  }
}));

// 2. 检查任务列表是否更新
// 3. 检查徽章数字是否正确
// 4. 点击徽章，检查抽屉是否打开
// 5. 检查 localStorage 是否持久化
JSON.parse(localStorage.getItem('scrapy-tasks'))

// 6. 刷新页面，检查任务是否保留
location.reload()
```

**UI 交互验证**:
```bash
# Agent 执行步骤：
# 1. 启动开发服务器：cd frontend && npm run dev
# 2. 访问：http://localhost:5173
# 3. 在控制台执行上述测试代码
# 4. 截图验证：
#    - 右侧头部显示徽章按钮
#    - 点击打开抽屉
#    - 任务列表正确显示
#    - 状态标签颜色正确
#    - 进度条显示
#    - 删除功能工作
```

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: 创建 sseParser.ts（无依赖）

Wave 2 (After Task 1):
├── Task 2: 创建 TaskStatusPanel 组件（依赖 sseParser）
└── Task 3: 修改 Chat 组件集成（依赖 sseParser 和 TaskStatusPanel）

Critical Path: Task 1 → Task 2 → Task 3
Sequential execution (no parallelization possible)
```

---

## TODOs

### Task 1: 创建 SSE 解析器

**What to do**:
- 创建 `frontend/src/utils/sseParser.ts` 文件
- 实现 `parseSSEStream` 函数，解析 `data: {...}\n\n` 格式的 SSE 流
- 实现 `dispatchTaskEvent` 辅助函数
- 定义 `SSETaskEvent` 接口

**Must NOT do**:
- 不要使用第三方 SSE 库（原生实现足够）
- 不要修改现有的 SSE 处理逻辑

**Recommended Agent Profile**:
> - **Category**: `quick`
>   - Reason: 单文件创建，逻辑清晰，快速完成
> - **Skills**: N/A（无需特殊技能）
> - **Skills Evaluated but Omitted**:
>   - 无

**Parallelization**:
- **Can Run In Parallel**: YES | NO
- **Parallel Group**: Sequential
- **Blocks**: Task 2, Task 3
- **Blocked By**: None (can start immediately)

**References**:

**Pattern References** (existing code to follow):
- `frontend/src/components/Chat/index.tsx` - 现有的 SSE 处理模式（查找 fetch 和 ReadableStream）
- `SSE_STREAMING.md` - SSE 事件格式文档

**API/Type References** (contracts to implement against):
- `ReadableStreamDefaultReader<Uint8Array>` - 浏览器原生 API
- `TextDecoder` - 浏览器原生解码器

**Test References** (testing patterns to follow):
- 无现有测试，使用浏览器控制台手动测试

**Documentation References** (specs and requirements):
- `SSE_STREAMING.md` - SSE 格式规范

**External References** (libraries and frameworks):
- MDN: ReadableStream - https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream
- MDN: TextDecoder - https://developer.mozilla.org/en-US/docs/Web/API/TextDecoder

**WHY Each Reference Matters**:
- `SSE_STREAMING.md`: 定义了后端 SSE 事件格式（`data: {...}\n\n`），必须遵守
- 现有的 SSE 处理代码：了解如何集成到现有流程中

**Acceptance Criteria**:

**Automated Verification**:
```bash
# Agent executes:
cd frontend && npx tsc --noEmit src/utils/sseParser.ts
# Assert: No TypeScript errors
```

**Code Review Checklist**:
- [ ] `parseSSEStream` 函数签名正确（reader, onEvent, onTaskEvent）
- [ ] 正确使用 TextDecoder 解码 Uint8Array
- [ ] 缓冲区处理正确（保留未完成的行）
- [ ] 识别 `type?.startsWith('TASK_')` 事件
- [ ] 调用 `onTaskEvent` 回调传递任务事件
- [ ] TypeScript 类型定义完整（`SSETaskEvent` 接口）

**Commit**: NO (groups with Task 2, 3)

---

### Task 2: 创建 TaskStatusPanel 组件

**What to do**:
- 创建 `frontend/src/components/Chat/TaskStatusPanel/index.tsx` 文件
- 实现右侧抽屉组件，显示任务列表
- 使用 `useLocalStorageState` 持久化任务列表
- 监听 `sse-task-event` 自定义事件
- 显示任务类型、状态标签、进度条、时间、错误信息
- 实现删除任务、清空已完成、清空所有功能

**Must NOT do**:
- 不要使用 Modal（使用 Drawer）
- 不要创建新的状态管理
- 不要修改样式模式（遵循 OptionsPanel）

**Recommended Agent Profile**:
> - **Category**: `visual-engineering`
>   - Reason: UI 组件开发，需要关注样式、布局、交互
> - **Skills**: `ui-styling`, `frontend-ui-ux`
>   - `ui-styling`: 使用 antd-style 创建样式，Ant Design 组件库
>   - `frontend-ui-ux`: 组件交互设计、状态管理、用户反馈
> - **Skills Evaluated but Omitted**:
>   - `web-frameworks`: 不需要（项目已配置好）

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Sequential (Wave 2)
- **Blocks**: Task 3
- **Blocked By**: Task 1 (需要 sseParser 的类型定义)

**References**:

**Pattern References** (existing code to follow):
- `frontend/src/components/Chat/OptionsPanel/index.tsx:1-27` - Drawer 模式参考
- `frontend/src/components/Chat/OptionsPanel/OptionsEditor.tsx:9-30` - createStyles 样式模式
- `frontend/src/components/Chat/index.tsx:37-40` - useLocalStorageState 使用模式

**API/Type References** (contracts to implement against):
- `SSETaskEvent` from `sseParser.ts` - 任务事件类型
- `useLocalStorageState` from `ahooks` - 状态持久化
- `Drawer` from `@agentscope-ai/design` - 抽屉组件
- `Badge`, `Progress`, `List`, `Tag` from `antd` - UI 组件

**Test References** (testing patterns to follow):
- 无现有测试，手动 UI 测试

**Documentation References** (specs and requirements):
- 无独立文档，参考计划文档

**External References** (libraries and frameworks):
- Ant Design List: https://ant.design/components/list
- Ant Design Progress: https://ant.design/components/progress
- Ant Design Tag: https://ant.design/components/tag
- ahooks useLocalStorageState: https://ahooks.js.org/hooks/use-local-storage-state

**WHY Each Reference Matters**:
- `OptionsPanel/index.tsx`: 展示了 Drawer + IconButton 的标准实现模式
- `OptionsEditor.tsx`: 展示了 createStyles 和布局模式（flex, padding）
- `Chat/index.tsx`: 展示了 useLocalStorageState 的使用方法

**Acceptance Criteria**:

**Automated Verification**:
```bash
# Agent executes:
cd frontend && npx tsc --noEmit src/components/Chat/TaskStatusPanel/index.tsx
# Assert: No TypeScript errors
```

**Manual Verification (Agent executes in browser)**:
```javascript
// 1. 在控制台执行模拟事件
document.dispatchEvent(new CustomEvent('sse-task-event', {
  detail: {
    type: 'TASK_CREATED',
    task_id: 'test-' + Date.now(),
    task_type: '爬虫任务',
    status: 'pending',
    progress: 0,
    message: '开始执行',
    timestamp: Date.now() / 1000
  }
}));

// 2. 检查 UI 更新
// Agent verifies:
// - 徽章数字增加
// - 点击徽章打开抽屉
// - 任务列表显示新任务
// - 状态标签显示"等待中"
// - 截图保存到 .sisyphus/evidence/task-status-panel-1.png

// 3. 测试进度更新
setTimeout(() => {
  document.dispatchEvent(new CustomEvent('sse-task-event', {
    detail: {
      type: 'TASK_PROGRESS',
      task_id: 'test-' + (Date.now() - 2000),
      task_type: '爬虫任务',
      status: 'running',
      progress: 50,
      message: '执行中... 50%',
      timestamp: Date.now() / 1000
    }
  }));
}, 2000);

// Agent verifies:
// - 进度条显示 50%
// - 状态变为"运行中"
// - 截图保存

// 4. 测试完成
setTimeout(() => {
  document.dispatchEvent(new CustomEvent('sse-task-event', {
    detail: {
      type: 'TASK_COMPLETED',
      task_id: 'test-' + (Date.now() - 5000),
      task_type: '爬虫任务',
      status: 'completed',
      progress: 100,
      message: '任务成功',
      timestamp: Date.now() / 1000
    }
  }));
}, 5000);

// Agent verifies:
// - 进度条 100%
// - 状态变为"已完成"
// - 徽章数字减少
// - 截图保存

// 5. 测试 localStorage
localStorage.setItem('scrapy-tasks', JSON.stringify([
  {
    task_id: 'persist-test',
    task_type: '持久化测试',
    status: 'completed',
    progress: 100,
    created_at: Date.now() / 1000,
    updated_at: Date.now() / 1000
  }
]));

// Agent verifies:
// - 刷新页面（location.reload()）
// - 任务仍然存在
// - 截图保存
```

**Code Review Checklist**:
- [ ] 使用 `createStyles` 定义样式
- [ ] 使用 `useLocalStorageState` 持久化任务列表
- [ ] 监听 `sse-task-event` 事件
- [ ] 正确处理任务的创建、更新、删除
- [ ] 状态配置正确（STATUS_CONFIG）
- [ ] 进度条仅在 running 状态显示
- [ ] 徽章显示运行中任务数
- [ ] 删除功能正常
- [ ] 清空已完成/所有功能正常
- [ ] 时间格式化正确

**Commit**: NO (groups with Task 3)

---

### Task 3: 集成到 Chat 组件

**What to do**:
- 修改 `frontend/src/components/Chat/index.tsx`
- 导入 `TaskStatusPanel` 和 `parseSSEStream`
- 将 TaskStatusPanel 添加到 `rightHeader`
- 在 SSE 处理逻辑中添加任务事件分发
- 触发 `CustomEvent('sse-task-event')` 传递任务事件

**Must NOT do**:
- 不要破坏现有的 OptionsPanel 集成
- 不要修改现有的消息处理逻辑
- 不要使用其他事件名称

**Recommended Agent Profile**:
> - **Category**: `quick`
>   - Reason: 简单的集成修改，添加导入和回调
> - **Skills**: N/A（无需特殊技能）
> - **Skills Evaluated but Omitted**:
>   - 无

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Sequential (Wave 2)
- **Blocks**: None (final task)
- **Blocked By**: Task 1, Task 2

**References**:

**Pattern References** (existing code to follow):
- `frontend/src/components/Chat/index.tsx:51-58` - rightHeader 定义位置
- `frontend/src/components/Chat/index.tsx:1-11` - 导入语句位置

**API/Type References** (contracts to implement against):
- `AgentScopeRuntimeWebUI` from `@agentscope-ai/chat` - 主组件
- `IAgentScopeRuntimeWebUIOptions` - options 类型

**Test References** (testing patterns to follow):
- 无现有测试

**Documentation References** (specs and requirements):
- 计划文档中的集成示例

**External References** (libraries and frameworks):
- 无

**WHY Each Reference Matters**:
- `Chat/index.tsx`: 现有的集成模式，了解如何添加组件到 rightHeader

**Acceptance Criteria**:

**Automated Verification**:
```bash
# Agent executes:
cd frontend && npx tsc --noEmit src/components/Chat/index.tsx
# Assert: No TypeScript errors
```

**Manual Verification (Agent executes in browser)**:
```javascript
// 1. 检查组件渲染
// Agent verifies:
// - 右侧头部显示徽章按钮
// - 点击徽章打开抽屉
// - 截图保存到 .sisyphus/evidence/chat-integration-1.png

// 2. 测试端到端流程
document.dispatchEvent(new CustomEvent('sse-task-event', {
  detail: {
    type: 'TASK_CREATED',
    task_id: 'e2e-test',
    task_type: '端到端测试',
    status: 'pending',
    progress: 0,
    message: '开始测试',
    timestamp: Date.now() / 1000
  }
}));

// Agent verifies:
// - 任务事件触发
// - TaskStatusPanel 收到事件
// - UI 更新显示新任务
// - 截图保存

// 3. 测试 localStorage 跨组件同步
// 在一个标签页添加任务，在另一个标签页应该能看到
// Agent verifies:
// - 打开两个标签页
// - 在一个标签页添加任务
// - 另一个标签页自动更新
// - 截图保存
```

**Code Review Checklist**:
- [ ] 正确导入 `TaskStatusPanel` 和 `parseSSEStream`
- [ ] TaskStatusPanel 添加到 `rightHeader` 的 Space 中
- [ ] 在 SSE 处理中添加 `onTaskEvent` 回调
- [ ] 触发 `CustomEvent('sse-task-event')`
- [ ] 事件传递正确的 detail 对象
- [ ] 不破坏现有功能

**Commit**: YES (single commit for all tasks)
- **Message**: `feat(chat): add task status panel with SSE real-time updates`
- **Files**:
  - `frontend/src/utils/sseParser.ts`
  - `frontend/src/components/Chat/TaskStatusPanel/index.tsx`
  - `frontend/src/components/Chat/index.tsx`
- **Pre-commit**: `cd frontend && npx tsc --noEmit`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1, 2, 3 | `feat(chat): add task status panel with SSE real-time updates` | sseParser.ts, TaskStatusPanel/index.tsx, Chat/index.tsx | `npx tsc --noEmit` |

---

## Success Criteria

### Verification Commands
```bash
# TypeScript 编译检查
cd frontend && npx tsc --noEmit

# 启动开发服务器
cd frontend && npm run dev
```

### Final Checklist
- [ ] TaskStatusPanel 显示在右侧头部
- [ ] 点击徽章打开抽屉
- [ ] 任务列表正确显示
- [ ] 状态标签颜色和图标正确
- [ ] 进度条实时更新
- [ ] 删除功能正常
- [ ] localStorage 持久化工作
- [ ] 刷新页面任务不丢失
- [ ] 浏览器控制台测试通过
- [ ] 无 TypeScript 编译错误
- [ ] 现有功能不受影响

---

## Evidence to Capture

**Screenshots to save** (`.sisyphus/evidence/`):
1. `task-status-panel-closed.png` - 关闭状态（徽章按钮）
2. `task-status-panel-open.png` - 打开状态（抽屉显示）
3. `task-status-panel-running.png` - 运行中任务（进度条）
4. `task-status-panel-completed.png` - 已完成任务
5. `task-status-panel-failed.png` - 失败任务
6. `localstorage-persistence.png` - 刷新前后对比

**Terminal output to capture**:
- TypeScript 编译结果（`npx tsc --noEmit`）
- 开发服务器启动日志（`npm run dev`）

---

## Notes

### Backend SSE Event Format (for reference)

后端应该推送以下格式的 SSE 事件：

```
data: {"type": "TASK_CREATED", "task_id": "task_123", "task_type": "scraping", "status": "pending", "progress": 0, "message": "开始执行", "timestamp": 1704067200}

data: {"type": "TASK_PROGRESS", "task_id": "task_123", "task_type": "scraping", "status": "running", "progress": 50, "message": "执行中... 50%", "timestamp": 1704067260}

data: {"type": "TASK_COMPLETED", "task_id": "task_123", "task_type": "scraping", "status": "completed", "progress": 100, "message": "任务成功", "timestamp": 1704067320}

data: {"type": "TASK_FAILED", "task_id": "task_123", "task_type": "scraping", "status": "failed", "progress": 0, "message": "任务失败", "error": "超时", "timestamp": 1704067320}
```

### Integration Points

**关键集成点**：找到现有的 SSE 处理逻辑（可能在 `AgentScopeRuntimeWebUI` 内部），确保任务事件能被正确分发。

**可能的集成位置**：
1. `senderOptions.onSubmit` - 如果发送消息时有 SSE 处理
2. `sessionApi` - 如果会话 API 处理 SSE
3. 自定义 fetch 包装 - 如果直接调用 `/process` 端点

如果 SSE 处理在 `@agentscope-ai/chat` 库内部，可能需要：
- 查看库的配置选项
- 使用库提供的钩子或回调
- 在 `AgentScopeRuntimeWebUI` 的 props 中传递自定义处理器

---

**开始执行**: 运行 `/start-work` 启动实施流程。
