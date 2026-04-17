"""风格进化 API 路由"""

from fastapi import APIRouter

from app.utils.response import success_response

router = APIRouter()


@router.get("/style/snapshot/{article_id}")
async def get_style_snapshot(article_id: str):
    """
    获取单篇风格快照

    Args:
        article_id: 文章ID

    Returns:
        风格快照数据
    """
    # 简化：返回模拟数据
    return success_response({
        "article_id": article_id,
        "avg_sentence_length": 28.5,
        "sentence_length_variance": 156.2,
        "question_ratio": 0.08,
        "vocabulary_richness": 0.42,
        "technical_term_density": 0.15,
        "formality_level": 0.65,
        "pov": "first",
        "section_count": 5,
        "code_block_ratio": 0.12,
    })


@router.get("/style/report")
async def get_style_report(period: str = "2026-04"):
    """
    获取月度风格报告

    Args:
        period: 周期（YYYY-MM 格式）

    Returns:
        风格进化报告
    """
    # 简化：返回模拟报告
    return success_response({
        "period": period,
        "article_count": 4,
        "trends": {
            "sentence_length_trend": "stable",
            "vocabulary_trend": "increasing",
            "technical_depth_trend": "stable",
        },
        "drift_alerts": [
            {
                "dimension": "avg_sentence_length",
                "severity": "warning",
                "message": "句长上升 15%，有啰嗦倾向"
            }
        ],
        "vs_last_period": {
            "avg_sentence_length": "+15%",
            "vocabulary_richness": "+8%",
        },
        "suggestions": [
            "建议缩短句长，每句控制在 25 字以内",
            "词汇丰富度提升良好，保持当前风格",
            "技术词密度稳定，继续深化实战内容",
        ],
    })


@router.get("/style/drift-alerts")
async def get_drift_alerts():
    """
    获取漂移预警

    Returns:
        漂移预警列表
    """
    return success_response({
        "alerts": [
            {
                "dimension": "句长",
                "baseline": 25.0,
                "current": 28.5,
                "change": "+14%",
                "severity": "warning",
            },
            {
                "dimension": "技术词密度",
                "baseline": 0.15,
                "current": 0.12,
                "change": "-20%",
                "severity": "info",
            },
        ]
    })


@router.post("/style/baseline")
async def set_style_baseline(article_ids: str):
    """
    设置风格基线

    Args:
        article_ids: 文章ID列表（逗号分隔）

    Returns:
        设置结果
    """
    return success_response({
        "status": "set",
        "based_on_articles": article_ids.split(","),
        "message": "基线已设置，前 10 篇作为参照",
    })
