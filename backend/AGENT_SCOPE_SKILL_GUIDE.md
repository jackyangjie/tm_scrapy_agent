# AgentScope Skill 使用指南

## 什么是 Skill？

Agent Scope Skill 是一组可以动态加载的指令、脚本和资源，用于在特定任务中提升 agent 性能。每个 skill 包含：

- **SKILL.md**: 必需文件，包含技能元数据和使用说明
- **辅助文件**: 可选的脚本、数据文件、配置文件等

## Skill 目录结构

```
skill_name/
├── SKILL.md          # 必需：技能说明文件（含 YAML Front Matter）
├── helper.py         # 可选：辅助脚本
├── data.json         # 可选：参考数据
└── config.yaml        # 可选：配置文件
```

## SKILL.md 格式要求

SKILL.md 必须以 YAML Front Matter 开头：

```markdown
---
name: skill_name
description: 技能的详细描述，说明该技能能做什么
---

# 技能使用指南

详细的技能说明、使用方法、示例等...

## 注意事项

...

## 示例

...
```

**Front Matter 必需字段**:
- `name`: 技能名称（唯一标识）
- `description`: 技能描述（会显示在 agent 的 system prompt 中）

## 如何注册 Skill

### 在代码中注册

```python
from agentscope.tool import Toolkit
import os

toolkit = Toolkit()

# 注册单个 skill
toolkit.register_agent_skill("/path/to/skill/directory")

# 注册多个 skills
skills = ["web_scraping", "data_extraction"]
for skill_name in skills:
    skill_path = os.path.join(SKILLS_DIR, skill_name)
    if os.path.exists(skill_path):
        toolkit.register_agent_skill(skill_path)
```

### 在 Agent 中使用

```python
from agentscope.agent import ReActAgent
from agentscope.tool import Toolkit

toolkit = Toolkit()

# 注册 skills
toolkit.register_agent_skill("skills/web_scraping")
toolkit.register_agent_skill("skills/data_extraction")

# 创建 agent（自动加载 skill prompt）
agent = ReActAgent(
    name="my_agent",
    sys_prompt="你是一个智能助手",
    model=model,
    toolkit=toolkit,
)

# agent 的 sys_prompt 会自动包含所有注册的 skills
# 实际 prompt = sys_prompt + "\n\n" + agent_skill_prompt
```

## Skill 如何工作

1. **注册阶段**: 调用 `toolkit.register_agent_skill(skill_dir)` 注册技能
2. **加载阶段**: Agent 在创建时读取所有注册的 skills
3. **使用阶段**: Agent 在 system prompt 中看到技能列表
4. **运行阶段**: Agent 根据任务需求选择使用哪些 skills

**注意**: Agent 会自动在 system prompt 中添加 skills 信息，你无需手动添加。

### 生成的 Prompt 结构

```
原始 system prompt
...

# Agent Skills
The agent skills are a collection of folds of instructions, scripts,
and resources that you can load dynamically to improve performance
on specialized tasks. Each agent skill has a `SKILL.md` file in its
folder that describes how to use the skill. If you want to use a
skill, you MUST read its `SKILL.md` file carefully.

## web_scraping
专业的网页抓取技能，包含数据提取、HTML解析和反爬虫处理的专业知识
Check "skills/web_scraping/SKILL.md" for how to use this skill

## data_extraction
数据提取和结构化技能，支持从非结构化文本中提取结构化数据
Check "skills/data_extraction/SKILL.md" for how to use this skill
```

## 实际示例

### 示例 1: 网页抓取 Skill

**目录结构**:
```
skills/web_scraping/
└── SKILL.md
```

