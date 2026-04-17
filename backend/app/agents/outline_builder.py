"""OutlineBuilder Agent"""

import json
from dataclasses import dataclass, field

from app.llm.providers.base import BaseLLMProvider
from app.utils.exceptions import LLMInvokeError


@dataclass
class OutlineSection:
    """大纲章节"""
    heading: str
    key_points: list[str]
    estimated_words: int


@dataclass
class Outline:
    """文章大纲"""
    sections: list[OutlineSection] = field(default_factory=list)
    total_words: int = 0


class OutlineBuilderAgent:
    """大纲构建 Agent"""

    SYSTEM_PROMPT = """你是一个专业的技术文章结构策划专家。请根据选题和标题，构建一篇结构清晰的技术文章大纲。

要求：
1. 章节数 3-8 个
2. 每个章节有明确的标题和关键要点（2-4 个）
3. 合理分配字数（总字数 1500-3000）
4. 结构层次：引言 → 正文 → 结语

请按以下 JSON 格式返回：
{
  "sections": [
    {
      "heading": "章节标题",
      "key_points": ["要点1", "要点2"],
      "estimated_words": 500
    }
  ],
  "total_words": 2000
}"""

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def build(
        self,
        topic: str,
        title: str,
        target_words: int = 2000,
        temperature: float = 0.5,
    ) -> Outline:
        """
        构建大纲

        Args:
            topic: 选题
            title: 标题
            target_words: 目标字数
            temperature: 温度参数

        Returns:
            文章大纲
        """
        prompt = f"""{self.SYSTEM_PROMPT}

选题：{topic}
标题：{title}
目标字数：{target_words}

请生成大纲："""

        try:
            response = await self.llm.invoke(
                prompt=prompt,
                temperature=temperature,
                max_tokens=2048,
            )

            return self._parse_response(response.content)

        except Exception as e:
            raise LLMInvokeError(f"Outline building failed: {e}")

    def _parse_response(self, content: str) -> Outline:
        """解析 LLM 响应"""
        try:
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)

            sections = [
                OutlineSection(
                    heading=s.get("heading", ""),
                    key_points=s.get("key_points", []),
                    estimated_words=s.get("estimated_words", 0),
                )
                for s in data.get("sections", [])
            ]

            return Outline(
                sections=sections,
                total_words=data.get("total_words", 0),
            )

        except json.JSONDecodeError:
            # 降级返回默认大纲
            return Outline(
                sections=[
                    OutlineSection(heading="引言", key_points=["背景"], estimated_words=200),
                    OutlineSection(heading="主要内容", key_points=["要点"], estimated_words=1500),
                    OutlineSection(heading="总结", key_points=["回顾"], estimated_words=300),
                ],
                total_words=2000,
            )

    def to_dict(self, outline: Outline) -> dict:
        """转换为字典（用于序列化）"""
        return {
            "sections": [
                {
                    "heading": s.heading,
                    "key_points": s.key_points,
                    "estimated_words": s.estimated_words,
                }
                for s in outline.sections
            ],
            "total_words": outline.total_words,
        }
