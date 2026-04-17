"""TitleGenerator Agent"""

import json
from dataclasses import dataclass
from typing import Optional

from app.llm.providers.base import BaseLLMProvider, LLMResponse
from app.utils.exceptions import LLMInvokeError


@dataclass
class TitleOption:
    """标题选项"""
    id: int
    text: str
    reason: str
    score: float


class TitleGeneratorAgent:
    """标题生成 Agent"""

    SYSTEM_PROMPT = """你是一个专业的内容标题策划专家。请根据用户选题，生成5个吸引人的文章标题。

要求：
1. 每个标题需要独特，避免重复
2. 长度控制在10-30字
3. 要有吸引力，能引发好奇心或点击欲望
4. 符合技术博客风格

请按以下JSON格式返回：
[
  {"id": 0, "text": "标题1", "reason": "推荐理由", "score": 85.0},
  {"id": 1, "text": "标题2", "reason": "推荐理由", "score": 80.0},
  ...
]"""

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def generate(
        self,
        topic: str,
        feedback_hints: Optional[dict] = None,
        temperature: float = 0.9,
    ) -> list[TitleOption]:
        """
        生成标题候选列表

        Args:
            topic: 选题
            feedback_hints: 可选的反馈提示（包含历史爆款标题特征）
            temperature: 温度参数（高多样性用0.9）

        Returns:
            5个标题选项
        """
        user_prompt = self._build_prompt(topic, feedback_hints)

        try:
            response = await self.llm.invoke(
                prompt=user_prompt,
                temperature=temperature,
                max_tokens=1024,
            )

            titles = self._parse_response(response.content)
            return titles

        except Exception as e:
            raise LLMInvokeError(f"Title generation failed: {e}")

    def _build_prompt(self, topic: str, feedback_hints: Optional[dict] = None) -> str:
        """构建提示词"""
        parts = [f"请为以下选题生成5个标题：\n\n选题：{topic}\n"]

        if feedback_hints:
            parts.append("\n参考反馈（历史爆款标题特征）：")
            if feedback_hints.get("top_patterns"):
                parts.append(f"- 高表现标题模式：{', '.join(feedback_hints['top_patterns'])}")
            if feedback_hints.get("avoid_patterns"):
                parts.append(f"- 需避免的模式：{', '.join(feedback_hints['avoid_patterns'])}")
            if feedback_hints.get("best_length"):
                parts.append(f"- 最佳标题长度：{feedback_hints['best_length']}字")
            if feedback_hints.get("best_emotion"):
                parts.append(f"- 偏好情绪：{feedback_hints['best_emotion']}")

        return "\n".join(parts)

    def _parse_response(self, content: str) -> list[TitleOption]:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON 数组
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)
            titles = [TitleOption(**item) for item in data]
            return titles[:5]  # 确保最多5个

        except json.JSONDecodeError:
            # 降级：返回默认标题
            return [
                TitleOption(
                    id=i,
                    text=f"关于{topic}的深入分析",
                    reason="基于选题生成",
                    score=70.0
                )
                for i in range(5)
            ]
