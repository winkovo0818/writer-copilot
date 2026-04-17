"""创作 API 路由 - LangGraph StateGraph + SQLite interrupt / resume"""

from __future__ import annotations

import json
import uuid
from typing import Any, AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langgraph.types import Command

from app.utils.response import success_response
from app.config import settings

router = APIRouter()


def get_llm_provider():
    """获取 LLM 提供者"""
    from app.llm.providers.mock import MockLLMProvider
    from app.llm.providers.dashscope import DashScopeProvider

    if settings.dashscope_api_key:
        return DashScopeProvider(api_key=settings.dashscope_api_key)
    return MockLLMProvider()


# === SSE 事件流 ===
async def sse_event(event: str, data: dict) -> str:
    """生成 SSE 格式事件"""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _unpack_astream_item(raw: Any) -> tuple[str, Any]:
    """兼容 LangGraph 不同版本的 astream 输出：二元组 / 三元组 / 裸 payload。"""
    if isinstance(raw, tuple):
        if len(raw) == 2:
            return str(raw[0]), raw[1]
        if len(raw) == 3:
            return str(raw[1]), raw[2]
    return "updates", raw


def _merge_delta(acc: dict[str, Any], delta: dict[str, Any]) -> None:
    for k, v in delta.items():
        if k == "history" and v:
            acc.setdefault("history", [])
            acc["history"] = list(acc.get("history") or []) + list(v)
        else:
            acc[k] = v


def _apply_updates_payload(acc: dict[str, Any], payload: Any) -> None:
    if not isinstance(payload, dict):
        return
    nodes = (
        "analyze",
        "title",
        "title_confirm",
        "outline",
        "outline_confirm",
        "write",
        "image",
    )
    if any(k in payload for k in nodes):
        for _node, delta in payload.items():
            if isinstance(delta, dict):
                _merge_delta(acc, delta)
    else:
        _merge_delta(acc, payload)


def _extract_interrupt_values(obj: Any) -> list[Any]:
    """递归收集 __interrupt__ 中的值（Interrupt.value 或裸值）。"""
    found: list[Any] = []

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            if "__interrupt__" in x:
                iv = x["__interrupt__"]
                seq = iv if isinstance(iv, (list, tuple)) else [iv]
                for item in seq:
                    found.append(getattr(item, "value", item))
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for i in x:
                walk(i)

    walk(obj)
    return found


async def article_stream(
    compiled_graph: Any,
    task_id: str,
    topic: str,
    image_source: str = "random",
    style_context: Optional[str] = None,
    feedback_hints: Optional[dict] = None,
    resume_payload: Optional[dict[str, Any]] = None,
) -> AsyncGenerator[str, None]:
    """
    文章创作 SSE。首次调用 resume_payload=None；从中断恢复时传入 Command(resume=...) 对应的数据字典。
    """
    try:
        initial_state: dict[str, Any] = {
            "task_id": task_id,
            "topic": topic,
            "image_source": image_source,
            "style_context": style_context,
            "feedback_hints": feedback_hints,
            "current_node": "start",
            "history": [],
        }

        acc: dict[str, Any] = {}
        config = {"configurable": {"thread_id": task_id}}

        if resume_payload is None:
            input_data: Any = initial_state
            acc = dict(initial_state)
            yield await sse_event("start", {"task_id": task_id, "topic": topic})
            yield await sse_event("stage", {"node": "analyze", "status": "running"})
        else:
            input_data = Command(resume=resume_payload)

        stream_modes: list[str] = ["updates", "custom"]
        write_stage_announced = False

        async for raw in compiled_graph.astream(
            input_data,
            config=config,
            stream_mode=stream_modes,
        ):
            intrs = _extract_interrupt_values(raw)
            if intrs:
                for val in intrs:
                    if not isinstance(val, dict):
                        continue
                    st = val.get("stage")
                    yield await sse_event("need_input", val)
                    if st == "title":
                        yield await sse_event(
                            "user_action",
                            {
                                "stage": "title",
                                "action": "confirm",
                                "message": "请选择一个标题或编辑后确认",
                            },
                        )
                    elif st == "outline":
                        yield await sse_event(
                            "user_action",
                            {
                                "stage": "outline",
                                "action": "confirm",
                                "message": "请确认大纲或编辑后继续",
                            },
                        )
                return

            mode, payload = _unpack_astream_item(raw)

            if isinstance(payload, dict) and payload.get("event") == "content":
                if not write_stage_announced:
                    write_stage_announced = True
                    yield await sse_event("stage", {"node": "write", "status": "running"})
                yield await sse_event(
                    "content",
                    {
                        "chunk": payload.get("chunk", ""),
                        "progress": payload.get("progress", 0),
                    },
                )
                continue

            if mode == "custom" and isinstance(payload, dict):
                if payload.get("event") == "content":
                    if not write_stage_announced:
                        write_stage_announced = True
                        yield await sse_event("stage", {"node": "write", "status": "running"})
                    yield await sse_event(
                        "content",
                        {
                            "chunk": payload.get("chunk", ""),
                            "progress": payload.get("progress", 0),
                        },
                    )
                continue

            if mode == "updates":
                _apply_updates_payload(acc, payload)

                if not isinstance(payload, dict):
                    continue

                for node_name, delta in payload.items():
                    if not isinstance(delta, dict):
                        continue

                    if node_name == "analyze" and "analysis" in delta:
                        a = delta["analysis"]
                        yield await sse_event(
                            "context_enriched",
                            {
                                "core_theme": a.get("core_theme"),
                                "target_audience": a.get("target_audience"),
                                "key_points": a.get("key_points"),
                            },
                        )
                        yield await sse_event("stage", {"node": "analyze", "status": "done"})
                        yield await sse_event("stage", {"node": "title", "status": "running"})

                    elif node_name == "title" and "titles" in delta:
                        yield await sse_event("titles", {"titles": delta["titles"]})
                        yield await sse_event("stage", {"node": "title", "status": "done"})

                    elif node_name == "outline" and "outline" in delta:
                        yield await sse_event("stage", {"node": "outline", "status": "running"})
                        yield await sse_event("outline", delta["outline"])
                        yield await sse_event("stage", {"node": "outline", "status": "done"})

                    elif node_name == "write":
                        if not write_stage_announced:
                            write_stage_announced = True
                            yield await sse_event("stage", {"node": "write", "status": "running"})
                        yield await sse_event("stage", {"node": "write", "status": "done"})
                        yield await sse_event("stage", {"node": "image", "status": "running"})

                    elif node_name == "image":
                        if "cover_image_url" in delta:
                            yield await sse_event(
                                "image_selected",
                                {
                                    "url": delta.get("cover_image_url"),
                                    "alt": delta.get("cover_image_alt"),
                                    "source": delta.get("cover_image_source"),
                                },
                            )
                        yield await sse_event("stage", {"node": "image", "status": "done"})

        yield await sse_event(
            "done",
            {
                "task_id": task_id,
                "title": acc.get("confirmed_title") or topic,
                "cover_image_url": acc.get("cover_image_url"),
            },
        )

    except Exception as e:
        yield await sse_event("error", {"code": 3001, "message": str(e)})


