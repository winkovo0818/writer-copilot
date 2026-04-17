"""Anthropic Claude LLM 提供者"""

import time
from typing import AsyncIterator

import anthropic
from anthropic import AsyncAnthropic

from app.llm.providers.base import BaseLLMProvider, LLMResponse
from app.utils.exceptions import LLMInvokeError, LLMTimeoutError


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude 提供者"""

    def __init__(self, api_key: str | None = None):
        self.client = AsyncAnthropic(api_key=api_key)
        self.default_model = "claude-3-5-sonnet-20241022"

    async def invoke(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> LLMResponse:
        """同步调用 Claude"""
        model = model or self.default_model
        start_time = time.time()

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens or 4096,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )

            latency_ms = int((time.time() - start_time) * 1000)
            content = response.content[0].text

            return LLMResponse(
                content=content,
                model_used=model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cost_cny=self._estimate_cost(model, response.usage.input_tokens, response.usage.output_tokens),
                latency_ms=latency_ms,
            )

        except Exception as e:
            raise LLMInvokeError(str(e), model=model)

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式调用 Claude"""
        model = model or self.default_model

        async def generator():
            async with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens or 4096,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                async for event in stream:
                    if event.type == "content_block_delta":
                        if event.delta.type == "text_delta":
                            yield event.delta.text

        return generator()

    def get_model_name(self) -> str:
        return self.default_model

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """估算成本（CNY）"""
        price_map = {
            "claude-3-5-sonnet-20241022": (0.015, 0.075),
            "claude-3-opus-20240229": (0.05, 0.25),
            "claude-3-haiku-20240307": (0.003, 0.015),
        }
        rate = price_map.get(model, (0.015, 0.075))
        return input_tokens / 1000 * rate[0] + output_tokens / 1000 * rate[1]
