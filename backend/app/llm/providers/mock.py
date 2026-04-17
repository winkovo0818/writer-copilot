"""Mock LLM 提供者（用于测试）"""

import asyncio
import time
from typing import AsyncIterator
from dataclasses import dataclass, field

from app.llm.providers.base import BaseLLMProvider, LLMResponse


@dataclass
class MockLLMProvider(BaseLLMProvider):
    """Mock LLM 提供者"""
    responses: list[str] = field(default_factory=list)
    call_count: int = 0
    default_model: str = "mock-model"

    def set_responses(self, responses: list[str]) -> None:
        """设置响应队列"""
        self.responses = responses
        self.call_count = 0

    async def invoke(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> LLMResponse:
        """同步调用"""
        self.call_count += 1
        await asyncio.sleep(0.01)  # 模拟延迟

        if self.responses:
            content = self.responses[self.call_count - 1] if self.call_count <= len(self.responses) else "mock response"
        else:
            content = f"Mock response for: {prompt[:50]}..."

        return LLMResponse(
            content=content,
            model_used=self.default_model,
            input_tokens=len(prompt) // 4,
            output_tokens=len(content) // 4,
            cost_cny=0.001,
            latency_ms=10,
        )

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式调用"""
        self.call_count += 1
        base_content = f"Mock stream for: {prompt[:30]}..."

        async def generator():
            for i, char in enumerate(base_content):
                await asyncio.sleep(0.001)
                yield char

        return generator()

    def get_model_name(self) -> str:
        return self.default_model
