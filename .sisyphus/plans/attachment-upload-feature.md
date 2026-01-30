# Plan: Frontend Attachment Upload Feature - Base64 Processing

## TL;DR

> **Quick Summary**: 实现前端附件上传功能，在 `query_func` 中直接处理前端传递的 base64 文件数据，保存到本地存储，生成可访问的文件URL，传递给Agent处理。
>
> **Deliverables**:
> - 修改 `query_func` 处理 `FileContent.file_data` (base64)
> - 新增文件保存辅助函数
> - 新增静态文件访问端点 `/files/{file_id}`
> - 单元测试和集成测试
>
> **Estimated Effort**: Medium
> **Parallel Execution**: NO - sequential
> **Critical Path**: 文件辅助函数 → query_func修改 → 静态文件服务 → 测试

---

## Context

### Original Request
用户要求实现前端附件上传功能，通过 `query_func` 获取 base64 编码的文件数据，不额外添加 `/upload` 接口。

### Interview Summary
**Key Discussions**:
- **上传存储**: 本地存储（`backend/uploads/`）
- **Agent处理**: 传递文件路径/URL，由Agent自主决定如何处理
- **文件类型**: 全部类型（无限制）
- **安全验证**: 基本验证（大小限制10MB + MIME白名单）

**Research Findings**:
- `@agentscope-ai/chat` 组件已配置 `sender.attachments: true`
- 前端自动将文件转换为 `FileContent(file_data="base64...", filename="xxx")`
- `FileContent` 数据模型支持 `file_url`, `file_id`, `filename`, `file_data`
- 后端使用 `agentscope_runtime` 的 `AgentApp` 框架

### Metis Review
**Identified Gaps** (addressed):
- **文件名安全性**: 需要防止路径遍历攻击（如 `../../etc/passwd`）
- **base64 解码错误处理**: 无效的 base64 数据应有优雅的错误处理
- **uploads 目录初始化**: 需要检查并创建 `backend/uploads/`

---

## Work Objectives

### Core Objective
在 `query_func` 中实现 base64 文件数据的处理逻辑，保存到本地存储，生成可访问的文件URL，传递给Agent处理。

### Concrete Deliverables
- 文件保存辅助函数 `save_file_from_base64()`
- 修改 `query_func` 处理 `FileContent`
- 静态文件访问端点 `/files/{file_id}`
- 单元测试：文件验证、保存、访问
- 集成测试：完整的上传流程验证

### Definition of Done
- [ ] 文件通过前端UI上传后，后端正确保存到 `backend/uploads/`
- [ ] 文件可通过 `http://localhost:8080/files/{file_id}` 访问
- [ ] Agent 接收到的消息包含正确的文件路径
- [ ] 所有测试通过（单元测试 + Playwright 集成测试）

### Must Have
- ✅ 支持 base64 和 data URL 两种格式
- ✅ 文件大小限制（10MB）
- ✅ MIME 类型白名单验证
- ✅ 文件名安全性（路径遍历防护）
- ✅ UUID4 文件ID生成
- ✅ 优雅的错误处理和日志记录

### Must NOT Have (Guardrails)
- **不新增 `/upload` 接口**: 直接在 `query_func` 中处理
- **不修改前端代码**: `@agentscope-ai/chat` 已自动处理
- **不实现文件删除**: 不在需求范围内
- **不添加认证到静态文件**: 前端UI需要访问

---

## Verification Strategy (MANDATORY)

> **Test Decision**:
> - **Infrastructure exists**: YES (pytest + Playwright)
> - **User wants tests**: YES (TDD)
> - **Framework**: pytest (unit), Playwright (integration)

### If TDD Enabled

Each TODO follows RED-GREEN-REFACTOR:

**Task Structure**:
1. **RED**: Write failing test first
2. **GREEN**: Implement minimum code to pass
3. **REFACTOR**: Clean up while keeping green

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: 新增文件辅助函数和工具函数
└── Task 2: 测试文件辅助函数