**SKILL.md 内容**:
```markdown
---
name: web_scraping
description: 专业的网页抓取技能，包含数据提取、HTML解析和反爬虫处理
---

# Web Scraping 技能使用指南

## 技能概述

本技能提供专业的网页抓取和数据提取能力：
- HTML/CSS 选择器使用
- 数据清洗和验证
- 反爬虫处理
- 异步批量抓取

## 使用方法

### 基本抓取流程

1. 使用 Playwright MCP 工具访问目标 URL
2. 等待页面加载完成
3. 使用 CSS 选择器提取数据
4. 处理分页和动态内容

### 数据提取规则

1. 优先使用语义化标签（如 `<article>`, `<main>`）
2. 降级使用 class 和 id 选择器
3. 提取后进行 `strip()` 和 `normalize()`

### 反爬虫处理

- 设置合理请求间隔（1-3秒）
- 使用浏览器指纹（User-Agent, Accept-Language）
- 模拟人类行为（随机延迟、滚动）

## 常见场景

### 列表页面抓取

```
1. 打开列表页面
2. 等待内容加载
3. 提取所有项目链接
4. 逐个访问详情页
```

### 详情页面抓取

```
1. 识别主要信息容器
2. 提取标题、内容、时间等字段
3. 处理图片和附件
4. 保存到目标格式
```
```

### 示例 2: 数据提取 Skill

**目录结构**:
```
skills/data_extraction/
└── SKILL.md
```

**SKILL.md 内容**:
```markdown
---
name: data_extraction
description: 数据提取和结构化技能，支持从非结构化文本中提取结构化数据
---

# Data Extraction 技能使用指南

## 技能概述

从非结构化文本中提取结构化数据：
- 命名实体识别（人名、地名、机构名）
- 时间日期提取和标准化
- 数据模式识别和提取
- 数据验证和清洗

## 使用方法

### 实体识别

在抓取的文本中识别：
1. **人名**：职务姓名、作者姓名
2. **机构**：政府部门、公司名称
3. **地点**：省市、地址
4. **时间**：日期、时间段、任期

### 数据结构化

将提取的信息组织为结构化格式：
```json
{
  "name": "姓名",
  "title": "职务",
  "organization": "机构",
  "start_date": "开始日期",
  "end_date": "结束日期",
  "source": "数据源"
}
```

## 提取规则

### 职务信息提取

- 职务全名：优先提取完整职务名称
- 职务层级：区分正职、副职、助理
- 部门：提取所属部门或机构

### 时间信息提取

- 标准格式：YYYY-MM-DD, YYYY年MM月DD日
- 相对时间："2023年至今" → start_date: "2023-01-01"
- 模糊时间："近三年" → 需结合上下文推断

### 数据验证

- 必填字段：姓名、职务至少一个
- 格式检查：日期格式、电话号码
- 数据一致性：检查逻辑矛盾

## 使用流程

1. 获取原始文本内容
2. 使用正则表达式或 NLP 技术提取实体
3. 标准化数据格式
4. 验证数据完整性
5. 保存为结构化格式（JSON/CSV/Excel）
```

## 在 ScrapyAgent 中使用

参考 `src/com/trs/agent/scrapy_agent.py` 的实现：

```python
class ScrapyAgent:
    def __init__(self):
        self.base_url = os.getenv("base_url")
        self.api_key = os.getenv("api_key")
        self.model_name = os.getenv("model_name")
        self.agent = None
        self.mcp_clients: dict[str, StdIOStatefulClient] = {}

    async def init(self):
        toolkit = Toolkit()

        # 注册 MCP 客户端
        for name, config in mcp_servers_config.items():
            mcp_client = StdIOStatefulClient(name, **config)
            await mcp_client.connect()
            await toolkit.register_mcp_client(mcp_client)
            self.mcp_clients[name] = mcp_client

        # 注册 Skills
        for skill_name in ["web_scraping", "data_extraction"]:
            skill_path = os.path.join(SKILLS_DIR, skill_name)
            if os.path.exists(skill_path):
                toolkit.register_agent_skill(skill_path)
                logging.info(f"Skill {skill_name} 注册成功 !")

        # 创建 Agent
        self.agent = ReActAgent(
            name="scrapy_agent",
            sys_prompt=scrapy_agent_sys_prompt,
            model=OpenAIChatModel(
                model_name=self.model_name,
                api_key=self.api_key,
                client_kwargs={"base_url": self.base_url},
            ),
            max_iters=5,
            toolkit=toolkit,
            plan_notebook=PlanNotebook(),
            formatter=OpenAIChatFormatter(),
        )
```

