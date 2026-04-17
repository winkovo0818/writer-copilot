"""文章创作 LangGraph：StateGraph 编译与执行入口"""

from __future__ import annotations

from typing import Any, AsyncIterator

from langgraph.graph import END, START, StateGraph

from app.llm.providers.base import BaseLLMProvider
from app.workflow.nodes import (
    make_analyze_node,
    make_image_node,
    make_outline_confirm_node,
    make_outline_node,
    make_title_confirm_node,
    make_title_node,
    make_write_node,
)
from app.workflow.state import ArticleState


class ArticleWorkflow:
    """文章创作工作流（interrupt + SQLite checkpoint 恢复）"""

    def __init__(
        self,
        llm: BaseLLMProvider,
        checkpointer: Any | None = None,
    ):
        self.llm = llm
        self.checkpointer = checkpointer
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(ArticleState)

        workflow.add_node("analyze", make_analyze_node(self.llm))
        workflow.add_node("title", make_title_node(self.llm))
        workflow.add_node("title_confirm", make_title_confirm_node())
        workflow.add_node("outline", make_outline_node(self.llm))
        workflow.add_node("outline_confirm", make_outline_confirm_node())
        workflow.add_node("write", make_write_node(self.llm))
        workflow.add_node("image", make_image_node())

        workflow.add_edge(START, "analyze")
        workflow.add_edge("analyze", "title")
        workflow.add_edge("title", "title_confirm")
        workflow.add_edge("title_confirm", "outline")
        workflow.add_edge("outline", "outline_confirm")
        workflow.add_edge("outline_confirm", "write")
        workflow.add_edge("write", "image")
        workflow.add_edge("image", END)

        return workflow.compile(checkpointer=self.checkpointer)

    def stream(
        self,
        input_state: ArticleState | dict[str, Any],
        config: dict[str, Any] | None = None,
        stream_mode: str | list[str] = "updates",
    ):
        """同步 stream（较少用于 FastAPI，保留与文档一致）"""
        return self.graph.stream(input_state, config=config, stream_mode=stream_mode)

    async def astream(
        self,
        input_state: ArticleState | dict[str, Any] | Any,
        config: dict[str, Any] | None = None,
        stream_mode: str | list[str] | None = None,
    ) -> AsyncIterator[Any]:
        """异步流式执行（推荐与 SSE 配合）；input_state 可为 dict 或 Command(resume=...)。"""
        modes: str | list[str] = stream_mode or ["updates", "custom"]
        async for chunk in self.graph.astream(
            input_state,
            config=config,
            stream_mode=modes,
        ):
            yield chunk

    async def ainvoke(
        self,
        input_state: ArticleState | dict[str, Any] | Any,
        config: dict[str, Any] | None = None,
    ) -> ArticleState | dict[str, Any]:
        return await self.graph.ainvoke(input_state, config=config)


def compile_article_graph(llm: BaseLLMProvider, checkpointer: Any | None) -> Any:
    """编译并返回已 compile 的图（供应用生命周期单例挂载）。"""
    return ArticleWorkflow(llm=llm, checkpointer=checkpointer).graph
