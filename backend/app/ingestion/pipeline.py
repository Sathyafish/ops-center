"""Ingestion pipeline: directory → clean → split → vector index."""

from __future__ import annotations

from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import settings
from app.ingestion.runbook_loader import load_runbooks_from_directory
from app.rag.vector_store import rebuild_vector_index


def default_runbooks_dir() -> Path:
    env_path = Path(settings.runbooks_dir)
    if env_path.is_dir():
        return env_path
    # Local dev: repo root data/runbooks
    repo_relative = Path(__file__).resolve().parents[3] / "data" / "runbooks"
    if repo_relative.is_dir():
        return repo_relative
    docker_path = Path("/data/runbooks")
    if docker_path.is_dir():
        return docker_path
    return env_path


def split_runbooks(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    return chunks


def ingest_runbooks_directory(
    runbooks_dir: Path | None = None,
    *,
    rebuild: bool = True,
) -> dict[str, int | str]:
    directory = runbooks_dir or default_runbooks_dir()
    if not directory.is_dir():
        return {
            "status": "error",
            "message": f"Runbooks directory not found: {directory}",
            "files": 0,
            "chunks": 0,
        }

    raw_docs = load_runbooks_from_directory(directory)
    if not raw_docs:
        return {
            "status": "error",
            "message": f"No .md runbooks under {directory}",
            "files": 0,
            "chunks": 0,
        }

    chunks = split_runbooks(raw_docs)
    count = rebuild_vector_index(chunks, rebuild=rebuild)
    return {
        "status": "ok",
        "directory": str(directory),
        "files": len(raw_docs),
        "chunks": count,
    }