Wave 2 (After Wave 1):
├── Task 3: 修改 query_func 处理 FileContent
└── Task 4: 新增静态文件访问端点

Wave 3 (After Wave 2):
├── Task 5: 集成测试：完整上传流程
└── Task 6: 端到端验证

Critical Path: Task 1 → Task 3 → Task 5
Parallel Speedup: ~25% faster than sequential
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2 | None (基础) |
| 2 | 1 | 3 | None |
| 3 | 1, 2 | 4 | 4 |
| 4 | 1 | 5 | 3 |
| 5 | 3, 4 | 6 | None (集成测试) |
| 6 | 5 | None | None (验证) |

---

## TODOs

- [ ] 1. 新增文件处理工具函数

  **What to do**:
  - 在 `backend/agent/scrapy_agent.py` 顶部新增工具函数
  - 实现 `save_file_from_base64(file_data: str, filename: str) -> dict`
  - 实现 `sanitize_filename(filename: str) -> str` （路径遍历防护）
  - 实现 `validate_mime_type(file_data: bytes) -> bool`
  - 实现 `validate_file_size(file_data: bytes, max_size: int) -> bool`
  - 添加 `UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "../uploads")`

  **Must NOT do**:
  - 不要修改任何其他文件
  - 不要添加额外的 `/upload` 端点

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: 工具函数是纯代码逻辑，单一文件，简单修改
  - **Skills**: []
    - 无需特殊技能，基础 Python 编码

  **Parallelization**:
  - **Can Run In Parallel**: YES | NO
  - **Parallel Group**: Sequential (can start immediately)
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `backend/agent/scrapy_agent.py:20` - SKILLS_DIR 模式（路径拼接）
  - `backend/agent/scrapy_agent.py:58-71` - 模型初始化模式

  **API/Type References** (contracts to implement against):
  - `backend/venv/lib/python3.12/site-packages/agentscope_runtime/engine/schemas/agent_schemas.py:386-401` - FileContent 结构
    - `file_data`: Optional[str] (base64 编码数据)
    - `filename`: Optional[str] (原始文件名)
    - `file_url`: Optional[str] (生成的URL)
    - `file_id`: Optional[str] (生成的ID)

  **Documentation References** (specs and requirements):
  - 草稿 `.sisyphus/drafts/attachment-upload-feature.md` - 技术方案和需求

  **WHY Each Reference Matters**:
  - `SKILLS_DIR` 模式：展示如何在项目中正确拼接路径，避免硬编码
  - `FileContent` 结构：确保正确设置 `file_url` 和 `file_id` 字段

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file created: backend/tests/test_file_utils.py
  - [ ] Test covers: sanitize_filename prevents path traversal
  - [ ] Test covers: validate_file_size rejects >10MB
  - [ ] Test covers: validate_mime_type accepts whitelist
  - [ ] pytest backend/tests/test_file_utils.py → PASS

  **Automated Verification (ALWAYS include, choose by deliverable type)**:
  ```bash
  # Agent runs:
  python -c "from backend.agent.scrapy_agent import save_file_from_base64, sanitize_filename; print('Functions defined')"

  # Assert: Output contains 'Functions defined'
  # Assert: No import errors
  ```

  **Evidence to Capture**:
  - [ ] Python import success output

  **Commit**: YES
  - Message: `feat(utils): add file processing utility functions`
  - Files: `backend/agent/scrapy_agent.py`
  - Pre-commit: `pytest backend/tests/test_file_utils.py`

---

