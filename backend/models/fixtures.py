"""
示例数据生成器

提供用于测试和演示的示例人物数据
"""

from datetime import datetime, timedelta
from typing import List, Dict

from .person_models import (
    PersonBaseInfo,
    Relationship,
    Event,
    RecentActivity,
    GenderEnum,
    RelationshipTypeEnum,
    EventCategoryEnum,
    ActivityTypeEnum,
    PersonFullProfile,
)


def generate_sample_person(
    name: str = "张三",
    gender: GenderEnum = GenderEnum.MALE,
    occupation: str = "教授",
    organization: str = "清华大学",
) -> PersonBaseInfo:
    """生成示例人物数据"""
    return PersonBaseInfo(
        name=name,
        name_en=f"{name} Zhang",
        aliases=[f"{name}老"],
        gender=gender,
        birth_date=datetime(1980, 1, 1),
        birth_place="北京",
        nationality="中国",
        occupation=[occupation],
        title="博士生导师",
        organization=organization,
        education=["博士学位"],
        alma_mater="北京大学",
        biography=f"著名{occupation}，在{organization}工作多年",
        summary=f"{organization}{occupation}",
        social_media={
            "twitter": f"@{name.lower()}",
            "weibo": f"https://weibo.com/{name}",
        },
    )


def generate_sample_relationship(
    person_id: str = "person_001",
    related_name: str = "李四",
    rel_type: RelationshipTypeEnum = RelationshipTypeEnum.COLLEAGUE,
) -> Relationship:
    """生成示例关系数据"""
    return Relationship(
        person_id=person_id,
        related_person_name=related_name,
        related_person_id=f"person_{int(person_id.split('_')[1]) + 1}",
        relationship_type=rel_type,
        relationship_description=f"与{related_name}有{rel_type.value}关系",
        start_date=datetime(2020, 1, 1),
        is_active=True,
        strength=4,
    )


def generate_sample_event(
    title: str = "获得国家科学技术进步奖",
    category: EventCategoryEnum = EventCategoryEnum.AWARD,
) -> Event:
    """生成示例事件数据"""
    return Event(
        title=title,
        description=f"因在{title}领域的突出贡献获得该奖项",
        category=category,
        tags=["获奖", category.value],
        event_date=datetime.now() - timedelta(days=30),
        location="北京人民大会堂",
        country="中国",
        participants=[],
        organizations=["国家科技部"],
        impact_level=5,
        significance="国家级重大奖项",
        news_links=[],
        source_count=10,
    )


def generate_sample_activity(
    activity_type: ActivityTypeEnum = ActivityTypeEnum.PUBLICATION,
    title: str = "发表AI领域论文",
) -> RecentActivity:
    """生成示例最近动向数据"""
    return RecentActivity(
        activity_type=activity_type,
        title=title,
        description=f"{title}，在顶级会议发表",
        activity_date=datetime.now() - timedelta(days=7),
        content="论文提出了新的模型架构",
        keywords=["人工智能", "大语言模型", "论文"],
        source_name="Nature",
        source_type="学术期刊",
        sentiment="positive",
        visibility=5,
    )


def generate_sample_profile(
    name: str = "张三",
    rel_count: int = 3,
    event_count: int = 2,
    activity_count: int = 5,
) -> PersonFullProfile:
    """生成完整示例人物档案"""
    person = generate_sample_person(name)

    relationships = [
        generate_sample_relationship(
            person_id=f"person_{i:03d}",
            related_name=f"关系{i}",
            rel_type=list(RelationshipTypeEnum)[i % len(RelationshipTypeEnum)],
        )
        for i in range(rel_count)
    ]

    events = [
        generate_sample_event(
            title=f"事件{i + 1}",
            category=list(EventCategoryEnum)[i % len(EventCategoryEnum)],
        )
        for i in range(event_count)
    ]

    activities = [
        generate_sample_activity(
            activity_type=list(ActivityTypeEnum)[i % len(ActivityTypeEnum)],
            title=f"动向{i + 1}",
        )
        for i in range(activity_count)
    ]

    return PersonFullProfile(
        base_info=person,
        relationships=relationships,
        events=events,
        recent_activities=activities,
    )


def get_sample_data_dict() -> Dict[str, List[Dict]]:
    """获取示例数据字典（适合JSON存储）"""
    from .validators import (
        export_person_to_dict,
        export_relationship_to_dict,
        export_event_to_dict,
        export_activity_to_dict,
    )

    profile = generate_sample_profile()

    return {
        "base_info": [export_person_to_dict(profile.base_info)],
        "relationships": [
            export_relationship_to_dict(r) for r in profile.relationships
        ],
        "events": [export_event_to_dict(e) for e in profile.events],
        "recent_activities": [
            export_activity_to_dict(a) for a in profile.recent_activities
        ],
    }


def generate_multiple_persons(count: int = 10) -> List[PersonBaseInfo]:
    """批量生成示例人物数据"""
    names = [
        "张三",
        "李四",
        "王五",
        "赵六",
        "钱七",
        "孙八",
        "周九",
        "吴十",
        "郑十一",
        "陈十二",
    ]

    occupations = ["教授", "医生", "律师", "工程师", "企业家"]

    return [
        generate_sample_person(
            name=names[i % len(names)],
            gender=GenderEnum.MALE if i % 2 == 0 else GenderEnum.FEMALE,
            occupation=occupations[i % len(occupations)],
            organization=f"机构{i + 1}",
        )
        for i in range(count)
    ]
