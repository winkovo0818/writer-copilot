"""LLM 提供者抽象"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model_used: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_cny: float = 0.0
    latency_ms: int = 0


class BaseLLMProvider(ABC):
    """LLM 提供者基类"""

    @abstractmethod
    async def invoke(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> LLMResponse:
        """同步调用"""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式调用"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
