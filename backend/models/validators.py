"""
数据验证工具模块

提供人物信息数据的验证、清洗和转换功能
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import re

from .person_models import (
    PersonBaseInfo,
    Relationship,
    Event,
    RecentActivity,
    GenderEnum,
    RelationshipTypeEnum,
    EventCategoryEnum,
    ActivityTypeEnum,
)


def validate_chinese_name(name: str) -> bool:
    """验证中文姓名格式"""
    if not name:
        return False
    pattern = r"^[\u4e00-\u9fa5]{2,10}$"
    return bool(re.match(pattern, name))


def validate_english_name(name: str) -> bool:
    """验证英文姓名格式"""
    if not name:
        return False
    pattern = r"^[A-Za-z]+(\s[A-Za-z]+){0,4}$"
    return bool(re.match(pattern, name.strip()))


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """验证电话号码格式"""
    if not phone:
        return False
    pattern = r"^[\d\-\+\(\)]{7,20}$"
    return bool(re.match(pattern, phone))


def validate_url(url: str) -> bool:
    """验证URL格式"""
    if not url:
        return False
    pattern = r"^https?://[^\s]+$"
    return bool(re.match(pattern, url))


def clean_text(text: Optional[str]) -> Optional[str]:
    """清洗文本数据"""
    if not text:
        return None
    return text.strip()


def clean_list(items: Optional[List]) -> List:
    """清洗列表数据"""
    if not items:
        return []
    return [clean_text(item) for item in items if item and str(item).strip()]


def clean_person_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """清洗人物基础数据"""
    cleaned = {}

    if data.get("name"):
        cleaned["name"] = clean_text(data["name"])

    if data.get("name_en"):
        cleaned["name_en"] = clean_text(data["name_en"])

    if data.get("aliases"):
        cleaned["aliases"] = clean_list(data["aliases"])

    if data.get("gender"):
        try:
            cleaned["gender"] = GenderEnum(data["gender"])
        except ValueError:
            cleaned["gender"] = GenderEnum.UNKNOWN

    if data.get("birth_place"):
        cleaned["birth_place"] = clean_text(data["birth_place"])

    if data.get("nationality"):
        cleaned["nationality"] = clean_text(data["nationality"])

    if data.get("occupation"):
        cleaned["occupation"] = clean_list(data["occupation"])

    if data.get("title"):
        cleaned["title"] = clean_text(data["title"])

    if data.get("organization"):
        cleaned["organization"] = clean_text(data["organization"])

    if data.get("education"):
        cleaned["education"] = clean_list(data["education"])

    if data.get("alma_mater"):
        cleaned["alma_mater"] = clean_text(data["alma_mater"])

    if data.get("email") and validate_email(data["email"]):
        cleaned["email"] = data["email"]

    if data.get("biography"):
        cleaned["biography"] = clean_text(data["biography"])

    if data.get("summary"):
        cleaned["summary"] = clean_text(data["summary"])

    return cleaned


def clean_relationship_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """清洗关系数据"""
    cleaned = {}

    if data.get("person_id"):
        cleaned["person_id"] = clean_text(data["person_id"])

    if data.get("related_person_name"):
        cleaned["related_person_name"] = clean_text(data["related_person_name"])

    if data.get("related_person_id"):
        cleaned["related_person_id"] = clean_text(data["related_person_id"])

    if data.get("relationship_type"):
        try:
            cleaned["relationship_type"] = RelationshipTypeEnum(
                data["relationship_type"]
            )
        except ValueError:
            cleaned["relationship_type"] = RelationshipTypeEnum.UNKNOWN

    if data.get("relationship_description"):
        cleaned["relationship_description"] = clean_text(
            data["relationship_description"]
        )

    if data.get("strength") and 1 <= int(data["strength"]) <= 5:
        cleaned["strength"] = int(data["strength"])

    if data.get("notes"):
        cleaned["notes"] = clean_text(data["notes"])

    return cleaned


def clean_event_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """清洗事件数据"""
    cleaned = {}

    if data.get("event_id"):
        cleaned["event_id"] = clean_text(data["event_id"])

    if data.get("title"):
        cleaned["title"] = clean_text(data["title"])

    if data.get("description"):
        cleaned["description"] = clean_text(data["description"])

    if data.get("category"):
        try:
            cleaned["category"] = EventCategoryEnum(data["category"])
        except ValueError:
            cleaned["category"] = EventCategoryEnum.UNKNOWN

    if data.get("tags"):
        cleaned["tags"] = clean_list(data["tags"])

    if data.get("location"):
        cleaned["location"] = clean_text(data["location"])

    if data.get("country"):
        cleaned["country"] = clean_text(data["country"])

    if data.get("participants"):
        cleaned["participants"] = clean_list(data["participants"])

    if data.get("organizations"):
        cleaned["organizations"] = clean_list(data["organizations"])

    if data.get("impact_level") and 1 <= int(data["impact_level"]) <= 5:
        cleaned["impact_level"] = int(data["impact_level"])

    if data.get("significance"):
        cleaned["significance"] = clean_text(data["significance"])

    if data.get("news_links"):
        cleaned["news_links"] = data["news_links"]

    return cleaned


def clean_activity_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """清洗最近动向数据"""
    cleaned = {}

    if data.get("activity_id"):
        cleaned["activity_id"] = clean_text(data["activity_id"])

    if data.get("activity_type"):
        try:
            cleaned["activity_type"] = ActivityTypeEnum(data["activity_type"])
        except ValueError:
            cleaned["activity_type"] = ActivityTypeEnum.UNKNOWN

    if data.get("title"):
        cleaned["title"] = clean_text(data["title"])

    if data.get("description"):
        cleaned["description"] = clean_text(data["description"])

    if data.get("location"):
        cleaned["location"] = clean_text(data["location"])

    if data.get("content"):
        cleaned["content"] = clean_text(data["content"])

    if data.get("keywords"):
        cleaned["keywords"] = clean_list(data["keywords"])

    if data.get("related_events"):
        cleaned["related_events"] = clean_list(data["related_events"])

    if data.get("related_persons"):
        cleaned["related_persons"] = clean_list(data["related_persons"])

    if data.get("source_name"):
        cleaned["source_name"] = clean_text(data["source_name"])

    if data.get("source_type"):
        cleaned["source_type"] = clean_text(data["source_type"])

    if data.get("sentiment"):
        cleaned["sentiment"] = clean_text(data["sentiment"])

    if data.get("visibility") and 1 <= int(data["visibility"]) <= 5:
        cleaned["visibility"] = int(data["visibility"])

    return cleaned


def create_person_from_dict(data: Dict[str, Any]) -> PersonBaseInfo:
    """从字典创建人物模型"""
    cleaned = clean_person_data(data)
    return PersonBaseInfo(**cleaned)


def create_relationship_from_dict(data: Dict[str, Any]) -> Relationship:
    """从字典创建关系模型"""
    cleaned = clean_relationship_data(data)
    return Relationship(**cleaned)


def create_event_from_dict(data: Dict[str, Any]) -> Event:
    """从字典创建事件模型"""
    cleaned = clean_event_data(data)
    return Event(**cleaned)


def create_activity_from_dict(data: Dict[str, Any]) -> RecentActivity:
    """从字典创建最近动向模型"""
    cleaned = clean_activity_data(data)
    return RecentActivity(**cleaned)


def export_person_to_dict(person: PersonBaseInfo) -> Dict[str, Any]:
    """导出人物数据为字典"""
    return person.dict()


def export_relationship_to_dict(relationship: Relationship) -> Dict[str, Any]:
    """导出关系数据为字典"""
    return relationship.dict()


def export_event_to_dict(event: Event) -> Dict[str, Any]:
    """导出事件数据为字典"""
    return event.dict()


def export_activity_to_dict(activity: RecentActivity) -> Dict[str, Any]:
    """导出最近动向数据为字典"""
    return activity.dict()
