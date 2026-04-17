"""反馈闭环 API 路由"""

from fastapi import APIRouter

from app.utils.response import success_response

router = APIRouter()


@router.get("/metrics/{article_id}")
async def get_article_metrics(article_id: str):
    """
    获取文章数据

    Args:
        article_id: 文章ID

    Returns:
        文章表现数据
    """
    # 简化：返回模拟数据
    return success_response({
        "article_id": article_id,
        "views": 3200,
        "unique_readers": 2800,
        "completion_rate": 0.65,
        "avg_read_time": 180,
        "likes": 45,
        "shares": 12,
        "favorites": 23,
        "comments": 8,
        "new_followers": 15,
        "engagement_rate": 0.045,
        "quality_score": 78.5,
    })


@router.post("/metrics/sync")
async def sync_article_metrics(article_id: str):
    """
    手动同步文章数据

    Args:
        article_id: 文章ID

    Returns:
        同步结果
    """
    return success_response({
        "article_id": article_id,
        "status": "syncing",
        "estimated_completion": "2分钟后",
    })


@router.get("/feedback/insights/{article_id}")
async def get_article_insights(article_id: str):
    """
    获取文章归因分析

    Args:
        article_id: 文章ID

    Returns:
        归因分析结果
    """
    # 简化：返回模拟洞察
    return success_response({
        "article_id": article_id,
        "quality_score": 78.5,
        "percentile": 0.72,
        "highlights": [
            "疑问式标题引发好奇心",
            "故事开头吸引读者",
            "代码示例实用性强",
        ],
        "issues": [
            "结尾略显仓促",
            "部分段落偏长",
        ],
        "suggestions": [
            "建议增加结尾总结",
            "建议拆分为更短的段落",
        ],
    })


@router.get("/feedback/patterns")
async def get_patterns():
    """
    获取模式洞察

    Returns:
        模式分析结果
    """
    # 简化：返回模拟数据
    return success_response({
        "best_title_patterns": [
            "疑问句标题",
            "数字列标题",
            "实战型标题",
        ],
        "best_structure": {
            "section_count": 5,
            "avg_section_length": "中",
            "has_code_blocks": True,
        },
        "best_publish_time": {
            "best_day": "周三",
            "best_hour": 9,
        },
        "top_topics": [
            "LangGraph",
            "Python异步",
            "源码分析",
        ],
    })


@router.get("/feedback/dashboard")
async def get_dashboard():
    """
    数据看板

    Returns:
        看板数据
    """
    return success_response({
        "monthly_summary": {
            "article_count": 4,
            "avg_views": 3200,
            "avg_engagement": 0.045,
            "total_likes": 180,
        },
        "trends": [
            {"week": "2026-W15", "views": 2800},
            {"week": "2026-W16", "views": 3500},
            {"week": "2026-W17", "views": 3200},
        ],
        "top_articles": [
            {
                "title": "LangGraph 入门指南",
                "views": 8500,
                "engagement": 0.082,
            },
            {
                "title": "Python 异步编程详解",
                "views": 5200,
                "engagement": 0.055,
            },
        ],
        "ai_insights": [
            "疑问句标题比陈述句标题平均高35%",
            "周三早9点发布的文章首日阅读高20%",
            "含代码示例的文章完读率高15%",
        ],
    })
