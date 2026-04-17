"""日志配置 - loguru"""

import sys
from contextvars import ContextVar
from pathlib import Path

from loguru import logger

from app.config import settings

# === Context Variables ===
trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)


def get_trace_id() -> str | None:
    """获取当前 trace_id"""
    return trace_id_var.get()


def set_trace_id(trace_id: str | None) -> None:
    """设置 trace_id"""
    if trace_id:
        trace_id_var.set(trace_id)


# === 日志格式器 ===
def log_formatter(record: dict) -> str:
    """自定义日志格式"""
    extra = record.get("extra", {})
    trace_id = extra.get("trace_id") or get_trace_id() or "-"
    trace_id_str = f"[{trace_id}]" if trace_id != "-" else ""

    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        f"{trace_id_str} "
        "<level>{message}</level>"
        "{exception}\n"
    )


# === 初始化日志 ===
def init_logging() -> None:
    """初始化日志系统"""

    # 移除默认 handler
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stderr,
        format=log_formatter,
        level=settings.log_level,
        colorize=True,
    )

    # 文件输出
    log_dir = Path("./data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_dir / "app_{time}.log",
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        compression="zip",
        format=log_formatter,
        level=settings.log_level,
        encoding="utf-8",
    )

    # 记录启动日志
    logger.info(f"Logging initialized, app_env={settings.app_env}, debug={settings.debug}")


def get_logger(name: str) -> logger:
    """获取模块日志器"""
    return logger.bind(name=name)
