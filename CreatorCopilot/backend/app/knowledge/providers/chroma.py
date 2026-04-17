"""Chroma 向量库提供者（chromadb 为可选依赖，见 requirements-chroma.txt）"""

from __future__ import annotations

import hashlib
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass

from app.config import settings

if TYPE_CHECKING:
    from chromadb.config import Settings as ChromaSettings


def _load_chromadb():
    """延迟导入，未安装 chromadb 时给出明确提示。"""
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings
    except ImportError as e:
        raise ImportError(
            "未安装 chromadb，无法使用向量知识库。请执行: pip install -r requirements-chroma.txt\n"
            "若在 Windows 上因 chroma-hnswlib 编译失败，请安装 Microsoft C++ Build Tools，"
            "或改用 Python 3.11/3.12 后再安装 chromadb。"
        ) from e
    return chromadb, ChromaSettings


@dataclass
class RetrievalResult:
    """检索结果"""
    article_id: str
    section_heading: str
    content: str
    score: float
    metadata: dict


class ChromaProvider:
    """Chroma 向量库提供者"""

    def __init__(self, persist_path: str | None = None):
        chromadb, ChromaSettings = _load_chromadb()
        self.persist_path = persist_path or settings.chroma_path
        self.client = chromadb.PersistentClient(
            path=self.persist_path,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        self.collection_name = "article_sections"
        self._init_collection()

    def _init_collection(self) -> None:
        """初始化集合"""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Article sections for retrieval"}
            )

    def add_sections(
        self,
        article_id: str,
        sections: list[dict],
        embeddings: list[list[float]],
        metadata: dict | None = None,
    ) -> None:
        """
        添加文章段落

        Args:
            article_id: 文章ID
            sections: 段落列表 [{"heading": "...", "content": "..."}]
            embeddings: 对应的向量列表
        """
        if not sections or not embeddings:
            return

        ids = [f"{article_id}_{i}" for i in range(len(sections))]
        documents = [s["content"] for s in sections]
        metadatas = [
            {
                "article_id": article_id,
                "heading": s.get("heading", ""),
                **s.get("metadata", {})
            }
            for s in sections
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[RetrievalResult]:
        """
        相似性检索

        Args:
            query_embedding: 查询向量
            top_k: 返回数量
            filter_metadata: 元数据过滤条件

        Returns:
            检索结果列表
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"]
        )

        retrieval_results = []
        if results and results["ids"]:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i]

                retrieval_results.append(RetrievalResult(
                    article_id=metadata.get("article_id", ""),
                    section_heading=metadata.get("heading", ""),
                    content=document,
                    score=1.0 / (1.0 + distance),  # 距离转分数
                    metadata=metadata,
                ))

        return retrieval_results

    def delete_by_article_id(self, article_id: str) -> None:
        """删除某篇文章的所有段落"""
        try:
            self.collection.delete(where={"article_id": article_id})
        except Exception:
            pass  # 忽略删除错误

    def reset(self) -> None:
        """重置集合（危险！）"""
        self.client.delete_collection(name=self.collection_name)
        self._init_collection()

    @staticmethod
    def compute_embedding(text: str, api_key: str | None = None) -> list[float]:
        """
        计算文本向量（简化版，实际应调用 embedding API）

        这里使用简单的词袋模拟，实际生产应使用真正的 embedding 模型
        """
        # 简化的 embedding 实现（实际应调用 dashscope 或 openai 的 embedding API）
        words = text.split()
        # 使用简单的 hash 生成伪向量（仅用于演示）
        vector = []
        for i, word in enumerate(words[:128]):  # 截断到 128 维
            hash_val = hashlib.md5(word.encode()).digest()
            # 从 hash 中提取数值
            val = int.from_bytes(hash_val[:4], "big") / (2**32 - 1)
            vector.append(val)

        # 补零到 128 维
        while len(vector) < 128:
            vector.append(0.0)

        # L2 归一化
        import math
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector
