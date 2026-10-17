# Runbook corpus

Add `.md` files here (YAML front matter optional). Re-index into Chroma:

```bash
docker compose exec api python -m app.scripts.ingest_runbooks
```

Front matter keys: `title`, `doc_type`, `application`, `version`.

Files prefixed with `_` are ignored by the loader.
