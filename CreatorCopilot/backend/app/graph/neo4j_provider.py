"""Neo4j 图数据库提供者"""

from typing import Any, Optional
from dataclasses import dataclass

from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import ServiceUnavailable, AuthError

from app.config import settings
from app.utils.exceptions import InternalError
from app.utils.logging import get_logger

logger = get_logger("neo4j")


@dataclass
class ConceptNode:
    """概念节点"""
    id: str
    name: str
    category: str
    aliases: list[str]
    description: str
    difficulty: int  # 1-5
    popularity: float
    is_covered: bool = False


@dataclass
class ConceptRelation:
    """概念关系"""
    source: str
    target: str
    relation_type: str  # 是_种/依赖于/相关于/前置知识/对比


class Neo4jProvider:
    """Neo4j 图数据库提供者"""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.uri = uri or settings.neo4j_uri
        self.username = username or settings.neo4j_username
        self.password = password or settings.neo4j_password
        self._driver: Optional[AsyncDriver] = None

    async def connect(self) -> None:
        """建立连接"""
        if self._driver is None:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password)
                )
                await self._driver.verify_connectivity()
                logger.info(f"Neo4j connected: {self.uri}")
            except (ServiceUnavailable, AuthError) as e:
                logger.warning(f"Neo4j connection failed: {e}, will use mock")
                self._driver = None

    async def close(self) -> None:
        """关闭连接"""
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def execute(self, query: str, params: dict | None = None) -> list[dict]:
        """执行 Cypher 查询"""
        if not self._driver:
            return []

        async with self._driver.session() as session:
            result = await session.run(query, params or {})
            records = await result.data()
            return records

    # === 概念节点操作 ===

    async def create_concept(self, concept: ConceptNode) -> None:
        """创建概念节点"""
        query = """
        MERGE (c:Concept {id: $id})
        SET c.name = $name,
            c.category = $category,
            c.aliases = $aliases,
            c.description = $description,
            c.difficulty = $difficulty,
            c.popularity = $popularity,
            c.is_covered = $is_covered
        """
        await self.execute(query, {
            "id": concept.id,
            "name": concept.name,
            "category": concept.category,
            "aliases": concept.aliases,
            "description": concept.description,
            "difficulty": concept.difficulty,
            "popularity": concept.popularity,
            "is_covered": concept.is_covered,
        })

    async def get_concept(self, name: str) -> Optional[ConceptNode]:
        """获取概念节点"""
        query = "MATCH (c:Concept {name: $name}) RETURN c"
        results = await self.execute(query, {"name": name})
        if results:
            c = results[0]["c"]
            return ConceptNode(
                id=c.get("id", ""),
                name=c.get("name", ""),
                category=c.get("category", ""),
                aliases=c.get("aliases", []),
                description=c.get("description", ""),
                difficulty=c.get("difficulty", 3),
                popularity=c.get("popularity", 0.0),
                is_covered=c.get("is_covered", False),
            )
        return None

    async def get_all_concepts(self, category: str | None = None) -> list[ConceptNode]:
        """获取所有概念"""
        if category:
            query = "MATCH (c:Concept {category: $category}) RETURN c"
            results = await self.execute(query, {"category": category})
        else:
            query = "MATCH (c:Concept) RETURN c"
            results = await self.execute(query)

        return [
            ConceptNode(
                id=r["c"].get("id", ""),
                name=r["c"].get("name", ""),
                category=r["c"].get("category", ""),
                aliases=r["c"].get("aliases", []),
                description=r["c"].get("description", ""),
                difficulty=r["c"].get("difficulty", 3),
                popularity=r["c"].get("popularity", 0.0),
                is_covered=r["c"].get("is_covered", False),
            )
            for r in results
        ]

    async def create_relation(self, relation: ConceptRelation) -> None:
        """创建关系"""
        query = """
        MATCH (s:Concept {name: $source})
        MATCH (t:Concept {name: $target})
        MERGE (s)-[r:RELATES_TO {type: $relation_type}]->(t)
        """
        await self.execute(query, {
            "source": relation.source,
            "target": relation.target,
            "relation_type": relation.relation_type,
        })

    async def get_neighbors(
        self,
        name: str,
        depth: int = 2,
        relation_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """获取 N 度邻居"""
        query = f"""
        MATCH path = (center:Concept {{name: $name}})
            -[r:RELATES_TO*1..{depth}]->(neighbor)
        WHERE center <> neighbor
        RETURN path,
               relationships(path) as rels,
               nodes(path) as node_list
        LIMIT 50
        """
        results = await self.execute(query, {"name": name})

        nodes = []
        edges = []
        seen_nodes = set()
        seen_edges = set()

        for r in results:
            node_list = r.get("node_list", [])
            rels = r.get("rels", [])

            for i, node in enumerate(node_list):
                if node.get("name") not in seen_nodes:
                    seen_nodes.add(node.get("name"))
                    nodes.append({
                        "id": node.get("id", ""),
                        "name": node.get("name", ""),
                        "category": node.get("category", ""),
                    })

                if i < len(rels) and rels[i]:
                    edge_key = f"{node_list[0].get('name')}-{node.get('name')}"
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        edges.append({
                            "source": node_list[0].get("name", ""),
                            "target": node.get("name", ""),
                            "type": rels[i].get("type", "related"),
                        })

        return {"nodes": nodes, "edges": edges}

    async def find_gaps(self, category: str | None = None, limit: int = 10) -> list[ConceptNode]:
        """Gap 分析：存在但未被文章覆盖的概念"""
        if category:
            query = """
            MATCH (c:Concept {category: $category})
            WHERE c.is_covered = false
            RETURN c
            ORDER BY c.popularity DESC
            LIMIT $limit
            """
            results = await self.execute(query, {"category": category, "limit": limit})
        else:
            query = """
            MATCH (c:Concept)
            WHERE c.is_covered = false
            RETURN c
            ORDER BY c.popularity DESC
            LIMIT $limit
            """
            results = await self.execute(query, {"limit": limit})

        return [
            ConceptNode(
                id=r["c"].get("id", ""),
                name=r["c"].get("name", ""),
                category=r["c"].get("category", ""),
                aliases=r["c"].get("aliases", []),
                description=r["c"].get("description", ""),
                difficulty=r["c"].get("difficulty", 3),
                popularity=r["c"].get("popularity", 0.0),
                is_covered=False,
            )
            for r in results
        ]

    async def mark_concept_covered(self, name: str, article_id: str) -> None:
        """标记概念为已覆盖"""
        query = """
        MATCH (c:Concept {name: $name})
        SET c.is_covered = true,
            c.article_id = $article_id
        """
        await self.execute(query, {"name": name, "article_id": article_id})
