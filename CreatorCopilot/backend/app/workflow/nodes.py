"""LangGraph 工作流节点（由 graph 通过工厂注入 llm / 依赖）"""

from __future__ import annotations

from app.agents.content_writer import ContentWriterAgent, WritingContext
from app.agents.outline_builder import OutlineBuilderAgent
from app.agents.title_generator import TitleGeneratorAgent
from app.agents.topic_analyzer import TopicAnalyzerAgent, TopicAnalysis
from app.llm.providers.base import BaseLLMProvider
from app.strategies.image_selector import ImageSelectorAgent, ImageResult
from app.workflow.state import ArticleState


def make_analyze_node(llm: BaseLLMProvider):
    async def analyze_node(state: ArticleState) -> dict:
        agent = TopicAnalyzerAgent(llm)
        analysis: TopicAnalysis = await agent.analyze(state["topic"])

        return {
            "analysis": {
                "core_theme": analysis.core_theme,
                "target_audience": analysis.target_audience,
                "key_points": analysis.key_points,
                "writing_suggestions": analysis.writing_suggestions,
            },
            "current_node": "analyze",
            "history": ["analyze"],
        }

    return analyze_node


def make_title_node(llm: BaseLLMProvider):
    async def title_node(state: ArticleState) -> dict:
        agent = TitleGeneratorAgent(llm)
        feedback_hints = state.get("feedback_hints")

        titles = await agent.generate(
            topic=state["topic"],
            feedback_hints=feedback_hints,
            temperature=0.9,
        )

        return {
            "titles": [
                {"id": t.id, "text": t.text, "reason": t.reason, "score": t.score}
                for t in titles
            ],
            "current_node": "title",
            "history": ["title"],
        }

    return title_node


def make_title_confirm_node():
    """人机确认标题：首次在 interrupt 处暂停，resume 后写入 selected_title_id / edited_title。"""

    async def title_confirm_node(state: ArticleState) -> dict:
        from langgraph.types import interrupt

        resume_payload = interrupt(
            {
                "stage": "title",
                "titles": state.get("titles") or [],
            }
        )

        out: dict = {"current_node": "title_confirm", "history": ["title_confirm"]}
        if isinstance(resume_payload, dict):
            sid = resume_payload.get("selected_id")
            if sid is not None:
                out["selected_title_id"] = int(sid)
            et = resume_payload.get("edited_title")
            if et:
                out["edited_title"] = str(et)
        return out

    return title_confirm_node


def make_outline_node(llm: BaseLLMProvider):
    async def outline_node(state: ArticleState) -> dict:
        agent = OutlineBuilderAgent(llm)

        confirmed_title = state.get("edited_title")
        titles = state.get("titles") or []
        sid = state.get("selected_title_id")
        if not confirmed_title and titles and sid is not None:
            selected = next((t for t in titles if t.get("id") == sid), None)
            if selected:
                confirmed_title = selected.get("text")

        confirmed_title = confirmed_title or state["topic"]

        outline = await agent.build(
            topic=state["topic"],
            title=confirmed_title,
            target_words=2000,
        )

        return {
            "outline": {
                "sections": [
                    {
                        "heading": s.heading,
                        "key_points": s.key_points,
                        "estimated_words": s.estimated_words,
                    }
                    for s in outline.sections
                ],
                "total_words": outline.total_words,
            },
            "current_node": "outline",
            "history": ["outline"],
        }

    return outline_node


def make_outline_confirm_node():
    """人机确认大纲：interrupt 暂停，resume 可带 edited_outline（空则沿用生成结果）。"""

    async def outline_confirm_node(state: ArticleState) -> dict:
        from langgraph.types import interrupt

        resume_payload = interrupt(
            {
                "stage": "outline",
                "outline": state.get("outline"),
            }
        )

        out: dict = {"current_node": "outline_confirm", "history": ["outline_confirm"]}
        if isinstance(resume_payload, dict):
            eo = resume_payload.get("edited_outline")
            if eo is not None:
                out["edited_outline"] = eo
        return out

    return outline_confirm_node


def make_write_node(llm: BaseLLMProvider):
    async def write_node(state: ArticleState) -> dict:
        from langgraph.config import get_stream_writer

        agent = ContentWriterAgent(llm)

        confirmed_title = state.get("edited_title")
        titles = state.get("titles") or []
        sid = state.get("selected_title_id")
        if not confirmed_title and titles and sid is not None:
            selected = next((t for t in titles if t.get("id") == sid), None)
            if selected:
                confirmed_title = selected.get("text")

        confirmed_title = confirmed_title or state["topic"]

        outline = state.get("edited_outline") or state.get("outline") or {}

        context = WritingContext(
            topic=state["topic"],
            title=confirmed_title,
            outline=outline,
            style_context=state.get("style_context"),
        )

        try:
            writer = get_stream_writer()
        except Exception:
            writer = None

        parts: list[str] = []
        total_chunks = 0
        async for chunk in agent.write_stream(context):
            parts.append(chunk)
            total_chunks += 1
            progress = min(total_chunks / 100, 0.99)
            if writer:
                writer(
                    {
                        "event": "content",
                        "chunk": chunk,
                        "progress": progress,
                    }
                )

        full_content = "".join(parts)

        return {
            "content": full_content,
            "confirmed_title": confirmed_title,
            "current_node": "write",
            "history": ["write"],
        }

    return write_node


def make_image_node():
    async def image_node(state: ArticleState) -> dict:
        agent = ImageSelectorAgent()

        confirmed_title = state.get("confirmed_title") or state["topic"]
        image_source = state.get("image_source") or "random"

        result: ImageResult = await agent.select(
            title=confirmed_title,
            content=state.get("content") or "",
            strategy=image_source,
        )

        return {
            "cover_image_url": result.url,
            "cover_image_alt": result.alt,
            "cover_image_source": result.source,
            "current_node": "image",
            "history": ["image"],
        }

    return image_node
