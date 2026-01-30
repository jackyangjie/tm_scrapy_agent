"""聊天会话相关数据模型"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """消息角色枚举"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """WebSocket 消息类型枚举"""

    MESSAGE = "message"
    TYPING = "typing"
    PING = "ping"
    PONG = "pong"
    SYSTEM = "system"
    ERROR = "error"
    TASK_CREATED = "task_created"
    TASK_UPDATE = "task_update"
    CLOSE = "close"


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ChatMessage(BaseModel):
    """聊天消息模型"""

    role: MessageRole = Field(..., description="消息发送者角色")
    content: str = Field(..., description="消息内容")
    timestamp: Optional[float] = Field(None, description="消息时间戳")
    task_id: Optional[str] = Field(None, description="关联的任务 ID")
    session_id: Optional[str] = Field(None, description="会话 ID")


class WebSocketMessage(BaseModel):
    """WebSocket 通信消息模型"""

    type: MessageType = Field(..., description="消息类型")
    content: Optional[str] = Field(None, description="消息内容")
    role: Optional[MessageRole] = Field(
        None, description="消息角色（仅 type=message 时有效）"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="消息上下文信息")
    task_id: Optional[str] = Field(None, description="任务 ID")
    task_type: Optional[str] = Field(None, description="任务类型")
    success: Optional[bool] = Field(None, description="操作是否成功")
    status: Optional[str] = Field(None, description="状态信息")
    session_id: Optional[str] = Field(None, description="会话 ID")
    timestamp: Optional[float] = Field(None, description="时间戳")


class ChatSession(BaseModel):
    """聊天会话模型"""

    session_id: str = Field(..., description="会话 ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    messages: List[ChatMessage] = Field(
        default_factory=list, description="会话消息列表"
    )
    context: Dict[str, Any] = Field(default_factory=dict, description="会话上下文信息")
    active: bool = Field(default=True, description="会话是否活跃")


class ScrapingContext(BaseModel):
    """爬虫任务上下文模型"""

    position_name: Optional[str] = Field(None, description="职位名称")
    position_name_en: Optional[str] = Field(None, description="职位英文名")
    government_session: Optional[str] = Field(None, description="政府届别")
    data_source: Optional[str] = Field(default="auto", description="数据源类型")
    data_source_url: Optional[str] = Field(None, description="数据源 URL")


class ScrapingTask(BaseModel):
    """爬虫任务模型"""

    task_id: str = Field(..., description="任务 ID")
    task_type: str = Field(..., description="任务类型")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    progress: int = Field(default=0, ge=0, le=100, description="任务进度 0-100")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    context: ScrapingContext = Field(..., description="任务上下文")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息（如果失败）")


class ChatResponse(BaseModel):
    """聊天 API 响应模型"""

    success: bool = Field(..., description="操作是否成功")
    response: str = Field(..., description="AI 响应内容")
    task_id: Optional[str] = Field(None, description="关联的任务 ID（如果创建了任务）")
    task_type: Optional[str] = Field(None, description="任务类型")


class ChatRequest(BaseModel):
    """聊天 API 请求模型"""

    message: str = Field(..., description="用户消息")
    context: Optional[ScrapingContext] = Field(None, description="可选的爬虫任务上下文")


class ClearChatResponse(BaseModel):
    """清空聊天 API 响应模型"""

    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
