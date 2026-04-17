"""TopicAnalyzer Agent"""

import json
from dataclasses import dataclass

from app.llm.providers.base import BaseLLMProvider
from app.utils.exceptions import LLMInvokeError


@dataclass
class TopicAnalysis:
    """选题分析结果"""
    core_theme: str
    target_audience: str
    key_points: list[str]
    writing_suggestions: str


class TopicAnalyzerAgent:
    """选题分析 Agent"""

    SYSTEM_PROMPT = """你是一个专业的内容策划专家。请分析用户提供的选题，提取核心主题、目标受众、关键要点，并给出写作建议。

请按以下 JSON 格式返回：
{
  "core_theme": "核心主题（一句话概括）",
  "target_audience": "目标受众描述",
  "key_points": ["要点1", "要点2", "要点3"],
  "writing_suggestions": "写作建议（100字以内）"
}"""

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def analyze(self, topic: str) -> TopicAnalysis:
        """
        分析选题

        Args:
            topic: 选题

        Returns:
            分析结果
        """
        prompt = f"{self.SYSTEM_PROMPT}\n\n选题：{topic}"

        try:
            response = await self.llm.invoke(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1024,
            )

            return self._parse_response(response.content)

        except Exception as e:
            raise LLMInvokeError(f"Topic analysis failed: {e}")

    def _parse_response(self, content: str) -> TopicAnalysis:
        """解析 LLM 响应"""
        try:
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)
            return TopicAnalysis(
                core_theme=data.get("core_theme", ""),
                target_audience=data.get("target_audience", ""),
                key_points=data.get("key_points", []),
                writing_suggestions=data.get("writing_suggestions", ""),
            )

        except json.JSONDecodeError:
            # 降级返回
            return TopicAnalysis(
                core_theme=content[:50],
                target_audience="技术开发者",
                key_points=["待分析"],
                writing_suggestions="",
            )
