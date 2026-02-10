"""SimpleAgent 使用示例

本文档展示如何使用 SimpleAgent 进行简单问答任务。
"""

import asyncio
import logging
from agentscope.message import Msg
from agent.simple_agent import SimpleAgent, create_simple_agent
from agent.agent_factory import get_agent_type
from agentscope.model import OpenAIChatModel


async def example_1_basic_qa():
    """示例1：基础问答（无工具）"""
    # 初始化模型
    model = OpenAIChatModel(
        model_name="glm-4.7",
        api_key="your-api-key",
        client_kwargs={"base_url": "https://open.bigmodel.cn/api/coding/paas/v4"},
    )

    # 创建 SimpleAgent
    agent = SimpleAgent(
        name="qa_bot",
        model=model,
        toolkit=None,  # 不使用工具
    )

    # 进行问答
    question = Msg(role="user", content="什么是人工智能？")
    answer = agent.forward([question])

    print(f"问题: {question.content}")
    print(f"回答: {answer.content}")


async def example_2_with_search():
    """示例2：带搜索功能的问答"""
    # 创建带搜索功能的 SimpleAgent
    agent = await create_simple_agent(
        name="search_bot",
        enable_search=True,  # 启用搜索工具
    )

    # 问答
    questions = [
        "今天北京的天气怎么样？",
        "最新的AI发展动态是什么？",
    ]

    for q in questions:
        question = Msg(role="user", content=q)
        answer = agent.forward([question])
        print(f"\n问题: {q}")
        print(f"回答: {answer.content}")


async def example_3_custom_prompt():
    """示例3：自定义系统提示词"""
    model = OpenAIChatModel(
        model_name="glm-4.7",
        api_key="your-api-key",
        client_kwargs={"base_url": "your-base-url"},
    )

    # 自定义提示词
    custom_prompt = """你是一个专业的编程助手。
    请用简洁的语言回答编程相关问题。
    如果问题涉及代码，请提供简单的代码示例。
    """

    agent = SimpleAgent(
        name="coding_assistant",
        model=model,
        sys_prompt=custom_prompt,
    )

    question = Msg(role="user", content="Python中如何读取文件？")
    answer = agent.forward([question])

    print(f"问题: {question.content}")
    print(f"回答: {answer.content}")


async def example_4_agent_selection():
    """示例4：根据任务类型选择合适的 Agent"""
    tasks = [
        "你好",  # 简单问答 -> SimpleAgent
        "帮我采集一些网页数据",  # 复杂任务 -> ReActAgent
        "Python是什么？",  # 简单问答 -> SimpleAgent
    ]

    for task in tasks:
        agent_type = get_agent_type(task)
        print(f"任务: {task}")
        print(f"推荐Agent类型: {agent_type}")
        print("-" * 60)


async def example_5_conversation():
    """示例5：多轮对话"""
    agent = await create_simple_agent(
        name="chat_bot",
        enable_search=False,
    )

    # 模拟多轮对话
    conversation = [
        "我叫小明",
        "我刚才说我叫什么？",
        "我喜欢什么颜色？",
    ]

    history = []
    for user_input in conversation:
        # 添加用户消息
        user_msg = Msg(role="user", content=user_input)
        history.append(user_msg)

        # 获取回复
        response = agent.forward(history)
        print(f"\n用户: {user_input}")
        print(f"助手: {response.content}")

        # 添加助手回复到历史
        history.append(response)


async def main():
    """运行所有示例"""
    print("=" * 80)
    print("SimpleAgent 使用示例")
    print("=" * 80)

    print("\n示例1：基础问答")
    print("-" * 80)
    # await example_1_basic_qa()

    print("\n示例2：带搜索功能")
    print("-" * 80)
    # await example_2_with_search()

    print("\n示例3：自定义提示词")
    print("-" * 80)
    # await example_3_custom_prompt()

    print("\n示例4：Agent类型选择")
    print("-" * 80)
    await example_4_agent_selection()

    print("\n示例5：多轮对话")
    print("-" * 80)
    # await example_5_conversation()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
