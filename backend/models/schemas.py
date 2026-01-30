"""
Pydantic 数据模型
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    task_id: Optional[str] = None


class TaskCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    progress: int
    message: str


class TaskResultResponse(BaseModel):
    task_id: str
    status: TaskStatus
    data: Optional[List[Dict[str, Any]]] = None
