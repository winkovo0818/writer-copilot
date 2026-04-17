"""LLM 智能路由"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from app.llm.providers.base import BaseLLMProvider, LLMResponse
from app.llm.providers.dashscope import DashScopeProvider
from app.llm.providers.mock import MockLLMProvider
from app.llm.task_types import TaskType, DEFAULT_ROUTING, MODEL_PRICES
from app.utils.exceptions import LLMInvokeError, LLMTimeoutError, LLMRateLimitError, LLMCostExceededError
from app.utils.logging import get_logger

logger = get_logger("llm_router")


@dataclass
class LLMConstraints:
    """LLM 调用约束"""
    max_cost: Optional[float] = None
    max_latency_ms: Optional[int] = None
    min_quality: Optional[str] = None
    prefer_model: Optional[str] = None
    exclude_models: list[str] = field(default_factory=list)


@dataclass
class LLMRouter:
    """LLM 智能路由器"""

    # 提供者注册表
    providers: dict[str, BaseLLMProvider] = field(default_factory=dict)

    # 每日成本统计
    daily_cost: float = 0.0
    daily_cost_limit: float = 50.0

    # 成本警告阈值（80%）
    cost_warning_threshold: float = 0.8

    def __init__(
        self,
        dashscope_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        ollama_url: Optional[str] = None,
        daily_cost_limit: float = 50.0,
    ):
        # 注册提供者
        if dashscope_key:
            self.providers["dashscope"] = DashScopeProvider(api_key=dashscope_key)

        if ollama_url:
            from app.llm.providers.ollama import OllamaProvider
            self.providers["ollama"] = OllamaProvider(base_url=ollama_url)

        if not self.providers:
            # 默认使用 mock
            self.providers["mock"] = MockLLMProvider()

        self.daily_cost_limit = daily_cost_limit

        logger.info(f"LLMRouter initialized with providers: {list(self.providers.keys())}")

    async def invoke(
        self,
        task_type: TaskType,
        prompt: str,
        constraints: Optional[LLMConstraints] = None,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        智能路由调用

        Args:
            task_type: 任务类型
            prompt: 提示词
            constraints: 调用约束
            stream: 是否流式
            **kwargs: 其他参数

        Returns:
            LLM 响应
        """
        constraints = constraints or LLMConstraints()

        # 1. 检查成本限额
        if self.daily_cost >= self.daily_cost_limit:
            raise LLMCostExceededError(self.daily_cost, self.daily_cost_limit)

        # 2. 选择模型
        routing = DEFAULT_ROUTING.get(task_type, {"primary": "mock", "fallback": None})
        primary_model = constraints.prefer_model or routing["primary"]
        fallback_model = routing.get("fallback")

        # 3. 尝试调用
        last_error = None
        models_to_try = [primary_model]
        if fallback_model and primary_model not in constraints.exclude_models:
            models_to_try.append(fallback_model)

        for model in models_to_try:
            try:
                response = await self._call_model(
                    model=model,
                    prompt=prompt,
                    constraints=constraints,
                    stream=stream,
                    **kwargs
                )

                # 记录成本
                self._record_cost(response)

                return response

            except LLMTimeoutError:
                logger.warning(f"Timeout on {model}, trying fallback")
                last_error = "timeout"

            except LLMRateLimitError:
                logger.warning(f"Rate limit on {model}, trying fallback")
                last_error = "rate_limit"
                await asyncio.sleep(1)  # 等待后重试

            except Exception as e:
                logger.error(f"Error on {model}: {e}")
                last_error = str(e)

        # 所有模型都失败
        raise LLMInvokeError(f"All models failed, last error: {last_error}")

    async def _call_model(
        self,
        model: str,
        prompt: str,
        constraints: LLMConstraints,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """调用具体模型"""
        start_time = time.time()

        # 获取提供者
        provider = self._get_provider(model)

        # 超时检测
        timeout_ms = constraints.max_latency_ms or 60000

        try:
            if stream:
                # 流式调用
                chunks = []
                async for chunk in provider.stream(prompt=prompt, **kwargs):
                    chunks.append(chunk)
                    # 检查超时
                    elapsed_ms = (time.time() - start_time) * 1000
                    if elapsed_ms > timeout_ms:
                        raise LLMTimeoutError(model, timeout_ms)

                content = "".join(chunks)
                return LLMResponse(
                    content=content,
                    model_used=model,
                    input_tokens=len(prompt) // 4,
                    output_tokens=len(content) // 4,
                    cost_cny=0.0,
                    latency_ms=int((time.time() - start_time) * 1000),
                )

            else:
                # 非流式调用
                response = await asyncio.wait_for(
                    provider.invoke(prompt=prompt, **kwargs),
                    timeout=timeout_ms / 1000
                )
                return response

        except asyncio.TimeoutError:
            raise LLMTimeoutError(model, timeout_ms)

    def _get_provider(self, model: str) -> BaseLLMProvider:
        """获取模型对应的提供者"""
        # 根据模型名判断提供者
        if model.startswith("qwen") or model.startswith("text-embedding"):
            return self.providers.get("dashscope", self.providers.get("mock"))
        elif model.startswith("claude"):
            return self.providers.get("anthropic", self.providers.get("mock"))
        elif model == "ollama":
            return self.providers.get("ollama", self.providers.get("mock"))

        # 默认返回第一个
        return next(iter(self.providers.values()))

    def _record_cost(self, response: LLMResponse) -> None:
        """记录成本"""
        self.daily_cost += response.cost_cny

        # 成本警告
        if self.daily_cost >= self.daily_cost_limit * self.cost_warning_threshold:
            logger.warning(f"Daily cost {self.daily_cost:.2f} CNY reached {self.cost_warning_threshold * 100}% of limit")

    def estimate_cost(self, task_type: TaskType, text: str) -> float:
        """估算成本"""
        routing = DEFAULT_ROUTING.get(task_type, {"primary": "mock"})
        model = routing["primary"]
        prices = MODEL_PRICES.get(model, {"input": 0.01, "output": 0.05})

        input_tokens = len(text) // 4
        cost = input_tokens / 1000 * prices["input"]
        return cost


# 全局单例
_router: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """获取路由单例"""
    global _router
    if _router is None:
        from app.config import settings
        _router = LLMRouter(
            dashscope_key=settings.dashscope_api_key or None,
            daily_cost_limit=settings.daily_cost_limit_cny,
        )
    return _router
