"""LLM API 路由 — 用量与监控（V0：聚合模拟数据，后续可接真实计量）"""

from fastapi import APIRouter

from app.utils.response import success_response

router = APIRouter()


@router.get("/llm/monitoring")
async def get_llm_monitoring():
    """
    LLM 监控面板数据：成本趋势、模型占比、降级/失败、高消费任务。

    前端 FE-Epic-8；数据后续可由调用链路与账单表替换。
    """
    return success_response(
        {
            "cost_trend": [
                {"date": "2026-04-10", "cost_cny": 2.1},
                {"date": "2026-04-11", "cost_cny": 3.4},
                {"date": "2026-04-12", "cost_cny": 2.8},
                {"date": "2026-04-13", "cost_cny": 4.2},
                {"date": "2026-04-14", "cost_cny": 3.6},
                {"date": "2026-04-15", "cost_cny": 5.1},
                {"date": "2026-04-16", "cost_cny": 4.0},
            ],
            "model_share": [
                {"model": "qwen-turbo", "calls": 142, "tokens_in": 88000, "tokens_out": 42000},
                {"model": "qwen-plus", "calls": 38, "tokens_in": 24000, "tokens_out": 31000},
                {"model": "mock-llm", "calls": 56, "tokens_in": 12000, "tokens_out": 8000},
            ],
            "routing": {
                "degradation_count": 4,
                "failure_count": 2,
                "total_calls": 236,
                "failure_rate": 0.0085,
            },
            "top_tasks": [
                {
                    "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "topic": "LangGraph 状态机与 Checkpoint",
                    "cost_cny": 1.85,
                    "calls": 12,
                },
                {
                    "task_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                    "topic": "Python 异步 IO 实战",
                    "cost_cny": 1.22,
                    "calls": 9,
                },
                {
                    "task_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
                    "topic": "公众号标题心理学",
                    "cost_cny": 0.76,
                    "calls": 6,
                },
            ],
            "daily_cost_cny": 4.0,
            "daily_cost_limit_cny": 50.0,
        }
    )
