"""Embeddings for Chroma: OpenAI or Ollama (e.g. nomic-embed-text)."""

import os

from langchain_core.embeddings import Embeddings

from app.config import settings


def _embedding_provider() -> str:
    """Prefer process env (Docker) over Settings file defaults."""
    env = (os.environ.get("EMBEDDING_PROVIDER") or "").strip().lower()
    if env:
        return env
    llm_env = (os.environ.get("LLM_PROVIDER") or "").strip().lower()
    if llm_env == "ollama":
        return "ollama"
    return settings.embedding_provider.strip().lower()


def _ollama_base_url() -> str:
    return (os.environ.get("OLLAMA_BASE_URL") or settings.ollama_base_url or "").strip()


def _ollama_embedding_model() -> str:
    return (os.environ.get("OLLAMA_EMBEDDING_MODEL") or settings.ollama_embedding_model or "").strip()


def embeddings_is_configured() -> bool:
    if _embedding_provider() == "ollama":
        return bool(_ollama_embedding_model() and _ollama_base_url())
    return bool((settings.openai_api_key or "").strip())


def get_embeddings() -> Embeddings:
    provider = _embedding_provider()
    if provider == "ollama":
        try:
            from langchain_ollama import OllamaEmbeddings
        except ImportError as exc:
            raise ImportError(
                "EMBEDDING_PROVIDER=ollama but langchain-ollama is not installed. "
                "Rebuild api: docker compose build --no-cache api"
            ) from exc
        return OllamaEmbeddings(
            model=_ollama_embedding_model(),
            base_url=_ollama_base_url(),
        )
    if not (settings.openai_api_key or "").strip():
        raise ValueError(
            "EMBEDDING_PROVIDER=openai requires OPENAI_API_KEY, or set "
            "EMBEDDING_PROVIDER=ollama with OLLAMA_BASE_URL and OLLAMA_EMBEDDING_MODEL."
        )
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)
