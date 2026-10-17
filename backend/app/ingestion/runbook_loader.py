"""Load runbook markdown files with optional YAML front matter."""

from __future__ import annotations

import re
from pathlib import Path

from langchain_core.documents import Document

FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MULTI_NEWLINE_RE = re.compile(r"\n{3,}")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    block = match.group(1)
    body = text[match.end() :]
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            meta[key] = value
    return meta, body


def clean_runbook_text(text: str) -> str:
    text = HTML_COMMENT_RE.sub("", text)
    text = MULTI_NEWLINE_RE.sub("\n\n", text)
    return text.strip()


def load_runbook_file(path: Path) -> Document:
    raw = path.read_text(encoding="utf-8")
    front, body = _parse_front_matter(raw)
    cleaned = clean_runbook_text(body)
    metadata = {
        "source": path.stem,
        "filename": path.name,
        "doc_type": front.get("doc_type", "runbook"),
        "application": front.get("application", ""),
        "title": front.get("title", path.stem.replace("-", " ").title()),
        "version": front.get("version", "1.0"),
    }
    return Document(page_content=cleaned, metadata=metadata)


def load_runbooks_from_directory(runbooks_dir: Path) -> list[Document]:
    if not runbooks_dir.is_dir():
        return []
    docs: list[Document] = []
    for path in sorted(runbooks_dir.glob("**/*.md")):
        if path.name.startswith("_"):
            continue
        docs.append(load_runbook_file(path))
    return docs
