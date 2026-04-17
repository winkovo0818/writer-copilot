"""LangGraph 条件边（Phase 2：interrupt / 人机确认时启用）"""

from typing import Literal

from app.workflow.state import ArticleState


def _get_current_node(state: ArticleState | dict) -> str:
    return str(state.get("current_node") or "start")  # type: ignore[union-attr]


def should_continue(state: ArticleState | dict) -> Literal["title", "outline", "write", "end"]:
    """决定下一个节点（保留给 Phase 2 动态路由；当前主路径由 StateGraph 固定）"""
    current_node = _get_current_node(state)

    if current_node == "start":
        return "title"

    if current_node == "title":
        return "outline"

    if current_node == "outline":
        return "write"

    if current_node == "write":
        return "image"

    if current_node == "image":
        return "end"

    return "end"


def get_next_node(state: ArticleState | dict) -> str:
    """获取下一个节点名称"""
    flow = {
        "start": "analyze",
        "analyze": "title",
        "title": "title_confirm",
        "title_confirm": "outline",
        "outline": "outline_confirm",
        "outline_confirm": "write",
        "write": "image",
        "image": "end",
    }
    return flow.get(_get_current_node(state), "end")
