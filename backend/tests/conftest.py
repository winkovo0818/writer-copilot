"""Pytest 配置和 Fixtures"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_llm():
    """Mock LLM 客户端"""
    mock = MagicMock()
    mock.invoke = AsyncMock(return_value="mock response")
    mock.stream = AsyncMock(return_value=async_mock_stream())
    mock.call_count = 0
    return mock


async def async_mock_stream():
    """Mock 异步流式响应"""
    async def generator():
        yield "chunk1"
        yield "chunk2"
        yield "chunk3"
    return generator()


@pytest.fixture
def sample_topic():
    """样例选题"""
    return "LangGraph 的 Checkpoint 机制"


@pytest.fixture
def sample_article_content():
    """样例文章内容"""
    return """# LangGraph Checkpoint 机制详解

本文将深入探讨 LangGraph 的 Checkpoint 机制...

## 什么是 Checkpoint

Checkpoint 是 LangGraph 中的状态保存机制...
"""
