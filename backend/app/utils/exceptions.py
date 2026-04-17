"""自定义异常"""

from typing import Any


class AppError(Exception):
    """应用基础异常"""

    def __init__(self, code: int, message: str, details: Any = None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# === 系统异常 ===
class ValidationError(AppError):
    """验证错误"""

    def __init__(self, message: str, details: Any = None):
        super().__init__(1001, message, details)


class NotFoundError(AppError):
    """资源不存在"""

    def __init__(self, message: str, details: Any = None):
        super().__init__(1002, message, details)


class InternalError(AppError):
    """内部错误"""

    def __init__(self, message: str, details: Any = None):
        super().__init__(1003, message, details)


# === 创作异常 ===
class TaskNotFoundError(AppError):
    """任务不存在"""

    def __init__(self, task_id: str):
        super().__init__(2001, f"Task not found: {task_id}")


class TaskCancelledError(AppError):
    """任务已取消"""

    def __init__(self, task_id: str):
        super().__init__(2002, f"Task already cancelled: {task_id}")


class TaskCannotResumeError(AppError):
    """任务无法恢复"""

    def __init__(self, task_id: str, reason: str):
        super().__init__(2003, f"Task cannot resume: {task_id}, reason: {reason}")


class InvalidTopicError(AppError):
    """无效选题"""

    def __init__(self, topic: str):
        super().__init__(2004, f"Invalid topic: {topic[:50]}...")


# === LLM 异常 ===
class LLMInvokeError(AppError):
    """LLM 调用错误"""

    def __init__(self, message: str, model: str | None = None):
        super().__init__(3001, f"LLM invoke error{model and f' ({model})' or ''}: {message}")


class LLMTimeoutError(AppError):
    """LLM 超时"""

    def __init__(self, model: str, timeout_ms: int):
        super().__init__(3002, f"LLM timeout: {model} exceeded {timeout_ms}ms")


class LLMRateLimitError(AppError):
    """LLM 限流"""

    def __init__(self, model: str):
        super().__init__(3003, f"LLM rate limit exceeded: {model}")


class LLMCostExceededError(AppError):
    """LLM 成本超限"""

    def __init__(self, daily_cost: float, limit: float):
        super().__init__(3004, f"Daily LLM cost {daily_cost:.2f} CNY exceeded limit {limit:.2f} CNY")


class LLMModelNotFoundError(AppError):
    """LLM 模型不存在"""

    def __init__(self, model: str):
        super().__init__(3005, f"LLM model not found: {model}")
