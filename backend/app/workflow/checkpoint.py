"""LangGraph SQLite 异步 Checkpoint（持久化线程状态，供 interrupt / resume）"""

from __future__ import annotations

from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


def sqlite_checkpointer_cm(db_path: str):
    """
    返回 AsyncSqliteSaver 异步上下文管理器，供 `async with` 贯穿应用生命周期。

    示例::

        async with sqlite_checkpointer_cm("./data/langgraph_checkpoints.db") as saver:
            ...
    """
    parent = Path(db_path).parent
    if str(parent) not in (".", ""):
        parent.mkdir(parents=True, exist_ok=True)
    return AsyncSqliteSaver.from_conn_string(db_path)
