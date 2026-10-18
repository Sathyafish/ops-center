"""Print effective LLM/embedding backend (run inside api container)."""

import os

from app.config import settings
from app.rag.embeddings_factory import _embedding_provider, get_embeddings
from app.rag.llm_factory import _llm_provider, get_chat_llm


def main() -> None:
    print("=== Process env ===")
    print(f"  LLM_PROVIDER={os.environ.get('LLM_PROVIDER')!r}")
    print(f"  EMBEDDING_PROVIDER={os.environ.get('EMBEDDING_PROVIDER')!r}")
    print(f"  OLLAMA_BASE_URL={os.environ.get('OLLAMA_BASE_URL')!r}")
    print("=== Settings (pydantic) ===")
    print(f"  LLM_PROVIDER={settings.llm_provider!r}")
    print(f"  EMBEDDING_PROVIDER={settings.embedding_provider!r}")
    print(f"  effective llm={_llm_provider()!r} embed={_embedding_provider()!r}")
    print(f"  OLLAMA_BASE_URL={settings.ollama_base_url!r}")
    print(f"  OLLAMA_MODEL={settings.ollama_model!r}")
    print(f"  OLLAMA_EMBEDDING_MODEL={settings.ollama_embedding_model!r}")
    print(f"  OPENAI_API_KEY set={bool((settings.openai_api_key or '').strip())}")
    emb = get_embeddings()
    llm = get_chat_llm()
    print("=== Runtime classes ===")
    print(f"  embeddings={type(emb).__module__}.{type(emb).__name__}")
    print(f"  chat_llm={type(llm).__module__}.{type(llm).__name__}")
    if "openai" in type(emb).__module__.lower() and settings.embedding_provider == "ollama":
        raise SystemExit("ERROR: embedding_provider is ollama but OpenAI embeddings class loaded — rebuild api image")
    if "openai" in type(llm).__module__.lower() and settings.llm_provider == "ollama":
        raise SystemExit("ERROR: llm_provider is ollama but OpenAI chat class loaded — rebuild api image")


if __name__ == "__main__":
    main()
