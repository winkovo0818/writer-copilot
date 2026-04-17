"""知识库 API 路由"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.knowledge.base import KnowledgeBase
from app.utils.response import success_response

router = APIRouter()

# 知识库单例
kb_instance: Optional[KnowledgeBase] = None


def get_kb() -> KnowledgeBase:
    """获取知识库实例"""
    global kb_instance
    if kb_instance is None:
        kb_instance = KnowledgeBase()
    return kb_instance


@router.post("/knowledge/articles")
async def import_article(
    title: str,
    content: str,
    publish_date: Optional[str] = None,
    source_url: Optional[str] = None,
    tags: Optional[str] = None,
):
    """
    导入单篇文章

    Args:
        title: 标题
        content: 正文（Markdown）
        publish_date: 发布日期
        source_url: 原文链接
        tags: 标签（逗号分隔）

    Returns:
        导入结果
    """
    article_id = str(uuid.uuid4())
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    kb = get_kb()
    result = kb.add_article(
        article_id=article_id,
        title=title,
        content=content,
        publish_date=publish_date,
        source_url=source_url,
        tags=tag_list,
    )

    return success_response(result)


@router.get("/knowledge/search")
async def search_knowledge(q: str, top_k: int = 5):
    """
    语义检索

    Args:
        q: 查询文本
        top_k: 返回数量

    Returns:
        检索结果
    """
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    kb = get_kb()
    results = kb.retrieve(q, top_k=top_k)

    return success_response({
        "results": [
            {
                "article_id": r.article_id,
                "section_heading": r.section_heading,
                "content": r.content[:200],  # 截断
                "score": r.score,
            }
            for r in results
        ]
    })


@router.get("/knowledge/check-duplication")
async def check_duplication(topic: str, threshold: float = 0.85):
    """
    选题查重

    Args:
        topic: 选题
        threshold: 相似度阈值

    Returns:
        相似文章列表
    """
    kb = get_kb()
    results = kb.check_duplication(topic, threshold)

    return success_response({
        "is_duplicate": len(results) > 0,
        "similar": [
            {
                "article_id": r.article_id,
                "title": r.metadata.get("title", ""),
                "similarity": r.score,
            }
            for r in results
        ]
    })


@router.get("/knowledge/articles")
async def list_articles(page: int = 1, page_size: int = 20):
    """
    文章列表

    Returns:
        文章列表（分页）
    """
    # TODO: 实现从数据库查询
    return success_response({
        "articles": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
    })


@router.delete("/knowledge/articles/{article_id}")
async def delete_article(article_id: str):
    """
    删除文章

    Args:
        article_id: 文章ID

    Returns:
        删除结果
    """
    kb = get_kb()
    kb.delete_article(article_id)

    return success_response({"article_id": article_id, "status": "deleted"})