def _get_compiled_graph(request: Request) -> Any:
    g = getattr(request.app.state, "article_compiled_graph", None)
    if g is None:
        raise HTTPException(status_code=503, detail="Article workflow not initialized")
    return g


# === API 接口 ===


@router.post("/article/stream")
async def create_article_stream(
    request: Request,
    topic: str,
    image_source: str = "random",
):
    """
    创建创作任务（SSE 流式）。在标题/大纲确认处会中断，需调用 confirm 接口以 SSE 恢复。
    """
    if not topic or len(topic) < 5:
        raise HTTPException(status_code=400, detail="Topic too short")
    if len(topic) > 200:
        raise HTTPException(status_code=400, detail="Topic too long")

    task_id = str(uuid.uuid4())
    compiled = _get_compiled_graph(request)

    return StreamingResponse(
        article_stream(compiled, task_id, topic, image_source),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/article/confirm-title")
async def confirm_title(
    request: Request,
    task_id: str,
    selected_id: Optional[int] = None,
    edited_title: Optional[str] = None,
):
    """
    确认标题后恢复工作流（SSE），继续到大纲确认中断点。
    """
    if not selected_id and not edited_title:
        raise HTTPException(status_code=400, detail="selected_id or edited_title required")

    resume: dict[str, Any] = {}
    if selected_id is not None:
        resume["selected_id"] = selected_id
    if edited_title:
        resume["edited_title"] = edited_title

    compiled = _get_compiled_graph(request)
    return StreamingResponse(
        article_stream(
            compiled,
            task_id,
            topic="",
            resume_payload=resume,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/article/confirm-outline")
async def confirm_outline(
    request: Request,
    task_id: str,
    edited_outline: Optional[dict] = None,
):
    """
    确认大纲后恢复工作流（SSE），继续写作与配图直至完成。
    """
    resume: dict[str, Any] = {}
    if edited_outline is not None:
        resume["edited_outline"] = edited_outline

    compiled = _get_compiled_graph(request)
    return StreamingResponse(
        article_stream(
            compiled,
            task_id,
            topic="",
            resume_payload=resume,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/article/cancel")
async def cancel_task(task_id: str):
    """
    取消任务

    Args:
        task_id: 任务ID

    Returns:
        取消结果
    """
    return success_response({"task_id": task_id, "status": "cancelled"})


@router.get("/task/{task_id}")
async def get_task(task_id: str):
    """
    获取任务详情

    Args:
        task_id: 任务ID

    Returns:
        任务详情
    """
    return success_response(
        {
            "task_id": task_id,
            "status": "running",
            "topic": "测试选题",
        }
    )


@router.get("/task/{task_id}/resume")
async def resume_task(task_id: str):
    """
    已废弃：请使用 POST /article/confirm-title 或 /article/confirm-outline 并携带 body 以恢复（SSE）。
    """
    raise HTTPException(
        status_code=400,
        detail="Use POST /article/confirm-title or /article/confirm-outline with resume body; interrupt requires Command(resume=...).",
    )
