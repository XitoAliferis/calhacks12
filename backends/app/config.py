#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@File    :   config.py
@Time    :   2025/10/25 15:53:14
@Author  :   Ethan Pan 
@Version :   1.0
@Contact :   epan@cs.wisc.edu
@License :   (C)Copyright 2020-2025, Ethan Pan
@Desc    :   settings for the application. Supports .env file.
'''


from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


# loading settings from .env file.
class Settings(BaseSettings):
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL: str = "anthropic/claude-3.5-haiku"
    MOCK_AI_RESPONSES_FILE: str | None = None

    DB_URL: str = "sqlite:///./todos.db"

    CHROMA_DIR: str = "./chroma_data"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    DEBUG: bool = True
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# caching the settings for faster access.
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# exporting the settings for use in the application.
settings = get_settings()
