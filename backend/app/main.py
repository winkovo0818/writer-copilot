"""FastAPI 应用入口"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.utils.exceptions import AppError
from app.utils.logging import init_logging, logger, set_trace_id
from app.utils.response import ErrCode, error_response, ErrorResponse

# === 初始化日志 ===
init_logging()
logger_api = logger.bind(name="api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger.info("Starting Creator Copilot...")

    from app.api.article import get_llm_provider
    from app.workflow.checkpoint import sqlite_checkpointer_cm
    from app.workflow.graph import compile_article_graph

    async with sqlite_checkpointer_cm(settings.langgraph_sqlite_path) as checkpointer:
        app.state.langgraph_checkpointer = checkpointer
        app.state.article_compiled_graph = compile_article_graph(
            get_llm_provider(),
            checkpointer,
        )
        yield

    logger.info("Shutting down Creator Copilot...")


# === 创建应用 ===
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
    lifespan=lifespan,
)


# === CORS 中间件 ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 请求拦截器 - 添加 trace_id ===
@app.middleware("http")
async def add_trace_id(request: Request, call_next):
    """为每个请求添加 trace_id"""
    trace_id = request.headers.get("x-trace-id") or request.headers.get("trace-id")
    set_trace_id(trace_id)
    response = await call_next(request)
    if trace_id:
        response.headers["x-trace-id"] = trace_id
    return response


# === 异常处理 ===
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """业务异常处理"""
    logger_api.warning(f"AppError: {exc.code} - {exc.message}", exc_info=exc.details)
    err = error_response(code=exc.code, message=exc.message)
    return JSONResponse(status_code=200, content=err.model_dump())


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP 异常处理"""
    logger_api.warning(f"HTTP {exc.status_code}: {exc.detail}")
    err = error_response(code=exc.status_code, message=exc.detail)
    return JSONResponse(status_code=200, content=err.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """验证错误处理"""
    logger_api.warning(f"Validation error: {exc.errors()}")
    err = error_response(code=ErrCode.VALIDATION_ERROR, message="Validation error")
    return JSONResponse(status_code=200, content=err.model_dump())


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理（隐藏堆栈）"""
    logger_api.error(f"Unhandled exception: {type(exc).__name__}: {exc}", exc_info=True)
    err = error_response(code=ErrCode.INTERNAL_ERROR, message="Internal server error")
    return JSONResponse(status_code=200, content=err.model_dump())


# === 健康检查 ===
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": settings.app_version}


# === 根路由 ===
@app.get("/")
async def root():
    """根路由"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.is_dev else "disabled",
    }


# === 导入路由 ===
from app.api import article, knowledge, graph, style, matrix, feedback, llm, deps

# 注册路由
app.include_router(article.router, prefix=settings.api_prefix, tags=["创作"])
app.include_router(knowledge.router, prefix=settings.api_prefix, tags=["知识库"])
app.include_router(graph.router, prefix=settings.api_prefix, tags=["知识图谱"])
app.include_router(style.router, prefix=settings.api_prefix, tags=["风格进化"])
app.include_router(matrix.router, prefix=settings.api_prefix, tags=["内容矩阵"])
app.include_router(feedback.router, prefix=settings.api_prefix, tags=["反馈闭环"])
app.include_router(llm.router, prefix=settings.api_prefix, tags=["LLM"])
