# AGENTS.md - Development Guidelines for AI Coding Agents

This document provides guidelines and instructions for AI coding agents operating in this repository.

## Project Overview

**tm_scrapy_agent** - An AI-powered web scraping and data collection system built with:
- **AgentScope**: Multi-agent framework for AI-driven data collection
- **Pydantic v2**: Data validation and settings management
- **Pandas**: Data processing and Excel handling
- **Python 3.10+**: With async/await patterns

## Build, Lint, and Test Commands

### Setup and Dependencies

```bash
# Create virtual environment (if not exists)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Install development dependencies
pip install pytest ruff black mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test_models.py

# Run single test function
pytest test_models.py::test_person_base_info

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Formatting and Linting

```bash
# Format code with Black
black src/ tests/

# Check formatting
black src/ tests/ --check

# Lint with Ruff
ruff check src/ tests/

# Lint with specific rules
ruff check src/ --select=E,F,W --ignore=E501

# Type checking with mypy
mypy src/ --ignore-missing-imports
```

### Running the Application

```bash
# Run main application (from backend directory)
python main.py

# Run with custom Excel file
python main.py --file /path/to/data.xlsx
```

## Code Style Guidelines

### Imports

**Standard Library First, Then Third-Party, Then Local:**

```python
# Correct order
import asyncio
import logging
import os
from contextlib import contextmanager, asynccontextmanager
from typing import Any, AsyncGenerator, Optional, List, Dict

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl

from agentscope.agent import ReActAgent
from agentscope.message import Msg

from config import scrapy_agent_sys_prompt, mcp_servers_config
from src.com.trs.service.scrapy_service import ScrapyService
```

**Avoid wildcard imports:**
```python
# Bad
from src.com.trs.models import *

# Good
from src.com.trs.models import PersonBaseInfo, Relationship, Event
```

### Formatting

**Line Length**: Maximum 120 characters (ruff default)

**Blank Lines**:
- Two blank lines between top-level definitions
- One blank line between method definitions in a class
- No blank lines between related one-liners

**String Quotes**: Use double quotes for Chinese text, single quotes for English:
```python
# Good
name: str = "张三"
status: str = 'processing'

# For multi-line strings, use triple quotes
message: str = """
职务中英文名: {row["职务原文名"]}
职务中文名: {row["职务中文名"]}
"""
```

### Type Hints

**Always use type hints for function signatures:**

```python
# Good
async def get_scrapy_agent() -> AsyncGenerator[ScrapyAgent, Any]:
    ...

def clean_person_data(data: Dict[str, Any]) -> Dict[str, Any]:
    ...

class PersonBaseInfo(BaseModel):
    name: str = Field(..., description="人物姓名")
    aliases: List[str] = Field(default_factory=list, description="别名/曾用名")
    gender: Optional[GenderEnum] = Field(default=GenderEnum.UNKNOWN, description="性别")
```

**Use modern syntax (Python 3.10+):**

```python
# Good (Python 3.10+)
def process_data(data: dict[str, Any]) -> None:
    ...

# Avoid
def process_data(data: Dict[str, Any]) -> None:
    ...
```

### Naming Conventions

**Classes**: PascalCase with descriptive names
```python
class ScrapyAgent: ...
class PersonBaseInfo: ...
class RelationshipTypeEnum: ...
```

**Functions and Variables**: snake_case
```python
def clean_person_data(): ...
def validate_chinese_name(): ...
mcp_clients: dict[str, StdIOStatefulClient] = {}
```

**Constants**: UPPER_SNAKE_CASE
```python
API_HOST = "0.0.0.0"
API_PORT = 8000
MAX_ITERS = 20
```

**Private Methods/Attributes**: Leading underscore
```python
class ScrapyAgent:
    def __init__(self):
        self._agent = None
        self._mcp_clients: dict = {}
```

### Pydantic Models

**Use Field for validation and documentation:**

```python
class PersonBaseInfo(BaseModel):
    name: str = Field(..., description="人物姓名")
    email: Optional[str] = Field(None, description="邮箱")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "张三",
                "email": "zhangsan@example.com",
            }
        }
```

**Use enums for fixed values:**

```python
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"
```

### Error Handling

**Use logging instead of print:**

```python
import logging

logger = logging.getLogger(__name__)

# Good
try:
    result = await agent(msg)
