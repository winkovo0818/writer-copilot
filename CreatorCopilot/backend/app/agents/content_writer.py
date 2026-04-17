"""ContentWriter Agent（流式）"""

from dataclasses import dataclass
from typing import AsyncIterator, Optional

from app.llm.providers.base import BaseLLMProvider


@dataclass
class WritingContext:
    """写作上下文"""
    topic: str
    title: str
    outline: dict
    style_context: Optional[str] = None


class ContentWriterAgent:
    """正文写作 Agent（支持流式输出）"""

    SYSTEM_PROMPT = """你是一个专业的技术博客写作者。请根据给定的大纲，写出一篇完整的技术文章。

要求：
1. 遵循给定的大纲结构
2. 语言专业但易于理解
3. 适当穿插代码示例
4. 段落长度适中，结构清晰
5. 文章要有深度，提供实战价值

请直接开始写作，不需要额外说明。"""

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def write_stream(
        self,
        context: WritingContext,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        流式写作

        Args:
            context: 写作上下文
            temperature: 温度参数

        Yields:
            文本块
        """
        prompt = self._build_prompt(context)

        try:
            async for chunk in self.llm.stream(
                prompt=prompt,
                temperature=temperature,
                max_tokens=4096,
            ):
                yield chunk

        except Exception as e:
            raise Exception(f"Content writing failed: {e}")

    async def write(
        self,
        context: WritingContext,
        temperature: float = 0.7,
    ) -> str:
        """
        非流式写作（一次性返回完整内容）

        Returns:
            完整文章内容
        """
        chunks = []
        async for chunk in self.write_stream(context, temperature):
            chunks.append(chunk)
        return "".join(chunks)

    def _build_prompt(self, context: WritingContext) -> str:
        """构建提示词"""
        parts = [self.SYSTEM_PROMPT, "\n\n"]

        # 标题
        parts.append(f"标题：{context.title}\n\n")

        # 风格上下文
        if context.style_context:
            parts.append(f"风格参考：\n{context.style_context}\n\n")

        # 大纲
        if context.outline:
            parts.append("文章大纲：\n")
            sections = context.outline.get("sections", [])
            for i, section in enumerate(sections, 1):
                heading = section.get("heading", "")
                key_points = section.get("key_points", [])
                parts.append(f"{i}. {heading}\n")
                for point in key_points:
                    parts.append(f"   - {point}\n")
                parts.append("\n")

        parts.append("请开始写作：\n")

        return "".join(parts)