- [ ] 2. 修改 query_func 处理 FileContent

  **What to do**:
  - 修改 `backend/agent/scrapy_agent.py:123-172` 的 `query_func`
  - 在遍历 `msgs.content` 时，检查是否为 `FileContent`
  - 如果 `FileContent.file_data` 存在：
    - 调用 `save_file_from_base64()` 保存文件
    - 更新 `FileContent.file_id` 和 `FileContent.file_url`
    - 记录日志：文件保存成功
  - 如果 `FileContent.file_data` 为 None 且 `file_url` 已存在：
    - 直接使用现有的 `file_url`（可能是历史消息）
  - 如果 `FileContent.file_data` 不在在且 `file_url` 不在在：
    - 记录警告：没有有效的文件数据
  - 对于 `TextContent`：保持现有逻辑

  **Must NOT do**:
  - 不要添加 `/upload` 端点
  - 不要修改前端代码

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 修改现有函数，逻辑清晰
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: YES | NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 4
  - **Blocked By**: Task 1

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `backend/agent/scrapy_agent.py:145-171` - 消息遍历和 agent 调用模式

  **API/Type References** (contracts to implement against):
  - `backend/venv/lib/python3.12/site-packages/agentscope_runtime/engine/schemas/agent_schemas.py:450-548` - Message 类
    - `content: Optional[List[AgentContent]]` - 遍历内容
  - `backend/venv/lib/python3.12/site-packages/agentscope_runtime/engine/schemas/agent_schemas.py:386-401` - FileContent
    - 需要设置 `file_id` 和 `file_url`

  **Documentation References** (specs and requirements):
  - 草稿 `.sisyphus/drafts/attachment-upload-feature.md` - 文件上传流程

  **WHY Each Reference Matters**:
  - 消息遍历模式：展示如何正确遍历和修改消息内容
  - `FileContent` 结构：确保正确设置字段

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file created: backend/tests/test_query_func.py
  - [ ] Test covers: FileContent with base64 saves file
  - [ ] Test covers: FileContent.file_id and file_url updated
  - [ ] Test covers: TextContent works as before
  - [ ] pytest backend/tests/test_query_func.py → PASS

  **Automated Verification (ALWAYS include, choose by deliverable type)**:
  ```bash
  # Agent runs:
  grep -n "isinstance(item, FileContent)" backend/agent/scrapy_agent.py
  # Assert: Output shows match at expected line
  # Assert: File processing logic exists
  ```

  **Evidence to Capture**:
  - [ ] Grep output showing FileContent handling

  **Commit**: YES
  - Message: `feat(agent): add FileContent processing in query_func`
  - Files: `backend/agent/scrapy_agent.py`
  - Pre-commit: `pytest backend/tests/test_query_func.py`

---

- [ ] 3. 新增静态文件访问端点

  **What to do**:
  - 在 `backend/agent/scrapy_agent.py` 新增 `/files/{file_id}` 端点
  - 使用 `@agent_app.endpoint("/files/{file_id}")` 装饰器
  - 读取 `file_id` 对应的文件
  - 返回文件内容（设置正确的 Content-Type）
  - 处理文件不存在情况（返回 404）
  - 使用 `send_file` 或类似的响应方法

  **Must NOT do**:
  - 不要添加认证（前端 UI 需要访问）
  - 不要限制文件类型（已在上传时验证）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 新增简单端点
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: YES | NO
  - **Parallel Group**: Parallel with Task 3
  - **Blocks**: Task 5
  - **Blocked By**: Task 1

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `backend/agent/scrapy_agent.py:89-96` - 现有端点模式
  - `backend/venv/lib/python3.12/site-packages/agentscope_runtime/` - AgentApp endpoint 装饰器用法

  **API/Type References** (contracts to implement against):
  - AgentApp endpoint 装饰器语法

  **Documentation References** (specs and requirements):
  - 草稿 `.sisyphus/drafts/attachment-upload-feature.md` - 静态文件服务要求

  **WHY Each Reference Matters**:
  - 现有端点模式：展示如何正确定义和返回响应

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file created: backend/tests/test_file_endpoint.py
  - [ ] Test covers: GET /files/{file_id} returns file
  - [ ] Test covers: Content-Type header is correct
  - [ ] Test covers: 404 for non-existent file_id
  - [ ] pytest backend/tests/test_file_endpoint.py → PASS

  **Automated Verification (ALWAYS include, choose by deliverable type)**:
  ```bash
  # Agent runs:
  curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/files/nonexistent-id
  # Assert: Exit code 0 and status 404

  # After uploading a file:
  curl -s -o /tmp/test.txt http://localhost:8080/files/{file_id}
  # Assert: File downloaded successfully
  ```

  **Evidence to Capture**:
  - [ ] curl output showing file download
  - [ ] curl output showing 404 for missing file

  **Commit**: YES
  - Message: `feat(endpoint): add static file access endpoint`
  - Files: `backend/agent/scrapy_agent.py`
  - Pre-commit: `pytest backend/tests/test_file_endpoint.py`