except Exception as e:
    logger.error(f"scrapy_agent 运行出错: {e}", exc_info=True)
    raise e
```

**Use specific exception types:**

```python
# Good
from pathlib import Path

def read_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    return file_path.read_text()
```

**Use context managers for resources:**

```python
# Good
async with get_scrapy_agent() as agent:
    await agent.run(row)
```

### Async/Await Patterns

**Use async for I/O operations:**

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

@asynccontextmanager
async def get_scrapy_agent() -> AsyncGenerator[ScrapyAgent, Any]:
    agent = ScrapyAgent()
    await agent.init()
    try:
        yield agent
    finally:
        await agent.close()
```

**Always handle task cancellation:**

```python
async def run_task():
    try:
        while True:
            data = await websocket.receive_text()
            await process(data)
    except asyncio.CancelledError:
        logger.info("Task cancelled")
        raise
    except WebSocketDisconnect:
        logger.info("Client disconnected")
```

### Documentation

**Use docstrings for all public functions and classes:**

```python
class ScrapyAgent:
    """AI-powered web scraping agent for data collection.
    
    This agent integrates with AgentScope to provide intelligent
    data gathering capabilities using MCP tools and custom skills.
    """
    
    async def run(self, row: dict) -> None:
        """Execute data collection task.
        
        Args:
            row: Dictionary containing job information including
                 position name, government session, and data source.
                 
        Returns:
            None. Results are printed to console.
                 
        Raises:
            Exception: If agent execution fails.
        """
```

### Project-Specific Conventions

**Environment Variables**: Load from `.env` file
```python
from dotenv import load_dotenv
load_dotenv()

base_url = os.getenv("base_url")
api_key = os.getenv("api_key")
```

**Configuration**: Centralized in `config.py`
```python
from config import scrapy_agent_sys_prompt, mcp_servers_config
```

**MCP Tools**: Initialize and register in Toolkit
```python
mcp_client = StdIOStatefulClient(name, **config)
await mcp_client.connect()
await toolkit.register_mcp_client(mcp_client)
```

**Skills Directory**: Use relative path from current working directory
```python
SKILLS_DIR = os.path.join(os.getcwd(), "./skills")
```

## File Organization

```
backend/
├── main.py                    # Application entry point
├── config.py                  # Configuration and prompts
├── requirements.txt           # Python dependencies
├── src/com/trs/
│   ├── agent/                # Agent implementations
│   │   └── scrapy_agent.py   # Main ScrapyAgent class
│   ├── service/              # Service layer
│   │   └── scrapy_service.py # Task orchestration
│   ├── tools/                # Utility tools
│   │   └── excel_reader.py   # Excel reading utility
│   ├── models/               # Data models
│   │   ├── person_models.py  # Pydantic models
│   │   ├── validators.py     # Validation functions
│   │   └── fixtures.py       # Sample data generators
│   └── __init__.py
├── skills/                    # AgentScope skills
│   ├── web_scraping/
│   └── data_extraction/
├── data/                      # Input data
│   └── shuju.xlsx
├── logs/                      # Log files
└── test_models.py            # Test file
```

## Common Tasks

**Adding a new model:**
1. Create Pydantic model in `src/com/trs/models/`
2. Add validation functions if needed
3. Export from `src/com/trs/models/__init__.py`
4. Add tests in `test_models.py`

**Adding a new API endpoint:**
1. Create route file in `backend/api/`
2. Import in `backend/main.py`
3. Register with FastAPI app

**Adding a new skill:**
1. Create skill directory in `backend/skills/`
2. Add `SKILL.md` with description
3. Register in `scrapy_agent.py`

## Environment Variables Required

```
base_url: API endpoint URL (e.g., https://open.bigmodel.cn/api/coding/paas/v4)
api_key: API authentication key
model_name: LLM model name (e.g., glm-4.7)
```

## Notes for AI Agents

1. **Preserve existing patterns**: Follow the coding conventions already established in the codebase
2. **Use type hints**: Always add type annotations for function signatures
3. **Handle errors gracefully**: Use try/except with logging, not bare except
4. **Use async/await**: For I/O operations, prefer async patterns
5. **Document thoroughly**: Add docstrings for all public functions and classes
6. **Test your changes**: Run relevant tests after modifications
7. **Don't modify existing tests**: Add new tests instead of changing existing ones
