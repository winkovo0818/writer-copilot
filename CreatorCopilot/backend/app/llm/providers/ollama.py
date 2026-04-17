"""Ollama LLM 提供者（本地模型）"""

import time
from typing import AsyncIterator

import httpx

from app.llm.providers.base import BaseLLMProvider, LLMResponse
from app.utils.exceptions import LLMInvokeError


class OllamaProvider(BaseLLMProvider):
    """Ollama 本地模型提供者"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip("/")
        self.default_model = model
        self.client = httpx.AsyncClient(timeout=120.0)

    async def invoke(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> LLMResponse:
        """同步调用 Ollama"""
        model = model or self.default_model
        start_time = time.time()

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "options": {
                        "num_predict": max_tokens or 2048,
                    },
                    **kwargs
                }
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = int((time.time() - start_time) * 1000)
            content = data.get("response", "")

            return LLMResponse(
                content=content,
                model_used=model,
                input_tokens=len(prompt) // 4,
                output_tokens=len(content) // 4,
                cost_cny=0.0,  # 本地模型无成本
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
        """流式调用 Ollama"""
        model = model or self.default_model

        async def generator():
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": True,
                    "options": {
                        "num_predict": max_tokens or 2048,
                    },
                    **kwargs
                }
            ) as stream:
                async for line in stream.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue

        return generator()

    def get_model_name(self) -> str:
        return self.default_model
