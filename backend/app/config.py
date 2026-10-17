from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

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


settings = Settings()
