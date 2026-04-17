"""配置管理 - 使用 pydantic-settings"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # === 环境 ===
    app_env: Literal["dev", "test", "prod"] = "dev"
    debug: bool = False

    # === 应用 ===
    app_name: str = "Creator Copilot"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"

    # === 数据库 ===
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # === LangGraph Checkpoint（SQLite，interrupt / resume）===
    langgraph_sqlite_path: str = "./data/langgraph_checkpoints.db"
    # database_url: str = "mysql+aiomysql://user:pass@localhost:3306/creator_copilot"

    # === Chroma ===
    chroma_path: str = "./data/chroma"

    # === Neo4j ===
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""

    # === LLM - DashScope ===
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/api/v1"

    # === LLM - Anthropic ===
    anthropic_api_key: str = ""

    # === LLM - Ollama ===
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # === 微信公众号 ===
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # === 配图 ===
    pexels_api_key: str = ""
    minimax_api_key: str = ""

    # === APScheduler ===
    scheduler_enabled: bool = True
    feedback_sync_interval_hours: int = 6

    # === 成本控制 ===
    daily_cost_limit_cny: float = 50.0
    user_daily_task_limit: int = 20

    # === 日志 ===
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_rotation: str = "100 MB"
    log_retention: str = "30 days"
    log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"

    # === CORS ===
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"


@lru_cache
def get_settings() -> Settings:
    """获取单例配置"""
    return Settings()


settings = get_settings()
