"""Test SimpleAgent functionality.

This script tests:
1. SimpleAgent basic Q&A without tools
2. SimpleAgent with search tools
3. Agent factory integration
"""

import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv

load_dotenv()

from agent.simple_agent import SimpleAgent, create_simple_agent
from agentscope.model import OpenAIChatModel
from agentscope.message import Msg


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def test_simple_qa():
    """Test SimpleAgent basic Q&A without search tools."""
    logging.info("=" * 60)
    logging.info("Test 1: SimpleAgent Basic Q&A (No Tools)")
    logging.info("=" * 60)

    try:
        # Initialize model
        model_name = os.getenv("model_name")
        model = OpenAIChatModel(
            model_name=model_name,
            api_key=os.getenv("api_key"),
            client_kwargs={"base_url": os.getenv("base_url")},
        )

        # Create SimpleAgent without tools
        agent = SimpleAgent(
            name="test_simple_agent",
            model=model,
            toolkit=None,
            sys_prompt="你是一个友好的AI助手，请简洁地回答问题。",
        )

        # Test questions
        questions = [
            "什么是Python？",
            "人工智能的三个主要分支是什么？",
            "如何煮一个完美的鸡蛋？",
        ]

        for question in questions:
            logging.info(f"\n用户提问: {question}")

            msg = Msg(role="user", content=question)
            response = agent.forward([msg])

            logging.info(f"Agent回答: {response.content}")
            print("-" * 60)

        logging.info("✅ Test 1 passed: Basic Q&A works")

    except Exception as e:
        logging.error(f"❌ Test 1 failed: {e}", exc_info=True)
        return False

    return True


async def test_with_search():
    """Test SimpleAgent with search tools."""
    logging.info("\n" + "=" * 60)
    logging.info("Test 2: SimpleAgent with Search Tools")
    logging.info("=" * 60)

    try:
        # Create SimpleAgent with search
        agent = await create_simple_agent(
            name="search_agent",
            enable_search=True,
            custom_prompt="你是一个AI助手，可以使用搜索工具获取最新信息来回答问题。",
        )

        # Test questions that need current info
        questions = [
            "今天北京的天气怎么样？",
            "最新的AI新闻有什么？",
        ]

        for question in questions:
            logging.info(f"\n用户提问: {question}")

            msg = Msg(role="user", content=question)
            response = agent.forward([msg])

            logging.info(f"Agent回答: {response.content}")
            print("-" * 60)

        logging.info("✅ Test 2 passed: Search-enabled Q&A works")

    except Exception as e:
        logging.error(f"❌ Test 2 failed: {e}", exc_info=True)
        return False

    return True


async def test_agent_factory():
    """Test agent factory integration."""
    logging.info("\n" + "=" * 60)
    logging.info("Test 3: Agent Factory Integration")
    logging.info("=" * 60)

    try:
        from agent.agent_factory import get_agent_type

        # Test agent type detection
        test_cases = [
            ("你好", "simple"),
            ("帮我采集一些数据", "react"),
            ("Python是什么？", "simple"),
            ("搜索最新的科技新闻", "react"),
            ("解释量子计算", "simple"),
        ]

        all_correct = True
        for task, expected_type in test_cases:
            detected_type = get_agent_type(task)
            status = "✅" if detected_type == expected_type else "❌"
            logging.info(
                f"{status} Task: '{task}' -> {detected_type} (expected: {expected_type})"
            )
            if detected_type != expected_type:
                all_correct = False

        if all_correct:
            logging.info("✅ Test 3 passed: Agent type detection works")
        else:
            logging.warning("⚠️ Test 3: Some agent type detections were incorrect")

        return all_correct

    except Exception as e:
        logging.error(f"❌ Test 3 failed: {e}", exc_info=True)
        return False


async def main():
    """Run all tests."""
    logging.info("🚀 Starting SimpleAgent Tests")
    logging.info("=" * 60)

    results = []

    # Run tests
    results.append(await test_simple_qa())
    results.append(await test_with_search())
    results.append(await test_agent_factory())

    # Summary
    logging.info("\n" + "=" * 60)
    logging.info("测试总结")
    logging.info("=" * 60)
    logging.info(f"通过: {sum(results)}/{len(results)}")
    logging.info(f"失败: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        logging.info("🎉 所有测试通过！")
    else:
        logging.warning("⚠️ 部分测试失败")


if __name__ == "__main__":
    asyncio.run(main())
