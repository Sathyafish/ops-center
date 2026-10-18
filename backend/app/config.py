from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM: openai | ollama
    llm_provider: str = "openai"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.2:3b"

    # Embeddings: openai | ollama (pull nomic-embed-text for local RAG)
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    ollama_embedding_model: str = "nomic-embed-text"

    llm_context_max_chars: int = 6000

    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 480
    jwt_algorithm: str = "HS256"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "changeme-neo4j"

    chroma_persist_dir: str = "./data/chroma"
    runbooks_dir: str = "./data/runbooks"
    chunk_size: int = 600
    chunk_overlap: int = 80
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @model_validator(mode="after")
    def normalize_and_align_providers(self) -> Self:
        object.__setattr__(self, "llm_provider", self.llm_provider.strip().lower())
        object.__setattr__(self, "embedding_provider", self.embedding_provider.strip().lower())
        # Common misconfig: chat on Ollama but embeddings still defaulting to OpenAI
        if self.llm_provider == "ollama" and self.embedding_provider == "openai":
            if not (self.openai_api_key or "").strip():
                object.__setattr__(self, "embedding_provider", "ollama")
        return self


settings = Settings()
