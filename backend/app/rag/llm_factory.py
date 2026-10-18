"""Chat LLM: OpenAI or Ollama (local on EC2 host)."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.config import settings


def llm_is_configured() -> bool:
    if settings.llm_provider == "ollama":
        return bool(settings.ollama_model)
    return bool(settings.openai_api_key)


def get_chat_llm() -> BaseChatModel:
    provider = settings.llm_provider.lower()
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )
    if not (settings.openai_api_key or "").strip():
        raise ValueError(
            "LLM_PROVIDER=openai requires OPENAI_API_KEY, or set LLM_PROVIDER=ollama "
            "with OLLAMA_BASE_URL and OLLAMA_MODEL."
        )
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )
