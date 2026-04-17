"""FeedbackAnalyzer Agent - 反馈分析"""

import json
from dataclasses import dataclass
from typing import Optional

from app.llm.providers.base import BaseLLMProvider
from app.utils.exceptions import LLMInvokeError


@dataclass
class FeedbackInsight:
    """单篇反馈洞察"""
    article_id: str
    quality_score: float
    percentile: float  # 分位数（相对历史）
    highlights: list[str]  # 亮点
    issues: list[str]  # 问题
    suggestions: list[str]  # 建议


@dataclass
class PatternReport:
    """模式报告"""
    period: str
    article_count: int
    best_title_patterns: list[str]
    best_structure: dict
    best_publish_time: dict
    top_topics: list[str]


class FeedbackAnalyzerAgent:
    """反馈分析 Agent"""

    SYSTEM_PROMPT = """你是一个专业的内容数据分析师。请分析文章的表现数据，给出归因分析和改进建议。

请根据以下JSON格式返回：
{
  "quality_score": 85.0,
  "percentile": 0.82,
  "highlights": ["亮点1", "亮点2"],
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}"""

    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm

    async def analyze_single(
        self,
        article_id: str,
        article_title: str,
        metrics: dict,
    ) -> FeedbackInsight:
        """
        单篇归因分析

        Args:
            article_id: 文章ID
            article_title: 文章标题
            metrics: 文章指标 {views, likes, shares, completion_rate, ...}

        Returns:
            归因分析结果
        """
        prompt = f"""{self.SYSTEM_PROMPT}

文章：{article_title}
指标数据：
- 阅读量：{metrics.get('views', 0)}
- 阅读人数：{metrics.get('unique_readers', 0)}
- 完读率：{metrics.get('completion_rate', 0):.1%}
- 平均阅读时长：{metrics.get('avg_read_time', 0)}秒
- 点赞数：{metrics.get('likes', 0)}
- 分享数：{metrics.get('shares', 0)}
- 收藏数：{metrics.get('favorites', 0)}
- 评论数：{metrics.get('comments', 0)}

请分析："""

        try:
            response = await self.llm.invoke(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1024,
            )

            return self._parse_response(response.content, article_id)

        except Exception as e:
            raise LLMInvokeError(f"Feedback analysis failed: {e}")

    async def analyze_patterns(
        self,
        articles: list[dict],
    ) -> PatternReport:
        """
        跨文章模式分析

        Args:
            articles: 文章列表 [{title, metrics, publish_date}, ...]

        Returns:
            模式报告
        """
        prompt = """你是一个专业的内容数据分析师。请分析多篇文章的表现模式，提取共同的规律。

文章列表：
"""

        for i, article in enumerate(articles, 1):
            metrics = article.get("metrics", {})
            prompt += f"""
{i}. {article.get('title', '未知')}
   - 阅读量：{metrics.get('views', 0)}
   - 互动率：{metrics.get('engagement_rate', 0):.2%}
   - 完读率：{metrics.get('completion_rate', 0):.1%}
   - 标题类型：{article.get('title_type', '未知')}
"""

        prompt += """
请分析并按以下JSON格式返回：
{
  "best_title_patterns": ["模式1", "模式2"],
  "best_structure": {"章节数": 5, "平均段落长度": "中"},
  "best_publish_time": {"最佳星期": "周三", "最佳小时": 9},
  "top_topics": ["话题1", "话题2"]
}"""

        try:
            response = await self.llm.invoke(
                prompt=prompt,
                temperature=0.5,
                max_tokens=2048,
            )

            return self._parse_pattern_report(response.content)

        except Exception as e:
            raise LLMInvokeError(f"Pattern analysis failed: {e}")

    def _parse_response(self, content: str, article_id: str) -> FeedbackInsight:
        """解析单篇归因响应"""
        try:
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)
            return FeedbackInsight(
                article_id=article_id,
                quality_score=data.get("quality_score", 0),
                percentile=data.get("percentile", 0),
                highlights=data.get("highlights", []),
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", []),
            )

        except json.JSONDecodeError:
            return FeedbackInsight(
                article_id=article_id,
                quality_score=0,
                percentile=0,
                highlights=[],
                issues=["数据不足"],
                suggestions=["继续积累数据"],
            )

    def _parse_pattern_report(self, content: str) -> PatternReport:
        """解析模式报告"""
        try:
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            data = json.loads(content)
            return PatternReport(
                period="all",
                article_count=0,
                best_title_patterns=data.get("best_title_patterns", []),
                best_structure=data.get("best_structure", {}),
                best_publish_time=data.get("best_publish_time", {}),
                top_topics=data.get("top_topics", []),
            )

        except json.JSONDecodeError:
            return PatternReport(
                period="all",
                article_count=0,
                best_title_patterns=[],
                best_structure={},
                best_publish_time={},
                top_topics=[],
            )
