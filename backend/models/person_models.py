"""
人物信息数据模型

包含人物基础信息、关系、事件和最近动向的Pydantic模型定义
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class GenderEnum(str, Enum):
    """性别枚举"""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class RelationshipTypeEnum(str, Enum):
    """关系类型枚举"""

    FAMILY = "family"  # 家庭关系
    FRIEND = "friend"  # 朋友
    COLLEAGUE = "colleague"  # 同事
    BUSINESS = "business"  # 商业伙伴
    POLITICAL = "political"  # 政治关系
    ACADEMIC = "academic"  # 学术关系
    MENTOR = "mentor"  # 师生/导师关系
    RIVAL = "rival"  # 竞争对手
    PARTNER = "partner"  # 伴侣
    UNKNOWN = "unknown"  # 未知


class EventCategoryEnum(str, Enum):
    """事件类别枚举"""

    CAREER = "career"  # 职业相关
    PERSONAL = "personal"  # 个人生活
    PUBLIC = "public"  # 公开活动
    ACADEMIC = "academic"  # 学术活动
    BUSINESS = "business"  # 商业活动
    POLITICAL = "political"  # 政治活动
    SOCIAL = "social"  # 社交活动
    AWARD = "award"  # 获奖/荣誉
    CONTROVERSY = "controversy"  # 争议事件
    UNKNOWN = "unknown"  # 未知


class ActivityTypeEnum(str, Enum):
    """活动类型枚举"""

    PUBLICATION = "publication"  # 发表作品
    INTERVIEW = "interview"  # 接受采访
    SPEECH = "speech"  # 发表演讲
    MEETING = "meeting"  # 参加会议
    TRAVEL = "travel"  # 出行
    SOCIAL_MEDIA = "social_media"  # 社交媒体活动
    APPOINTMENT = "appointment"  # 任职/任免
    INVESTMENT = "investment"  # 投资
    COLLABORATION = "collaboration"  # 合作
    UNKNOWN = "unknown"  # 未知


class PersonBaseInfo(BaseModel):
    """人物基础信息模型"""

    # 基本信息
    name: str = Field(..., description="人物姓名")
    name_en: Optional[str] = Field(None, description="英文姓名")
    aliases: List[str] = Field(default_factory=list, description="别名/曾用名")
    gender: Optional[GenderEnum] = Field(default=GenderEnum.UNKNOWN, description="性别")

    # 出生信息
    birth_date: Optional[datetime] = Field(None, description="出生日期")
    birth_place: Optional[str] = Field(None, description="出生地点")
    nationality: Optional[str] = Field(None, description="国籍")

    # 职业/身份
    occupation: List[str] = Field(default_factory=list, description="职业列表")
    title: Optional[str] = Field(None, description="头衔/职位")
    organization: Optional[str] = Field(None, description="所属组织/机构")

    # 教育背景
    education: List[str] = Field(default_factory=list, description="教育背景")
    alma_mater: Optional[str] = Field(None, description="母校")

    # 联系方式
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    website: Optional[HttpUrl] = Field(None, description="个人网站")
    social_media: dict = Field(default_factory=dict, description="社交媒体账号")

    # 简介
    biography: Optional[str] = Field(None, description="个人简介")
    summary: Optional[str] = Field(None, description="简要描述")

    # 元数据
    created_at: datetime = Field(
        default_factory=datetime.now, description="记录创建时间"
    )
    updated_at: Optional[datetime] = Field(None, description="记录更新时间")
    source: Optional[str] = Field(None, description="信息来源")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "张三",
                "name_en": "Zhang San",
                "aliases": ["张老三"],
                "gender": "male",
                "birth_date": "1980-01-01T00:00:00",
                "birth_place": "北京",
                "nationality": "中国",
                "occupation": ["教授", "研究员"],
                "title": "博士生导师",
                "organization": "清华大学",
                "education": ["博士学位"],
                "alma_mater": "北京大学",
                "biography": "著名学者，在人工智能领域有突出贡献",
            }
        }


class Relationship(BaseModel):
    """人物关系模型"""

    # 关系主体
    person_id: str = Field(..., description="人物ID")
    related_person_name: str = Field(..., description="关联人物姓名")
    related_person_id: Optional[str] = Field(None, description="关联人物ID")

    # 关系属性
    relationship_type: RelationshipTypeEnum = Field(..., description="关系类型")
    relationship_description: Optional[str] = Field(None, description="关系描述")
    start_date: Optional[datetime] = Field(None, description="关系开始时间")
    end_date: Optional[datetime] = Field(None, description="关系结束时间")
    is_active: bool = Field(default=True, description="关系是否活跃")

    # 关系强度
    strength: Optional[int] = Field(None, ge=1, le=5, description="关系强度(1-5)")

    # 附加信息
    notes: Optional[str] = Field(None, description="备注")
    source: Optional[str] = Field(None, description="信息来源")

    # 元数据
    created_at: datetime = Field(
        default_factory=datetime.now, description="记录创建时间"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "person_id": "person_001",
                "related_person_name": "李四",
                "related_person_id": "person_002",
                "relationship_type": "colleague",
                "relationship_description": "共同参与了多个研究项目",
                "strength": 4,
                "is_active": True,
            }
        }


class Event(BaseModel):
    """事件模型"""

    # 事件基本信息
    event_id: Optional[str] = Field(None, description="事件ID")
    title: str = Field(..., description="事件标题")
    description: Optional[str] = Field(None, description="事件详细描述")

    # 事件分类
    category: EventCategoryEnum = Field(..., description="事件类别")
    tags: List[str] = Field(default_factory=list, description="事件标签")

    # 时间信息
    event_date: Optional[datetime] = Field(None, description="事件发生时间")
    start_date: Optional[datetime] = Field(None, description="事件开始时间")
    end_date: Optional[datetime] = Field(None, description="事件结束时间")

    # 地点信息
    location: Optional[str] = Field(None, description="事件地点")
    country: Optional[str] = Field(None, description="国家")

    # 参与人物
    participants: List[str] = Field(default_factory=list, description="参与人物名单")
    organizations: List[str] = Field(default_factory=list, description="涉及组织")

    # 事件影响
    impact_level: Optional[int] = Field(None, ge=1, le=5, description="影响级别(1-5)")
    significance: Optional[str] = Field(None, description="事件重要性描述")

    # 媒体报道
    news_links: List[HttpUrl] = Field(default_factory=list, description="相关新闻链接")
    source_count: Optional[int] = Field(None, description="媒体报道数量")

    # 元数据
    created_at: datetime = Field(
        default_factory=datetime.now, description="记录创建时间"
    )
    updated_at: Optional[datetime] = Field(None, description="记录更新时间")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "获得国家科学技术进步奖",
                "description": "因在人工智能领域的突出贡献获得该奖项",
                "category": "award",
                "tags": ["获奖", "荣誉", "人工智能"],
                "event_date": "2024-01-15T00:00:00",
                "location": "北京人民大会堂",
                "country": "中国",
                "impact_level": 5,
                "significance": "国家级重大奖项",
            }
        }


class RecentActivity(BaseModel):
    """最近动向模型"""

    # 活动基本信息
    activity_id: Optional[str] = Field(None, description="活动ID")
    activity_type: ActivityTypeEnum = Field(..., description="活动类型")
    title: str = Field(..., description="活动标题")
    description: Optional[str] = Field(None, description="活动详细描述")

    # 时间信息
    activity_date: datetime = Field(..., description="活动发生时间")
    publish_date: Optional[datetime] = Field(None, description="发布时间")

    # 地点信息
    location: Optional[str] = Field(None, description="活动地点")

    # 活动内容
    content: Optional[str] = Field(None, description="活动内容摘要")
    keywords: List[str] = Field(default_factory=list, description="关键词")

    # 关联信息
    related_events: List[str] = Field(
        default_factory=list, description="关联事件ID列表"
    )
    related_persons: List[str] = Field(
        default_factory=list, description="关联人物ID列表"
    )

    # 媒体来源
    source_name: Optional[str] = Field(None, description="信息来源名称")
    source_url: Optional[HttpUrl] = Field(None, description="原始链接")
    source_type: Optional[str] = Field(
        None, description="来源类型(新闻/社交媒体/官方等)"
    )

    # 情感倾向
    sentiment: Optional[str] = Field(None, description="情感倾向(正面/负面/中性)")
    visibility: Optional[int] = Field(
        None, ge=1, le=5, description="可见度/关注度(1-5)"
    )

    # 元数据
    created_at: datetime = Field(
        default_factory=datetime.now, description="记录创建时间"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "activity_type": "publication",
                "title": "发表AI领域论文",
                "description": "在顶级会议发表关于大语言模型的研究论文",
                "activity_date": "2024-01-20T00:00:00",
                "content": "论文提出了新的模型架构",
                "keywords": ["人工智能", "大语言模型", "论文"],
                "source_name": "Nature",
                "source_type": "学术期刊",
                "sentiment": "positive",
                "visibility": 5,
            }
        }


# 组合模型（可选）
class PersonFullProfile(BaseModel):
    """人物完整档案模型"""

    base_info: PersonBaseInfo = Field(..., description="基础信息")
    relationships: List[Relationship] = Field(
        default_factory=list, description="人际关系"
    )
    events: List[Event] = Field(default_factory=list, description="相关事件")
    recent_activities: List[RecentActivity] = Field(
        default_factory=list, description="最近动向"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "base_info": {"name": "张三", "gender": "male", "occupation": ["教授"]},
                "relationships": [],
                "events": [],
                "recent_activities": [],
            }
        }
