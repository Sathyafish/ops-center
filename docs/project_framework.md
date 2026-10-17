# RAG Framework — Ops Center GraphRAG (for Google Doc submission)

## One-liner

My RAG app helps **Ops Center engineers** answer **incident contact, dependency impact, escalation, and change-correlation questions** from **Neo4j org graph + runbook corpus** in a **web chat UI** with **≥85% faithfulness** on golden eval and **&lt;8s** p95 latency.

| Field | Answer |
|-------|--------|
| **Use case** | Live incident triage in enterprise command center; compound questions needing people + deps + changes + procedures. |
| **Corpus** | Neo4j org graph (15 apps, teams, people, CRs) + **Markdown runbooks** in `data/runbooks/` (L1 triage, SME template, per-app troubleshooting); English. |
| **Ingestion + cleaning** | `app.ingestion`: load `.md`, YAML front matter → metadata, strip comments/blank lines, chunk, embed, rebuild Chroma via `ingest_runbooks`. |
| **Freshness** | Re-run ingest after runbook edits; graph re-seed via `seed_all`; prod would sync CMDB + Confluence nightly (SLA 24h). |
| **Chunking + embedding** | 600-char recursive chunks, 80 overlap; `text-embedding-3-small` for runbooks. |
| **Retrieve** | Graph: Cypher templates keyed by app name + intent; Vector: Chroma top-4; LangGraph routes auto/graph/vector/hybrid. |
| **Generation** | `gpt-4o-mini`, grounded system prompt, refusal if context empty. |
| **Eval** | 12 golden cases; keyword overlap on retrieval + optional LLM answer scoring; Graph vs vector win counts. |
| **Auth** | JWT; 5 ops users for demo. |
| **Surface** | React chat UI → FastAPI → LangGraph. |

## Prompts / agent instructions

See `backend/app/rag/graph_agent.py` — `SYSTEM_PROMPT` and LangGraph nodes: classify → retrieve_graph → retrieve_vector → generate.

## Iterations to document in your write-up

1. Fixed vs semantic chunking on runbooks (600 chosen for field lists)
2. Auto-routing heuristics vs always-hybrid (latency tradeoff)
3. App name extraction heuristic vs LLM entity extraction
