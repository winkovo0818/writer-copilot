"""DashScope LLM 提供者"""

import time
from typing import AsyncIterator

import dashscope
from dashscope import Generation

from app.llm.providers.base import BaseLLMProvider, LLMResponse
from app.utils.exceptions import LLMInvokeError, LLMTimeoutError


class DashScopeProvider(BaseLLMProvider):
    """DashScope (阿里云通义) 提供者"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or dashscope.api_key
        self.default_model = "qwen-max"

    async def invoke(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        timeout: int = 60,
        **kwargs
    ) -> LLMResponse:
        """同步调用 DashScope"""
        model = model or self.default_model
        start_time = time.time()

        try:
            response = Generation.call(
                model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens or 2048,
                result_format="message",
                api_key=self.api_key,
                timeout=timeout,
            )

            latency_ms = int((time.time() - start_time) * 1000)

            if response.status_code != 200:
                raise LLMInvokeError(
                    f"DashScope error: {response.message}",
                    model=model
                )

            content = response.output.choices[0].message.content

            # 估算 token（简化，实际应使用 tokenizer）
            input_tokens = len(prompt) // 4
            output_tokens = len(content) // 4
            cost_cny = self._estimate_cost(model, input_tokens, output_tokens)

            return LLMResponse(
                content=content,
                model_used=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_cny=cost_cny,
                latency_ms=latency_ms,
            )

        except Exception as e:
            if "timeout" in str(e).lower():
                raise LLMTimeoutError(model, timeout * 1000)
            raise LLMInvokeError(str(e), model=model)

    async def stream(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式调用 DashScope"""
        model = model or self.default_model

        response = Generation.call(
            model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens or 2048,
            result_format="message",
            api_key=self.api_key,
            stream=True,
        )

        async def generator():
            for chunk in response:
                if chunk.status_code == 200:
                    delta = chunk.output.choices[0].delta
                    if delta:
                        yield delta
                else:
                    raise LLMInvokeError(
                        f"DashScope stream error: {chunk.message}",
                        model=model
                    )

        return generator()

    def get_model_name(self) -> str:
        return self.default_model

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """估算成本（CNY）"""
        # 通义千问价格（参考）
        price_map = {
            "qwen-max": (0.02, 0.06),    # input 元/千token, output 元/千token
            "qwen-plus": (0.004, 0.012),
            "qwen-turbo": (0.002, 0.006),
        }
        rate = price_map.get(model, (0.01, 0.03))
        return (input_tokens / 1000 * rate[0] + output_tokens / 1000 * rate[1])
