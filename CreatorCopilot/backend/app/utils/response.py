"""统一响应格式 & 错误码"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """统一响应格式"""

    code: int = Field(default=0, description="状态码，0=成功，非0=失败")
    data: T | None = Field(default=None, description="响应数据")
    message: str = Field(default="ok", description="消息")
    trace_id: str | None = Field(default=None, description="追踪ID")


class ErrorResponse(BaseModel, Generic[T]):
    """错误响应格式"""

    code: int = Field(description="错误码")
    data: None = Field(default=None)
    message: str = Field(description="错误消息")
    trace_id: str | None = Field(default=None, description="追踪ID")


# === 错误码定义 ===
class ErrCode:
    """错误码常量"""

    # 系统级 1000-1999
    SUCCESS = 0
    UNKNOWN_ERROR = 1000
    VALIDATION_ERROR = 1001
    NOT_FOUND = 1002
    INTERNAL_ERROR = 1003
    SERVICE_UNAVAILABLE = 1004

    # 创作相关 2000-2999
    TASK_NOT_FOUND = 2001
    TASK_ALREADY_CANCELLED = 2002
    TASK_CANNOT_RESUME = 2003
    INVALID_TOPIC = 2004
    TITLE_SELECTION_REQUIRED = 2005
    OUTLINE_SELECTION_REQUIRED = 2006

    # LLM 相关 3000-3999
    LLM_INVOKE_ERROR = 3001
    LLM_TIMEOUT = 3002
    LLM_RATE_LIMIT = 3003
    LLM_COST_EXCEEDED = 3004
    LLM_MODEL_NOT_FOUND = 3005

    # 知识库相关 4000-4999
    KB_ARTICLE_EXISTS = 4001
    KB_IMPORT_ERROR = 4002
    KB检索_ERROR = 4003

    # 知识图谱相关 5000-5999
    KG_NODE_EXISTS = 5001
    KG_QUERY_ERROR = 5002

    # 反馈相关 6000-6999
    FB_SYNC_ERROR = 6001
    FB_DATA_NOT_READY = 6002

    # 风格相关 7000-7999
    SE_SNAPSHOT_ERROR = 7001
    SE_REPORT_ERROR = 7002

    # 矩阵相关 8000-8999
    MX_PLAN_ERROR = 8001
    MX_ARTICLE_NOT_FOUND = 8002


def success_response(data: Any = None, message: str = "ok", trace_id: str | None = None) -> Response:
    """成功响应"""
    return Response(code=ErrCode.SUCCESS, data=data, message=message, trace_id=trace_id)


def error_response(code: int, message: str, trace_id: str | None = None) -> ErrorResponse:
    """错误响应"""
    return ErrorResponse(code=code, message=message, trace_id=trace_id)
