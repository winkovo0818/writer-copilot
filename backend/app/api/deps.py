"""API 依赖注入"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with async_session() as session:
        yield session
