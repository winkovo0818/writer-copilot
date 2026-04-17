"""微信公众号 API 客户端"""

import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger("wechat_api")


@dataclass
class WeChatArticle:
    """微信公众号文章"""
    msg_id: str
    title: str
    author: str
    digest: str
    url: str
    publish_time: int


@dataclass
class WeChatArticleStats:
    """微信公众号文章数据"""
    msg_id: str
    stat_date: str
    int_page_read_count: int  # 阅读量
    int_page_read_user: int   # 阅读人数
    orig_int_page_read_count: int
    share_user_count: int      # 分享人数
    add_to_fav_count: int      # 收藏数
    like_count: int           # 点赞数
    comment_count: int        # 评论数
    catch_time: int           # 抓取时间


class WeChatAPI:
    """微信公众号 API 客户端"""

    def __init__(self, app_id: str | None = None, app_secret: str | None = None):
        self.app_id = app_id or settings.wechat_app_id
        self.app_secret = app_secret or settings.wechat_app_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: int = 0
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_access_token(self) -> str:
        """获取 access_token（自动刷新）"""
        now = int(time.time())

        if self._access_token and now < self._token_expires_at - 300:
            return self._access_token

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret,
        }

        try:
            response = await self.client.get(url, params=params)
            data = response.json()

            if "access_token" in data:
                self._access_token = data["access_token"]
                self._token_expires_at = now + data.get("expires_in", 7200)
                logger.info("WeChat access_token refreshed")
                return self._access_token
            else:
                raise Exception(f"Failed to get access_token: {data}")

        except Exception as e:
            logger.error(f"WeChat API error: {e}")
            raise

    async def get_article_list(self, offset: int = 0, count: int = 10) -> list[WeChatArticle]:
        """获取文章列表"""
        token = await self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/archive_list?access_token={token}"

        payload = {
            "type": "news",
            "offset": offset,
            "count": count,
        }

        try:
            response = await self.client.post(url, json=payload)
            data = response.json()

            if "item_count" in data:
                articles = []
                for item in data.get("item", []):
                    content = item.get("content", {}).get("news_item", [{}])[0]
                    articles.append(WeChatArticle(
                        msg_id=item.get("media_id", ""),
                        title=content.get("title", ""),
                        author=content.get("author", ""),
                        digest=content.get("digest", ""),
                        url=content.get("url", ""),
                        publish_time=item.get("content", {}).get("update_time", 0),
                    ))
                return articles

            return []

        except Exception as e:
            logger.error(f"Failed to get article list: {e}")
            return []

    async def get_article_stats(self, msg_id: str) -> Optional[WeChatArticleStats]:
        """获取单篇文章数据（需开通数据统计）"""
        token = await self.get_access_token()
        url = f"https://api.weixin.qq.com/datacube/getarticlearticleworldcloud?access_token={token}"

        payload = {
            "msgid": msg_id,
            "begin_date": "20240101",  # 简化
            "end_date": "20241231",
        }

        try:
            response = await self.client.post(url, json=payload)
            data = response.json()

            if "list" in data and data["list"]:
                item = data["list"][0]
                return WeChatArticleStats(
                    msg_id=msg_id,
                    stat_date=item.get("stat_date", ""),
                    int_page_read_count=item.get("int_page_read_count", 0),
                    int_page_read_user=item.get("int_page_read_user", 0),
                    orig_int_page_read_count=item.get("orig_int_page_read_count", 0),
                    share_user_count=item.get("share_user_count", 0),
                    add_to_fav_count=item.get("add_to_fav_count", 0),
                    like_count=item.get("like_count", 0),
                    comment_count=item.get("comment_count", 0),
                    catch_time=int(time.time()),
                )

            return None

        except Exception as e:
            logger.warning(f"Failed to get article stats (may not have permission): {e}")
            return None

    async def close(self) -> None:
        """关闭客户端"""
        await self.client.aclose()
