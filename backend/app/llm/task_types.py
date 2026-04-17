"""LLM 任务类型枚举"""

from enum import Enum


class TaskType(str, Enum):
    """LLM 任务类型"""
    # 创作相关
    TOPIC_ANALYZE = "topic_analyze"
    TITLE_GENERATE = "title_generate"
    OUTLINE_BUILD = "outline_build"
    CONTENT_WRITE = "content_write"
    CONTENT_POLISH = "content_polish"
    IMAGE_SELECT = "image_select"

    # 分析相关
    STYLE_ANALYZE = "style_analyze"
    FEEDBACK_ANALYZE = "feedback_analyze"

    # 规划相关
    MATRIX_PLAN = "matrix_plan"

    # embedding
    EMBEDDING = "embedding"


# === 路由配置 ===
DEFAULT_ROUTING = {
    TaskType.TOPIC_ANALYZE: {"primary": "qwen-plus", "fallback": "qwen-turbo"},
    TaskType.TITLE_GENERATE: {"primary": "qwen-max", "fallback": "qwen-plus"},
    TaskType.OUTLINE_BUILD: {"primary": "qwen-max", "fallback": "qwen-plus"},
    TaskType.CONTENT_WRITE: {"primary": "qwen-max", "fallback": "claude-sonnet"},
    TaskType.CONTENT_POLISH: {"primary": "claude-sonnet", "fallback": "qwen-max"},
    TaskType.IMAGE_SELECT: {"primary": "qwen-plus", "fallback": "qwen-turbo"},
    TaskType.STYLE_ANALYZE: {"primary": "qwen-plus", "fallback": "qwen-turbo"},
    TaskType.FEEDBACK_ANALYZE: {"primary": "qwen-plus", "fallback": "qwen-turbo"},
    TaskType.MATRIX_PLAN: {"primary": "qwen-max", "fallback": "qwen-plus"},
    TaskType.EMBEDDING: {"primary": "text-embedding-v2", "fallback": None},
}

# 模型价格（CNY / 1000 tokens）
MODEL_PRICES = {
    "qwen-max": {"input": 0.02, "output": 0.06},
    "qwen-plus": {"input": 0.004, "output": 0.012},
    "qwen-turbo": {"input": 0.002, "output": 0.006},
    "claude-sonnet": {"input": 0.015, "output": 0.075},
    "claude-opus": {"input": 0.05, "output": 0.25},
    "text-embedding-v2": {"input": 0.001, "output": 0},
}
