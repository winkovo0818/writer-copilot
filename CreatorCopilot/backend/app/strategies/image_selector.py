"""配图策略"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import random


@dataclass
class ImageResult:
    """图片结果"""
    url: str
    source: str
    alt: str
    width: int = 1200
    height: int = 630


class BaseImageStrategy(ABC):
    """配图策略基类"""

    @abstractmethod
    async def select(self, title: str, content: str | None = None) -> ImageResult:
        """选择图片"""
        pass

    def _default_result(self) -> ImageResult:
        """默认图片（当策略失败时）"""
        return ImageResult(
            url="https://picsum.photos/1200/630",
            source="picsum",
            alt="cover image",
            width=1200,
            height=630,
        )


class RandomStrategy(BaseImageStrategy):
    """随机策略"""

    async def select(self, title: str, content: str | None = None) -> ImageResult:
        await self._async_delay()
        return ImageResult(
            url=f"https://picsum.photos/1200/630?random={random.randint(1, 1000)}",
            source="picsum",
            alt=title,
        )


class PexelsStrategy(BaseImageStrategy):
    """Pexels 图库策略"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    async def select(self, title: str, content: str | None = None) -> ImageResult:
        # TODO: 调用 Pexels API
        return self._default_result()


class MermaidStrategy(BaseImageStrategy):
    """Mermaid 图表策略"""

    async def select(self, title: str, content: str | None = None) -> ImageResult:
        await self._async_delay()
        # 返回 Mermaid 图表 URL（简化实现）
        return ImageResult(
            url=f"https://mermaid.ink/img/{self._generate_mermaid(title)}",
            source="mermaid",
            alt=title,
        )

    def _generate_mermaid(self, text: str) -> str:
        """生成简化的 Mermaid URL"""
        # 简化实现，实际应生成更复杂的图表
        encoded = text[:50].replace(" ", "%20")
        return f"mermaid?message={encoded}"


class IconifyStrategy(BaseImageStrategy):
    """Iconify 图标策略"""

    async def select(self, title: str, content: str | None = None) -> ImageResult:
        await self._async_delay()
        return ImageResult(
            url=f"https://api.iconify.org/vscode-icons/file-type-code.svg",
            source="iconify",
            alt=title,
        )


class EmojiStrategy(BaseImageStrategy):
    """Emoji 策略"""

    EMOJIS = ["", "", "", "", ""]

    async def select(self, title: str, content: str | None = None) -> ImageResult:
        await self._async_delay()
        emoji = random.choice(self.EMOJIS)
        return ImageResult(
            url=f"https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f4da.svg",
            source="emoji",
            alt=f"{emoji} {title}",
        )


class SVGStrategy(BaseImageStrategy):
    """SVG 策略"""

    async def select(self, title: str, content: str | None = None) -> ImageResult:
        await self._async_delay()
        # 返回 SVG 占位图
        return ImageResult(
            url=f"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 630'><rect fill='%233498db' width='1200' height='630'/><text x='600' y='350' text-anchor='middle' fill='white' font-size='48'>{title[:20]}</text></svg>",
            source="svg",
            alt=title,
            width=1200,
            height=630,
        )


class ImageSelectorAgent:
    """配图选择 Agent"""

    STRATEGIES = {
        "random": RandomStrategy,
        "pexels": PexelsStrategy,
        "mermaid": MermaidStrategy,
        "iconify": IconifyStrategy,
        "emoji": EmojiStrategy,
        "svg": SVGStrategy,
    }

    def __init__(self, api_keys: dict | None = None):
        self.api_keys = api_keys or {}

    async def select(
        self,
        title: str,
        content: str | None = None,
        strategy: str = "random",
    ) -> ImageResult:
        """
        选择配图

        Args:
            title: 文章标题
            content: 文章内容（可选）
            strategy: 配图策略

        Returns:
            图片结果
        """
        strategy_class = self.STRATEGIES.get(strategy, RandomStrategy)

        try:
            if strategy_class == PexelsStrategy:
                strategy_instance = strategy_class(self.api_keys.get("pexels"))
            else:
                strategy_instance = strategy_class()

            return await strategy_instance.select(title, content)

        except Exception:
            # 失败时降级到 random
            return await RandomStrategy().select(title, content)

    def _async_delay(self):
        """模拟异步延迟"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(asyncio.sleep(0.01))
            else:
                asyncio.run(asyncio.sleep(0.01))
        except Exception:
            pass
