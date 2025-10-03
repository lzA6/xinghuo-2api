# app/core/config.py

from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """
    应用配置
    """
    # --- 服务监听端口 ---
    LISTEN_PORT: int = 8082

    # --- 应用元数据 ---
    APP_NAME: str = "Xinghuo Local API"
    APP_VERSION: str = "1.0.0"
    DESCRIPTION: str = "一个高性能的讯飞星火本地代理服务，兼容OpenAI API格式。"

    # --- 认证与安全 ---
    API_MASTER_KEY: Optional[str] = None

    # --- 支持的模型列表 (基于公开信息，可能需要根据实际情况调整) ---
    SUPPORTED_MODELS: List[str] = [
        "spark-3.5-max",
        "spark-pro",
        "spark-v2.0",
        "spark-lite",
    ]

    # --- 讯飞星火账号认证 ---
    XINGHUO_COOKIE: Optional[str] = None
    GT_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()