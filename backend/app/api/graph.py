"""知识图谱 API 路由"""

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.graph.neo4j_provider import Neo4jProvider, ConceptNode, ConceptRelation
from app.utils.response import success_response

router = APIRouter()

# 图数据库单例
_neo4j: Optional[Neo4jProvider] = None


def get_neo4j() -> Neo4jProvider:
    """获取图数据库实例"""
    global _neo4j
    if _neo4j is None:
        _neo4j = Neo4jProvider()
    return _neo4j


# === 概念节点 ===

@router.post("/graph/concepts")
async def create_concept(
    name: str,
    category: str,
    description: str = "",
    aliases: Optional[str] = None,
    difficulty: int = 3,
    popularity: float = 0.0,
):
    """创建概念节点"""
    concept = ConceptNode(
        id=name,  # 简化：使用 name 作为 id
        name=name,
        category=category,
        aliases=[a.strip() for a in aliases.split(",")] if aliases else [],
        description=description,
        difficulty=difficulty,
        popularity=popularity,
    )

    neo4j = get_neo4j()
    await neo4j.create_concept(concept)

    return success_response({"name": name, "status": "created"})


@router.get("/graph/concepts")
async def list_concepts(category: Optional[str] = None):
    """获取概念列表"""
    neo4j = get_neo4j()
    concepts = await neo4j.get_all_concepts(category)

    return success_response({
        "concepts": [
            {
                "name": c.name,
                "category": c.category,
                "description": c.description,
                "difficulty": c.difficulty,
                "popularity": c.popularity,
                "is_covered": c.is_covered,
            }
            for c in concepts
        ]
    })


@router.get("/graph/context")
async def get_topic_context(topic: str, depth: int = 2):
    """
    获取话题上下文（N 度邻居子图）

    Args:
        topic: 话题名称
        depth: 邻居深度（1-3）

    Returns:
        {nodes: [...], edges: [...]}
    """
    if depth < 1 or depth > 3:
        raise HTTPException(status_code=400, detail="depth must be 1-3")

    neo4j = get_neo4j()
    result = await neo4j.get_neighbors(topic, depth)

    return success_response(result)


@router.get("/graph/gaps")
async def find_gaps(category: Optional[str] = None, limit: int = 10):
    """
    Gap 分析：未覆盖的概念

    Args:
        category: 分类筛选
        limit: 返回数量

    Returns:
        未覆盖的高热度概念列表
    """
    neo4j = get_neo4j()
    gaps = await neo4j.find_gaps(category, limit)

    return success_response({
        "gaps": [
            {
                "name": c.name,
                "category": c.category,
                "description": c.description,
                "difficulty": c.difficulty,
                "popularity": c.popularity,
            }
            for c in gaps
        ]
    })


@router.get("/graph/recommendations")
async def recommend_topics(topic: str, limit: int = 5):
    """
    话题推荐

    Args:
        topic: 当前话题
        limit: 返回数量

    Returns:
        推荐话题列表
    """
    neo4j = get_neo4j()

    # 获取 2 度邻居作为推荐
    result = await neo4j.get_neighbors(topic, depth=2)

    # 过滤已覆盖的
    concepts = await neo4j.get_all_concepts()
    covered = {c.name for c in concepts if c.is_covered}

    recommendations = [
        n for n in result["nodes"]
        if n["name"] != topic and n["name"] not in covered
    ][:limit]

    return success_response({
        "recommendations": recommendations
    })


@router.post("/graph/relations")
async def create_relation(
    source: str,
    target: str,
    relation_type: str = "相关于",
):
    """创建概念关系"""
    relation = ConceptRelation(
        source=source,
        target=target,
        relation_type=relation_type,
    )

    neo4j = get_neo4j()
    await neo4j.create_relation(relation)

    return success_response({
        "source": source,
        "target": target,
        "status": "created"
    })


@router.post("/graph/link-article")
async def link_article_to_graph(article_id: str, concepts: str):
    """
    将文章关联到概念图谱

    Args:
        article_id: 文章ID
        concepts: 概念名称列表（逗号分隔）

    Returns:
        关联结果
    """
    neo4j = get_neo4j()

    concept_list = [c.strip() for c in concepts.split(",")]
    for concept_name in concept_list:
        await neo4j.mark_concept_covered(concept_name, article_id)

    return success_response({
        "article_id": article_id,
        "linked_concepts": concept_list,
    })
