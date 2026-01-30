"""
人物模型使用示例

测试数据模型、验证工具和示例数据生成器的功能
"""

import json
from datetime import datetime
from src.com.trs.models import (
    PersonBaseInfo,
    Relationship,
    Event,
    RecentActivity,
    PersonFullProfile,
    RelationshipTypeEnum,
    EventCategoryEnum,
    ActivityTypeEnum,
    GenderEnum,
    validate_chinese_name,
    validate_email,
    clean_person_data,
    create_person_from_dict,
    export_person_to_dict,
    generate_sample_person,
    generate_sample_relationship,
    generate_sample_event,
    generate_sample_activity,
    generate_sample_profile,
    get_sample_data_dict,
    generate_multiple_persons,
)


def test_person_base_info():
    """测试人物基础信息模型"""
    person = PersonBaseInfo(
        name="张三",
        name_en="Zhang San",
        aliases=["张老三"],
        gender=GenderEnum.MALE,
        birth_date=datetime(1980, 1, 1),
        birth_place="北京",
        nationality="中国",
        occupation=["教授", "研究员"],
        title="博士生导师",
        organization="清华大学",
        education=["博士学位"],
        alma_mater="北京大学",
        biography="著名学者，在人工智能领域有突出贡献",
        summary="AI领域专家",
    )
    print("1. 人物基础信息测试:")
    print(f"   姓名: {person.name}")
    print(f"   性别: {person.gender.value}")
    print(f"   组织: {person.organization}")
    return person


def test_relationship():
    """测试关系模型"""
    relationship = Relationship(
        person_id="person_001",
        related_person_name="李四",
        related_person_id="person_002",
        relationship_type=RelationshipTypeEnum.COLLEAGUE,
        relationship_description="共同参与了多个研究项目",
        strength=4,
        is_active=True,
    )
    print("\n2. 人物关系测试:")
    print(f"   关系类型: {relationship.relationship_type.value}")
    print(f"   关联人物: {relationship.related_person_name}")
    print(f"   关系强度: {relationship.strength}/5")
    return relationship


def test_event():
    """测试事件模型"""
    event = Event(
        title="获得国家科学技术进步奖",
        description="因在人工智能领域的突出贡献获得该奖项",
        category=EventCategoryEnum.AWARD,
        tags=["获奖", "荣誉", "人工智能"],
        event_date=datetime(2024, 1, 15),
        location="北京人民大会堂",
        country="中国",
        impact_level=5,
        significance="国家级重大奖项",
    )
    print("\n3. 事件模型测试:")
    print(f"   事件标题: {event.title}")
    print(f"   事件类别: {event.category.value}")
    print(f"   影响级别: {event.impact_level}/5")
    return event


def test_recent_activity():
    """测试最近动向模型"""
    activity = RecentActivity(
        activity_type=ActivityTypeEnum.PUBLICATION,
        title="发表AI领域论文",
        description="在顶级会议发表关于大语言模型的研究论文",
        activity_date=datetime(2024, 1, 20),
        content="论文提出了新的模型架构",
        keywords=["人工智能", "大语言模型", "论文"],
        source_name="Nature",
        source_type="学术期刊",
        sentiment="positive",
        visibility=5,
    )
    print("\n4. 最近动向测试:")
    print(f"   活动类型: {activity.activity_type.value}")
    print(f"   标题: {activity.title}")
    print(f"   情感: {activity.sentiment}")
    return activity


def test_validators():
    """测试验证函数"""
    print("\n5. 验证函数测试:")
    print(f"   验证中文名'张三': {validate_chinese_name('张三')}")
    print(f"   验证邮箱'test@example.com': {validate_email('test@example.com')}")
    print(f"   验证非法邮箱'invalid': {validate_email('invalid')}")


def test_data_cleaning():
    """测试数据清洗"""
    raw_data = {
        "name": "  王五  ",
        "email": "wang@example.com",
        "occupation": ["教授", "  研究员  "],
        "gender": "female",
    }
    cleaned = clean_person_data(raw_data)
    print("\n6. 数据清洗测试:")
    print(f"   清洗前: {raw_data}")
    print(f"   清洗后: {cleaned}")


def test_sample_generators():
    """测试示例数据生成器"""
    print("\n7. 示例数据生成器测试:")
    person = generate_sample_person("赵六", GenderEnum.FEMALE, "医生", "协和医院")
    print(f"   生成人物: {person.name} - {person.occupation}")

    relationship = generate_sample_relationship(
        "person_010", "钱七", RelationshipTypeEnum.FRIEND
    )
    print(
        f"   生成关系: 与{relationship.related_person_name}({relationship.relationship_type.value})"
    )

    event = generate_sample_event("获得医学奖", EventCategoryEnum.AWARD)
    print(f"   生成事件: {event.title}")

    activity = generate_sample_activity(ActivityTypeEnum.INTERVIEW, "接受央视采访")
    print(f"   生成动向: {activity.title}")


def test_full_profile():
    """测试完整档案"""
    profile = generate_sample_profile(
        "周八", rel_count=2, event_count=2, activity_count=3
    )
    print("\n8. 完整人物档案测试:")
    print(f"   姓名: {profile.base_info.name}")
    print(f"   关系数量: {len(profile.relationships)}")
    print(f"   事件数量: {len(profile.events)}")
    print(f"   动向数量: {len(profile.recent_activities)}")
    return profile


def test_json_export():
    """测试JSON导出"""
    person = generate_sample_person("吴九")
    data = export_person_to_dict(person)
    # 将datetime转换为字符串
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    print("\n9. JSON导出测试:")
    print(f"   导出类型: {type(data)}")
    print(f"   JSON格式: {json_str[:150]}...")


def test_multiple_persons():
    """测试批量生成"""
    persons = generate_multiple_persons(5)
    print("\n10. 批量生成测试:")
    print(f"    生成数量: {len(persons)}")
    for p in persons:
        print(f"    - {p.name} ({p.gender.value}) - {p.organization}")


def test_sample_data_dict():
    """测试示例数据字典"""
    sample_data = get_sample_data_dict()
    print("\n11. 示例数据字典测试:")
    print(f"    数据类型: {type(sample_data)}")
    print(f"    基础信息数: {len(sample_data['base_info'])}")
    print(f"    关系数: {len(sample_data['relationships'])}")
    print(f"    事件数: {len(sample_data['events'])}")
    print(f"    动向数: {len(sample_data['recent_activities'])}")


if __name__ == "__main__":
    print("=" * 60)
    print("人物模型Schema完整测试")
    print("=" * 60)

    # 运行所有测试
    test_person_base_info()
    test_relationship()
    test_event()
    test_recent_activity()
    test_validators()
    test_data_cleaning()
    test_sample_generators()
    test_full_profile()
    test_json_export()
    test_multiple_persons()
    test_sample_data_dict()

    print("\n" + "=" * 60)
    print("✅ 所有测试通过!")
    print("=" * 60)
