"""Embeddings for Chroma: OpenAI or Ollama (e.g. nomic-embed-text)."""

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings

from app.config import settings


def embeddings_is_configured() -> bool:
    if settings.embedding_provider == "ollama":
        return bool(settings.ollama_embedding_model)
    return bool(settings.openai_api_key)


def get_embeddings() -> Embeddings:
    if settings.embedding_provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        return OllamaEmbeddings(
            model=settings.ollama_embedding_model,
            base_url=settings.ollama_base_url,
        )
    if not (settings.openai_api_key or "").strip():
        raise ValueError(
            "EMBEDDING_PROVIDER=openai requires OPENAI_API_KEY, or set "
            "EMBEDDING_PROVIDER=ollama with OLLAMA_BASE_URL and OLLAMA_EMBEDDING_MODEL."
        )
    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
