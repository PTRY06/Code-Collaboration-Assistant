from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default


class Config:
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com/chat/completions",
    )
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
    MAX_ITERATIONS: int = _int_env("MAX_ITERATIONS", 3)
    TEMPERATURE: float = _float_env("TEMPERATURE", 0.2)
    TIMEOUT: int = _int_env("TIMEOUT", 60)
    MAX_RETRIES: int = _int_env("MAX_RETRIES", 3)
    RETRY_BACKOFF_FACTOR: float = _float_env(
        "RETRY_BACKOFF_FACTOR", 1.5
    )
    SANDBOX_TIMEOUT: int = _int_env("SANDBOX_TIMEOUT", 10)
    MAX_HISTORY_TOKENS: int = _int_env("MAX_HISTORY_TOKENS", 96000)

    @classmethod
    def validate(cls) -> bool:
        if (
            not cls.DEEPSEEK_API_KEY
            or cls.DEEPSEEK_API_KEY == "your_api_key_here"
        ):
            print("[ERROR] DEEPSEEK_API_KEY 未配置。")
            print(
                "  方式1: 设置环境变量  $env:DEEPSEEK_API_KEY='your-key'"
            )
            print(
                "  方式2: 复制 .env.example 为 .env 并填入 API 密钥"
            )
            return False
        return True
