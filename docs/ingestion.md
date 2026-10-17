# Runbook ingestion layer

## Flow

```
data/runbooks/*.md
    → runbook_loader (front matter + clean)
    → RecursiveCharacterTextSplitter (respects ## / ###)
    → OpenAI embeddings
    → Chroma (collection ops_runbooks, full rebuild by default)
```

## Authoring runbooks

Create a new file, e.g. `data/runbooks/myapp-troubleshooting.md`:

```markdown
---
title: MyApp Troubleshooting
doc_type: runbook
application: MyApp
version: "1.0"
---

## Common symptoms
...

## Mitigation
...
```

- **`application`** — shown in retrieval citations; helps ops tie text to CMDB names.
- Files starting with `_` are skipped (see `_README.md`).

## Commands

| Command | Purpose |
|---------|---------|
| `python -m app.scripts.ingest_runbooks` | Re-index all runbooks (default: wipe + rebuild Chroma) |
| `python -m app.scripts.ingest_runbooks --append` | Add chunks without deleting collection (dev only) |
| `python -m app.scripts.seed_all` | Neo4j seed + runbook ingest |

## Config (`backend/.env`)

- `RUNBOOKS_DIR` — path to markdown folder
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — default 600 / 80
- `CHROMA_PERSIST_DIR` — persisted vector store
- `EMBEDDING_MODEL` — default `text-embedding-3-small`

## Course framework mapping

| Field | This project |
|-------|----------------|
| Corpus | ~9 runbooks (procedures + per-app troubleshooting), Markdown, English |
| Cleaning | Strip HTML comments, collapse blank lines, front matter → metadata |
| Freshness | Manual re-ingest after edits; document cadence in your Google Doc |
| Chunking | Heading-aware separators + fixed size cap |
