"""Configuração mínima compartilhada pelo projeto acadêmico."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "change-me")
    app_env: str = os.getenv("APP_ENV", "development")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))


settings = Settings()
