"""Chat LLM: OpenAI or Ollama (local on EC2 host)."""

import os

from langchain_core.language_models.chat_models import BaseChatModel

from app.config import settings


def _llm_provider() -> str:
    env = (os.environ.get("LLM_PROVIDER") or "").strip().lower()
    if env:
        return env
    return settings.llm_provider.strip().lower()


def _ollama_base_url() -> str:
    return (os.environ.get("OLLAMA_BASE_URL") or settings.ollama_base_url or "").strip()


def _ollama_model() -> str:
    return (os.environ.get("OLLAMA_MODEL") or settings.ollama_model or "").strip()


def llm_is_configured() -> bool:
    if _llm_provider() == "ollama":
        return bool(_ollama_model() and _ollama_base_url())
    return bool((settings.openai_api_key or "").strip())


def get_chat_llm() -> BaseChatModel:
    provider = _llm_provider()
    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama
        except ImportError as exc:
            raise ImportError(
                "LLM_PROVIDER=ollama but langchain-ollama is not installed. "
                "Rebuild api: docker compose build --no-cache api"
            ) from exc
        return ChatOllama(
            model=_ollama_model(),
            base_url=_ollama_base_url(),
            temperature=0,
        )
    if not (settings.openai_api_key or "").strip():
        raise ValueError(
            "LLM_PROVIDER=openai requires OPENAI_API_KEY, or set LLM_PROVIDER=ollama "
            "with OLLAMA_BASE_URL and OLLAMA_MODEL."
        )
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )
