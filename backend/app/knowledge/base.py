"""知识库服务"""

import hashlib
import re
from typing import Optional

from app.knowledge.providers.chroma import ChromaProvider, RetrievalResult
from app.utils.logging import get_logger

logger = get_logger("knowledge")


class KnowledgeBase:
    """知识库服务"""

    def __init__(self, chroma_path: str | None = None):
        self.chroma = ChromaProvider(persist_path=chroma_path)

    def add_article(
        self,
        article_id: str,
        title: str,
        content: str,
        publish_date: Optional[str] = None,
        source_url: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> dict:
        """
        添加文章到知识库

        Args:
            article_id: 文章ID
            title: 标题
            content: 正文（Markdown）
            publish_date: 发布日期
            source_url: 原文链接
            tags: 标签

        Returns:
            导入结果
        """
        # 检查重复
        if self._check_duplication(article_id, title, source_url):
            logger.warning(f"Article already exists: {title}")
            return {"status": "skipped", "reason": "duplicate"}

        # 按二级标题分段
        sections = self._split_by_headings(content, title)

        # 计算每段的 embedding
        embeddings = []
        for section in sections:
            embedding = ChromaProvider.compute_embedding(section["content"])
            embeddings.append(embedding)

        # 存入向量库
        metadata = {
            "title": title,
            "publish_date": publish_date or "",
            "source_url": source_url or "",
            "tags": ",".join(tags) if tags else "",
        }
        self.chroma.add_sections(article_id, sections, embeddings)

        logger.info(f"Article added: {title}, {len(sections)} sections")

        return {
            "status": "success",
            "article_id": article_id,
            "sections_count": len(sections),
        }

    def _check_duplication(
        self,
        article_id: str,
        title: str,
        source_url: Optional[str],
    ) -> bool:
        """检查重复"""
        # 简化实现：可以基于 source_url 或 title hash 检查
        # 这里留个接口，实际可以查数据库
        return False

    def _split_by_headings(self, content: str, default_title: str = "") -> list[dict]:
        """按二级标题分段"""
        sections = []

        # 匹配 Markdown 二级标题
        pattern = r"(^##\s+.+$\n?)"
        parts = re.split(pattern, content, flags=re.MULTILINE)

        current_heading = default_title or "引言"
        current_content = ""

        for part in parts:
            if re.match(r"^##\s+", part):
                # 保存之前的段落
                if current_content.strip():
                    sections.append({
                        "heading": current_heading,
                        "content": current_content.strip(),
                    })
                current_heading = re.sub(r"^##\s+", "", part).strip()
                current_content = ""
            else:
                current_content += part

        # 保存最后一段
        if current_content.strip():
            sections.append({
                "heading": current_heading,
                "content": current_content.strip(),
            })

        # 如果没有分段，整篇作为一个段落
        if not sections:
            sections.append({
                "heading": default_title or "全文",
                "content": content.strip(),
            })

        return sections

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[RetrievalResult]:
        """
        语义检索

        Args:
            query: 查询文本
            top_k: 返回数量
            filter_metadata: 元数据过滤

        Returns:
            检索结果列表
        """
        query_embedding = ChromaProvider.compute_embedding(query)
        results = self.chroma.search(query_embedding, top_k, filter_metadata)
        return results

    def get_style_context(self, topic: str, limit: int = 3) -> str:
        """
        获取风格上下文（用于注入 Prompt）

        Args:
            topic: 选题
            limit: 返回段落数量

        Returns:
            风格上下文字符串
        """
        results = self.retrieve(topic, top_k=limit)

        if not results:
            return ""

        context_parts = ["参考历史文章风格："]

        for i, result in enumerate(results, 1):
            context_parts.append(f"\n【参考{i}】{result.section_heading}")
            context_parts.append(result.content[:500])  # 限制长度

        return "\n".join(context_parts)

    def check_duplication(
        self,
        topic: str,
        threshold: float = 0.85,
    ) -> list[RetrievalResult]:
        """
        选题查重

        Args:
            topic: 选题
            threshold: 相似度阈值

        Returns:
            相似的文章列表
        """
        results = self.retrieve(topic, top_k=5)
        return [r for r in results if r.score >= threshold]

    def delete_article(self, article_id: str) -> None:
        """删除文章"""
        self.chroma.delete_by_article_id(article_id)
        logger.info(f"Article deleted: {article_id}")