---

- [ ] 4. 单元测试：文件辅助函数

  **What to do**:
  - 创建 `backend/tests/test_file_utils.py`
  - 测试 `sanitize_filename()` 防止路径遍历
  - 测试 `validate_file_size()` 正确拒绝 >10MB
  - 测试 `validate_file_size()` 正确接受 ≤10MB
  - 测试 `validate_mime_type()` 接受白名单
  - 测试 `validate_mime_type()` 拒绝黑名单
  - 测试 `save_file_from_base64()` 解码并保存
  - 使用 pytest fixtures 创建测试数据

  **Must NOT do**:
  - 不要测试超出基本验证范围的功能（如病毒扫描）

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 纯测试代码
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: YES | NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 2
  - **Blocked By**: None

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `backend/test_models.py` - 现有测试模式

  **API/Type References** (contracts to implement against):
  - None (纯测试代码）

  **Documentation References** (specs and requirements):
  - `AGENTS.md` - 测试运行命令和风格指南

  **WHY Each Reference Matters**:
  - 现有测试模式：确保测试风格和结构一致

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file created: backend/tests/test_file_utils.py
  - [ ] All 6 tests pass
  - [ ] pytest backend/tests/test_file_utils.py -v → PASS

  **Automated Verification (ALWAYS include, choose by deliverable type)**:
  ```bash
  # Agent runs:
  pytest backend/tests/test_file_utils.py -v --tb=short

  # Assert: All tests pass
  # Assert: Coverage > 80%
  ```

  **Evidence to Capture**:
  - [ ] pytest output showing all tests passed
  - [ ] Coverage report output

  **Commit**: YES
  - Message: `test(utils): add unit tests for file processing functions`
  - Files: `backend/tests/test_file_utils.py`
  - Pre-commit: None

---

- [ ] 5. 集成测试：完整上传流程

  **What to do**:
  - 使用 Playwright 测试前端文件上传流程
  - 参考 `frontend/playwright-tests/file-upload-test.spec.ts` 现有测试
  - 测试：用户选择文件 → 消息包含 FileContent
  - 测试：文件保存到 `backend/uploads/`
  - 测试：Agent 接收到的消息包含 `file_url`
  - 测试：文件可通过 `/files/{file_id}` 访问
  - 添加截图验证步骤

  **Must NOT do**:
  - 不要测试文件删除（不在需求中）
  - 不要测试认证（静态文件不需要）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: 集成测试，需要浏览器交互
  - **Skills**: `["playwright"]`
    - `playwright`: 必需技能，用于浏览器自动化测试

  **Parallelization**:
  - **Can Run In Parallel**: YES | NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Task 3, 4

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `frontend/playwright-tests/file-upload-test.spec.ts:1-261` - 现有 Playwright 测试模式

  **API/Type References** (contracts to implement against):
  - `@agentscope-ai/chat` 组件 API（通过文档）

  **Documentation References** (specs and requirements):
  - 草稿 `.sisyphus/drafts/attachment-upload-feature.md` - 文件上传流程

  **WHY Each Reference Matters**:
  - 现有 Playwright 测试：展示测试结构和断言模式

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] Test file updated: frontend/playwright-tests/file-upload-integration.spec.ts
  - [ ] Test covers: File upload from UI
  - [ ] Test covers: File saved to backend/uploads/
  - [ ] Test covers: Agent receives file_url
  - [ ] Test covers: File accessible via /files/{file_id}
  - [ ] Playwright test passes

  **Automated Verification (ALWAYS include, choose by deliverable type)**:
  ```bash
  # Agent runs:
  npx playwright test frontend/playwright-tests/file-upload-integration.spec.ts --headed

  # Assert: All tests pass
  # Assert: Screenshots saved
  ```

  **Evidence to Capture**:
  - [ ] Playwright test output
  - [ ] Screenshot files
  - [ ] Test report HTML

  **Commit**: YES
  - Message: `test(e2e): add integration test for file upload`
  - Files: `frontend/playwright-tests/file-upload-integration.spec.ts`
  - Pre-commit: None

