"""LLM 路由单元测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.llm.router import LLMRouter, LLMConstraints
from app.llm.task_types import TaskType
from app.llm.providers.mock import MockLLMProvider
from app.llm.providers.base import LLMResponse


@pytest.fixture
def router():
    """测试路由"""
    return LLMRouter(daily_cost_limit=50.0)


@pytest.fixture
def mock_provider():
    """Mock 提供者"""
    provider = MockLLMProvider()
    provider.set_responses(["test response"])
    return provider


@pytest.mark.asyncio
async def test_router_invoke_basic(router):
    """测试基本调用"""
    response = await router.invoke(
        task_type=TaskType.TOPIC_ANALYZE,
        prompt="test prompt",
    )
    assert response.content == "test response"
    assert router.daily_cost >= 0


@pytest.mark.asyncio
async def test_router_invoke_with_constraints(router):
    """测试带约束调用"""
    constraints = LLMConstraints(
        max_latency_ms=5000,
        prefer_model="qwen-plus",
    )
    response = await router.invoke(
        task_type=TaskType.TITLE_GENERATE,
        prompt="test",
        constraints=constraints,
    )
    assert response is not None


@pytest.mark.asyncio
async def test_router_cost_tracking(router):
    """测试成本追踪"""
    initial_cost = router.daily_cost

    await router.invoke(TaskType.TOPIC_ANALYZE, "test")

    assert router.daily_cost >= initial_cost


@pytest.mark.asyncio
async def test_router_estimate_cost(router):
    """测试成本估算"""
    cost = router.estimate_cost(TaskType.TOPIC_ANALYZE, "test text")
    assert cost >= 0


def test_router_default_routing():
    """测试默认路由配置"""
    from app.llm.task_types import DEFAULT_ROUTING

    assert TaskType.TOPIC_ANALYZE in DEFAULT_ROUTING
    assert DEFAULT_ROUTING[TaskType.TOPIC_ANALYZE]["primary"] == "qwen-plus"

    assert TaskType.CONTENT_WRITE in DEFAULT_ROUTING
    assert DEFAULT_ROUTING[TaskType.CONTENT_WRITE]["primary"] == "qwen-max"
