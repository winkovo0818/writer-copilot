"""风格特征提取器"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StyleSnapshot:
    """风格快照"""
    article_id: str
    snapshot_at: str = ""

    # 句式特征
    avg_sentence_length: float = 0.0
    sentence_length_variance: float = 0.0
    question_ratio: float = 0.0
    exclamation_ratio: float = 0.0

    # 词汇特征
    vocabulary_richness: float = 0.0
    technical_term_density: float = 0.0
    colloquial_ratio: float = 0.0
    frequent_words: list[str] = field(default_factory=list)
    signature_phrases: list[str] = field(default_factory=list)

    # 结构特征
    section_count: int = 0
    avg_section_length: int = 0
    has_code_blocks: bool = False
    code_block_ratio: float = 0.0
    image_count: int = 0

    # 语气特征
    formality_level: float = 0.5
    emotional_tone: str = "neutral"
    pov: str = "third"

    # 内容特征
    abstraction_level: float = 0.5
    technical_depth: float = 0.5


class StyleFeatureExtractor:
    """风格特征提取器（纯函数，不依赖 LLM）"""

    def __init__(self):
        # 技术术语列表（简化）
        self.tech_terms = {
            "api", "sdk", "框架", "模块", "函数", "变量", "异步", "并发",
            "线程", "进程", "数据库", "缓存", "部署", "容器", "接口",
            "algorithm", "function", "async", "await", "promise",
            "class", "method", "object", "array", "dictionary",
        }
        self.formal_words = {"因此", "然而", "此外", "综上所述", "由此可见"}
        self.colloquial_words = {"其实", "基本上", "大概", "可能", "估计"}

    def extract(self, content: str, article_id: str) -> StyleSnapshot:
        """
        提取风格特征

        Args:
            content: 文章内容
            article_id: 文章ID

        Returns:
            风格快照
        """
        snapshot = StyleSnapshot(article_id=article_id)

        # 清理文本
        text = content.strip()

        # 句式分析
        sentences = self._split_sentences(text)
        snapshot.avg_sentence_length = self._avg_sentence_length(sentences)
        snapshot.sentence_length_variance = self._sentence_variance(sentences)
        snapshot.question_ratio = self._question_ratio(sentences)
        snapshot.exclamation_ratio = self._exclamation_ratio(sentences)

        # 词汇分析
        words = self._tokenize(text)
        snapshot.vocabulary_richness = self._ttr(words)
        snapshot.technical_term_density = self._technical_density(words)
        snapshot.colloquial_ratio = self._colloquial_ratio(words)
        snapshot.frequent_words = self._top_words(words, top_n=20)

        # 结构分析
        snapshot.section_count = self._count_sections(text)
        snapshot.avg_section_length = len(text) // max(snapshot.section_count, 1)
        snapshot.has_code_blocks, snapshot.code_block_ratio = self._code_blocks(text)
        snapshot.image_count = self._count_images(text)

        # 语气分析
        snapshot.formality_level = self._formality_level(text, words)
        snapshot.pov = self._detect_pov(text)
        snapshot.emotional_tone = self._emotional_tone(sentences)

        # 内容特征
        snapshot.abstraction_level = self._abstraction_level(text, words)
        snapshot.technical_depth = self._technical_depth(words)

        return snapshot

    def _split_sentences(self, text: str) -> list[str]:
        """分割句子"""
        # 按中英文标点和换行分割
        sentences = re.split(r"[。！？\n\.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _avg_sentence_length(self, sentences: list[str]) -> float:
        """平均句长"""
        if not sentences:
            return 0.0
        return sum(len(s) for s in sentences) / len(sentences)

    def _sentence_variance(self, sentences: list[str]) -> float:
        """句长方差"""
        if len(sentences) < 2:
            return 0.0
        avg = sum(len(s) for s in sentences) / len(sentences)
        variance = sum((len(s) - avg) ** 2 for s in sentences) / len(sentences)
        return variance

    def _question_ratio(self, sentences: list[str]) -> float:
        """疑问句比例"""
        if not sentences:
            return 0.0
        questions = sum(1 for s in sentences if "？" in s or "?" in s)
        return questions / len(sentences)

    def _exclamation_ratio(self, sentences: list[str]) -> float:
        """感叹句比例"""
        if not sentences:
            return 0.0
        exclamations = sum(1 for s in sentences if "！" in s or "!" in s)
        return exclamations / len(sentences)

    def _tokenize(self, text: str) -> list[str]:
        """简单分词"""
        # 移除 Markdown 语法和标点
        text = re.sub(r"```[\s\S]*?```", "", text)  # 移除代码块
        text = re.sub(r"[`#*_\[\]()>]", "", text)
        # 按空白分割
        words = re.findall(r"\w+", text)
        return [w.lower() for w in words if len(w) > 1]

    def _ttr(self, words: list[str]) -> float:
        """Type-Token Ratio（词汇丰富度）"""
        if not words:
            return 0.0
        unique = len(set(words))
        return unique / len(words)

    def _technical_density(self, words: list[str]) -> float:
        """技术词密度"""
        if not words:
            return 0.0
        tech_count = sum(1 for w in words if w in self.tech_terms)
        return tech_count / len(words)

    def _colloquial_ratio(self, words: list[str]) -> float:
        """口语化程度"""
        if not words:
            return 0.0
        collo_count = sum(1 for w in words if w in self.colloquial_words)
        return collo_count / len(words)

    def _top_words(self, words: list[str], top_n: int = 20) -> list[str]:
        """高频词"""
        from collections import Counter
        # 过滤停用词
        stopwords = {"的", "了", "是", "在", "和", "与", "为", "等", "这", "那", "有", "我", "你", "他", "我们", "他们"}
        filtered = [w for w in words if w not in stopwords and len(w) > 2]
        counter = Counter(filtered)
        return [w for w, _ in counter.most_common(top_n)]

    def _count_sections(self, text: str) -> int:
        """章节数（二级标题）"""
        sections = re.findall(r"^##\s+.+$", text, multiline=True)
        return len(sections) + 1 if sections else 1

    def _code_blocks(self, text: str) -> tuple[bool, float]:
        """代码块检测"""
        code_blocks = re.findall(r"```[\s\S]*?```", text)
        if not code_blocks:
            return False, 0.0
        total_chars = sum(len(b) for b in code_blocks)
        return True, total_chars / max(len(text), 1)

    def _count_images(self, text: str) -> int:
        """图片数量"""
        images = re.findall(r"!\[.*?\]\(.*?\)", text)
        return len(images)

    def _formality_level(self, text: str, words: list[str]) -> float:
        """正式程度 0-1"""
        formal_count = sum(1 for w in words if w in self.formal_words)
        return min(formal_count / max(len(words), 1) * 5, 1.0)

    def _detect_pov(self, text: str) -> str:
        """人称检测"""
        first_person = len(re.findall(r"\b我\b|\b我们\b", text))
        second_person = len(re.findall(r"\b你\b|\b您\b", text))
        if first_person > second_person:
            return "first"
        elif second_person > first_person:
            return "second"
        return "third"

    def _emotional_tone(self, sentences: list[str]) -> str:
        """情绪基调"""
        positive = sum(1 for s in sentences if any(w in s for w in ["好", "棒", "赞", "优秀", "喜欢"]))
        negative = sum(1 for s in sentences if any(w in s for w in ["难", "复杂", "问题", "错误"]))
        ratio = positive / max(len(sentences), 1)
        if ratio > 0.1:
            return "positive"
        elif negative > len(sentences) * 0.1:
            return "negative"
        return "neutral"

    def _abstraction_level(self, text: str, words: list[str]) -> float:
        """抽象度"""
        abstract_words = {"概念", "原理", "机制", "理论", "本质", "思想", "方法论"}
        abstract_count = sum(1 for w in words if w in abstract_words)
        return min(abstract_count / max(len(words), 1) * 10, 1.0)

    def _technical_depth(self, words: list[str]) -> float:
        """技术深度"""
        return self._technical_density(words)