---

- [ ] 6. 端到端验证

  **What to do**:
  - 运行所有单元测试：`pytest backend/tests/`
  - 运行集成测试：`npx playwright test`
  - 验证所有测试通过
  - 验证功能完整性
  - 生成测试报告

  **Must NOT do**:
  - 不要跳过测试步骤

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: 运行现有测试，验证代码
  - **Skills**: []
    - 无需特殊技能

  **Parallelization**:
  - **Can Run In Parallel**: YES | NO
  - **Parallel Group**: Sequential
  - **Blocks**: None
  - **Blocked By**: Task 5

  **References** (CRITICAL - Be Exhaustive):

  **Pattern References** (existing code to follow):
  - `AGENTS.md:24-30` - 运行测试命令

  **Acceptance Criteria**:

  **If TDD (tests enabled):**
  - [ ] All unit tests pass
  - [ ] All integration tests pass
  - [ ] Coverage ≥ 80%
  - [ ] No critical errors

  **Automated Verification (ALWAYS include, choose by deliverable type)**:
  ```bash
  # Agent runs:
  cd backend && pytest tests/ --cov=src --cov-report=html
  cd frontend && npx playwright test

  # Assert: pytest exit code 0
  # Assert: Playwright exit code 0
  # Assert: Coverage report generated
  ```

  **Evidence to Capture**:
  - [ ] pytest output (all tests passed)
  - [ ] Playwright output (all tests passed)
  - [ ] Coverage report summary

  **Commit**: NO (verification task)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(utils): add file processing utility functions` | `backend/agent/scrapy_agent.py` | `pytest backend/tests/test_file_utils.py` |
| 2 | `feat(agent): add FileContent processing in query_func` | `backend/agent/scrapy_agent.py` | `pytest backend/tests/test_query_func.py` |
| 3 | `feat(endpoint): add static file access endpoint` | `backend/agent/scrapy_agent.py` | `pytest backend/tests/test_file_endpoint.py` |
| 4 | `test(utils): add unit tests for file processing functions` | `backend/tests/test_file_utils.py` | `pytest backend/tests/test_file_utils.py` |
| 5 | `test(e2e): add integration test for file upload` | `frontend/playwright-tests/file-upload-integration.spec.ts` | `npx playwright test` |
| 6 | (no commit - verification) | - | all tests pass |

---

## Success Criteria

### Verification Commands
```bash
# 1. 运行单元测试
cd backend && pytest tests/ -v

# 2. 运行集成测试
cd frontend && npx playwright test

# 3. 手动验证
# 启动后端：cd backend && python main.py
# 启动前端：cd frontend && npm run dev
# 上传文件并通过浏览器检查文件访问
```

### Final Checklist
- [ ] 文件通过前端UI上传后，正确保存到 `backend/uploads/{file_id}/`
- [ ] 文件可通过 `http://localhost:8080/files/{file_id}` 访问
- [ ] Agent 接收到的消息包含正确的 `file_url`
- [ ] 所有单元测试通过（file_utils, query_func, file_endpoint）
- [ ] 所有集成测试通过（Playwright）
- [ ] 文件大小限制生效（>10MB 被拒绝）
- [ ] MIME 类型白名单生效（黑名单类型被拒绝）
- [ ] 文件名安全性生效（路径遍历被阻止）
- [ ] 无控制台错误或未处理的异常
