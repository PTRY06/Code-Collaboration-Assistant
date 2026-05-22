from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com/chat/completions",
    )
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))
    TEMPERATURE: float = 0.2
    TIMEOUT: int = 60

    @classmethod
    def validate(cls) -> bool:
        if not cls.DEEPSEEK_API_KEY or cls.DEEPSEEK_API_KEY == "your_api_key_here":
            print("[ERROR] DEEPSEEK_API_KEY 未配置。")
            print("  方式1: 设置环境变量  $env:DEEPSEEK_API_KEY='sk-...'")
            print("  方式2: 复制 .env.example 为 .env 并填入真实密钥")
            return False
        return True
