"""LangGraph 工作流状态（TypedDict + reducer，供 StateGraph 合并状态）"""

from __future__ import annotations

import operator
from typing import Annotated, Any, NotRequired, TypedDict


class ArticleState(TypedDict, total=False):
    """创作工作流共享状态（LangGraph StateGraph 状态模式）"""

    # 任务信息
    task_id: str
    topic: str
    matrix_id: str | None
    image_source: str

    # 创作产出
    analysis: dict[str, Any] | None
    titles: list[dict[str, Any]]
    selected_title_id: int | None
    edited_title: str | None
    outline: dict[str, Any] | None
    edited_outline: dict[str, Any] | None
    content: str | None
    cover_image_url: str | None
    cover_image_alt: NotRequired[str | None]
    cover_image_source: NotRequired[str | None]

    # 写作阶段派生
    confirmed_title: NotRequired[str | None]

    # 增强上下文（注入 Prompt）
    style_context: str | None
    graph_context: dict[str, Any] | None
    feedback_hints: dict[str, Any] | None

    # 元数据（history 使用 reducer 追加）
    current_node: str
    history: Annotated[list[str], operator.add]


def article_state_to_public_dict(state: ArticleState | dict[str, Any]) -> dict[str, Any]:
    """转为可 JSON 序列化的字典（供日志或对外接口）"""
    s = dict(state)
    return {
        "task_id": s.get("task_id", ""),
        "topic": s.get("topic", ""),
        "matrix_id": s.get("matrix_id"),
        "image_source": s.get("image_source", "random"),
        "analysis": s.get("analysis"),
        "titles": s.get("titles") or [],
        "selected_title_id": s.get("selected_title_id"),
        "edited_title": s.get("edited_title"),
        "outline": s.get("outline"),
        "edited_outline": s.get("edited_outline"),
        "content": s.get("content"),
        "cover_image_url": s.get("cover_image_url"),
        "cover_image_alt": s.get("cover_image_alt"),
        "style_context": s.get("style_context"),
        "graph_context": s.get("graph_context"),
        "feedback_hints": s.get("feedback_hints"),
        "current_node": s.get("current_node", "start"),
        "history": s.get("history") or [],
    }
