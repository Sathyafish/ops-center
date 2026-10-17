"""Runbook ingestion: load markdown corpus → clean → chunk → Chroma."""

from app.ingestion.pipeline import ingest_runbooks_directory

__all__ = ["ingest_runbooks_directory"]
