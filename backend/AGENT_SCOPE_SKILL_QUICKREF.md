# AgentScope Skill 快速参考

## 基本语法

### 1. 创建 Skill

```bash
mkdir skills/my_skill
cd skills/my_skill
touch SKILL.md
```

### 2. SKILL.md 格式

```markdown
---
name: skill_name
description: 简洁描述技能能做什么
---

# 使用指南

详细说明...

## 示例

...
```

### 3. 注册 Skill

```python
toolkit = Toolkit()
toolkit.register_agent_skill("/path/to/skill/directory")
```

### 4. 在 Agent 中使用

```python
agent = ReActAgent(
    name="my_agent",
    sys_prompt="你是一个智能助手",
    model=model,
    toolkit=toolkit,  # 包含已注册的 skills
)
# Agent 自动加载 skill prompt！
```

## 关键点

| 项目 | 说明 |
|------|------|
| **SKILL.md** | 必需文件，必须存在 |
| **Front Matter** | 必需 YAML 格式，包含 name 和 description |
| **name** | 技能唯一标识符 |
| **description** | 技能描述，显示在 agent prompt 中 |
| **自动加载** | Agent 创建时自动添加所有已注册 skills 到 system prompt |
| **条件使用** | Agent 根据任务需求自动判断使用哪些 skills |

## 完整示例

### 步骤 1: 创建 skill 目录和文件

```bash
# 目录结构
skills/
├── web_scraping/
│   └── SKILL.md
└── data_extraction/
    └── SKILL.md
```

### 步骤 2: 编写 SKILL.md

```markdown
---
name: web_scraping
description: 专业的网页抓取技能
---

# 使用指南

1. 使用 Playwright MCP 工具访问网页
2. 等待页面加载
3. 使用 CSS 选择器提取数据
4. 处理分页
```

### 步骤 3: 在代码中注册

```python
import os
from agentscope.tool import Toolkit

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "../skills")

toolkit = Toolkit()

# 注册多个 skills
skills = ["web_scraping", "data_extraction"]
for skill_name in skills:
    skill_path = os.path.join(SKILLS_DIR, skill_name)
    if os.path.exists(skill_path):
        toolkit.register_agent_skill(skill_path)
        print(f"Skill {skill_name} registered!")
```

### 步骤 4: 创建 Agent（自动加载 skills）

```python
from agentscope.agent import ReActAgent

agent = ReActAgent(
    name="scrapy_agent",
    sys_prompt="你是一个智能采集助手",
    model=model,
    toolkit=toolkit,  # 已包含 skills
)
# ✅ Agent 的 system prompt 自动包含所有 skills
```

## 最终 Prompt 效果

Agent 的 system prompt 会自动变成：

```
你是一个智能采集助手

# Agent Skills
The agent skills are a collection of folds of instructions, scripts,
and resources that you can load dynamically to improve performance
on specialized tasks. Each agent skill has a `SKILL.md` file in its
folder that describes how to use this skill. If you want to use a
skill, you MUST read its `SKILL.md` file carefully.

## web_scraping
专业的网页抓取技能
Check "skills/web_scraping/SKILL.md" for how to use this skill

## data_extraction
数据提取和结构化技能
Check "skills/data_extraction/SKILL.md" for how to use this skill
```

## 常用操作

```python
# 注册 skill
toolkit.register_agent_skill("/path/to/skill")

# 移除 skill
toolkit.remove_agent_skill("skill_name")

# 检查 skill 是否已注册
if "skill_name" in toolkit.skills:
    print("Skill 已注册")

# 获取所有 skills 描述
prompt = toolkit.get_agent_skill_prompt()
print(prompt)
```

## 最佳实践

1. **单一职责**: 每个 skill 专注一个功能
2. **描述清晰**: description 要简洁明确
3. **详细说明**: SKILL.md 中包含使用方法
4. **按需注册**: 只注册任务需要的 skills
5. **目录组织**: 将 skills 放在专门的目录中

## 更多信息

- 详细文档: `AGENT_SCOPE_SKILL_GUIDE.md`
- 实际示例: `skills/` 目录
- 官方文档: https://github.com/modelscope/agentscope
