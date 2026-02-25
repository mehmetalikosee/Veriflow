"""
Application settings (env-based).
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "veriflow123"  # default for local Docker Neo4j; override in .env

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/veriflow"

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
    CONFIDENCE_THRESHOLD: float = 0.9  # Below this -> Manual Review

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