## 最佳实践

### 1. Skill 设计原则

- **单一职责**: 每个 skill 专注一个领域
- **清晰描述**: description 要简洁明确
- **详细说明**: SKILL.md 中包含具体使用方法
- **示例丰富**: 提供多种使用场景

### 2. 组织 Skills

```
skills/
├── web_scraping/
│   └── SKILL.md
├── data_extraction/
│   └── SKILL.md
├── text_analysis/
│   └── SKILL.md
└── validation/
    └── SKILL.md
```

### 3. 条件注册

根据任务需求选择性注册 skills：

```python
# 只注册需要的 skills
required_skills = ["web_scraping"]
for skill_name in required_skills:
    skill_path = os.path.join(SKILLS_DIR, skill_name)
    if os.path.exists(skill_path):
        toolkit.register_agent_skill(skill_path)
```

### 4. 动态加载

在运行时根据任务动态加载：

```python
async def load_skills_based_on_task(toolkit: Toolkit, task_type: str):
    skills_mapping = {
        "web_scraping": ["web_scraping", "html_parser"],
        "data_extraction": ["data_extraction", "text_analysis"],
        "validation": ["validation", "quality_check"],
    }

    for skill_name in skills_mapping.get(task_type, []):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        if os.path.exists(skill_path):
            toolkit.register_agent_skill(skill_path)
```

## 常见问题

### Q1: Agent 如何知道应该使用哪个 Skill？

A: Agent 会根据任务需求自动判断。它在 system prompt 中看到所有已注册 skills 的描述，然后选择最相关的技能。

### Q2: Skill 中可以包含代码文件吗？

A: 可以。你可以在 skill 目录中包含任何辅助文件（.py, .json, .yaml 等），并在 SKILL.md 中说明如何使用它们。

### Q3: 如何移除已注册的 Skill？

```python
toolkit.remove_agent_skill("skill_name")
```

### Q4: 可以在运行时动态添加/移除 Skills 吗？

A: 可以。但需要注意：
- 添加 skill 后，新的 agent 实例会包含它
- 已存在的 agent 不会自动更新
- 重新创建 agent 实例以应用变更

### Q5: Skills 会影响性能吗？

A:
- **注册阶段**: 轻微开销（读取文件）
- **prompt 阶段**: 每个 skill 增加约 50-200 tokens
- **运行阶段**: 无性能影响
- **建议**: 只注册必要的 skills

## 进阶用法

### 自定义 Skill Prompt 模板

```python
toolkit = Toolkit(
    agent_skill_instruction="# 可用技能\n你可以使用以下技能...",
    agent_skill_template="### {name}\n{description}\n位置: {dir}"
)
```

### Skill 依赖管理

在 SKILL.md 中说明依赖：

```markdown
---
name: advanced_scraping
description: 高级抓取技能，需要 web_scraping 作为前置技能
---

## 依赖

- 基础技能: web_scraping
- 必需工具: Playwright MCP

## 使用步骤

1. 确保 web_scraping 技能已加载
2. 检查 Playwright MCP 可用
3. 按照以下步骤...
```

## 总结

Agent Scope Skill 提供了一种灵活的方式来扩展 agent 能力：

1. **创建**: 创建包含 SKILL.md 的技能目录
2. **注册**: 使用 `toolkit.register_agent_skill()` 注册
3. **使用**: Agent 自动在 system prompt 中加载技能
4. **扩展**: 根据需求添加更多 skills

通过合理组织和使用 skills，可以让 agent 在不同场景下表现出色，同时保持代码的模块化和可维护性。
