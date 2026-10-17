from pathlib import Path

import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.config import settings

COLLECTION = "ops_runbooks"


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)


def get_vector_store() -> Chroma:
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )


def _delete_collection_if_exists() -> None:
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass


def rebuild_vector_index(chunks: list[Document], *, rebuild: bool = True) -> int:
    """Replace or append runbook chunks in Chroma."""
    if not chunks:
        return 0
    if rebuild:
        _delete_collection_if_exists()
        Chroma.from_documents(
            chunks,
            get_embeddings(),
            collection_name=COLLECTION,
            persist_directory=settings.chroma_persist_dir,
        )
        return len(chunks)
    store = get_vector_store()
    store.add_documents(chunks)
    return len(chunks)


def ingest_documents(docs: list[Document]) -> int:
    """Legacy helper: split is caller's responsibility; prefer ingestion.pipeline."""
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    return rebuild_vector_index(chunks, rebuild=True)


def vector_retrieve(question: str, k: int = 4) -> tuple[str, list[dict[str, str]]]:
    store = get_vector_store()
    docs = store.similarity_search(question, k=k)
    if not docs:
        return "No vector documents indexed.", []
    parts: list[str] = []
    meta: list[dict[str, str]] = []
    for i, doc in enumerate(docs, start=1):
        src = doc.metadata.get("source", "runbook")
        title = doc.metadata.get("title", "")
        app = doc.metadata.get("application", "")
        label = f"{src}" + (f" | {title}" if title else "") + (f" | app={app}" if app else "")
        parts.append(f"[{i}] ({label})\n{doc.page_content}")
        meta.append(
            {
                "source": src,
                "title": title,
                "application": app,
                "snippet": doc.page_content[:200],
            }
        )
    return "\n\n".join(parts), meta
