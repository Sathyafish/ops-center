# Ops Center GraphRAG — Organizational Knowledge for Incident Response

**One-liner:** This RAG app helps **Ops Center engineers** answer **incident routing, blast-radius, escalation, and change-correlation questions** from an **enterprise application dependency graph + runbooks** in a **web chat UI**, with **≥85% faithfulness** on a golden eval set (target **&lt;8s** p95 latency on EC2 `t3.large`).

## Use case (Project 3 — GraphRAG for Organizational Knowledge)

Enterprise command center with hundreds of applications. Ops needs:

- **Who to contact** when an application has an incident
- **Downstream impact** via dependency edges
- **SME / escalation report structure** for handoffs
- **Change requests** in flight that may explain an incident (acknowledge / link)

Traditional vector RAG misses relationship questions (“who owns X and what depends on it?”). **GraphRAG** (Neo4j + Cypher) handles structure; **vector RAG** (Chroma) handles unstructured runbook text. LangGraph orchestrates routing, retrieval, and grounded answers.

## Architecture

```
┌─────────────┐     JWT      ┌──────────────────┐     LangGraph    ┌─────────┐
│  React UI   │ ──────────► │  FastAPI backend │ ───────────────► │ OpenAI  │
└─────────────┘              └────────┬─────────┘                  └─────────┘
                                      │
                         ┌────────────┼────────────┐
                         ▼            ▼            ▼
                    Neo4j graph   Chroma vectors   Golden eval
```

| Layer | Choice |
|-------|--------|
| Graph | Neo4j — `Application`, `Person`, `Team`, `ChangeRequest`, `Runbook` |
| Vector | Chroma — chunked runbooks / escalation templates |
| Orchestration | LangChain + LangGraph (route → retrieve → generate) |
| Auth | JWT + bcrypt; 5 seeded ops users |
| Deploy | Docker Compose on EC2 |

## Quick start (local)

### Prerequisites

- Docker & Docker Compose
- OpenAI API key

### Run

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set OPENAI_API_KEY, JWT_SECRET, NEO4J_PASSWORD

docker compose up --build
```

- **UI:** http://localhost:5173  
- **API:** http://localhost:8000/docs  
- **Neo4j Browser:** http://localhost:7474 (user `neo4j`, password from `.env`)

### Seed graph (20+ nodes) and vector corpus

```bash
docker compose exec api python -m app.scripts.seed_all
```

### Runbook ingestion (vector DB)

Troubleshooting and procedure docs live in **`data/runbooks/`** as Markdown (optional YAML front matter). The ingestion layer loads, cleans, splits by headings, embeds, and **rebuilds** the Chroma collection (no duplicate chunks on re-run).

```bash
# After editing or adding runbooks — re-index only vectors
docker compose exec api python -m app.scripts.ingest_runbooks

# Local (from backend/, with venv + OPENAI_API_KEY)
PYTHONPATH=. python -m app.scripts.ingest_runbooks
```

Example prompts (use **Vector** or **Auto** mode): “How do I troubleshoot PaymentGateway 502 errors?” or “What is the OrderService dependency check order?”

### Sample logins (change passwords in production)

| Username | Password | Role |
|----------|----------|------|
| ops.alice | OpsCenter2026! | lead |
| ops.bob | OpsCenter2026! | engineer |
| ops.carol | OpsCenter2026! | engineer |
| ops.dave | OpsCenter2026! | engineer |
| ops.eve | OpsCenter2026! | oncall |

## API

- `POST /auth/login` — `{ "username", "password" }` → JWT  
- `POST /query` — `{ "question", "mode": "auto"|"graph"|"vector" }` (Bearer token)  
- `GET /health`

## RAG evaluation

Golden set: `eval/golden_dataset.json` (10+ questions with expected graph entities and keywords).

```bash
docker compose exec api python -m app.scripts.run_eval --report /tmp/eval_report.json
```

Produces faithfulness/relevance proxies and **GraphRAG vs vector** side-by-side for comparison write-up.

## GraphRAG vs Vector — when each wins

| Query type | Prefer |
|------------|--------|
| Ownership, on-call, dependency chain | **Graph** |
| “What fields go in SME report?” | **Vector** (runbook chunks) |
| Change + app correlation | **Graph** |
| Policy wording / procedure steps | **Vector** |
| Blast radius N hops | **Graph** |

Document 10 comparison queries in `docs/comparison_analysis.md` after running eval.

## EC2 deployment

See [docs/ec2-deploy.md](docs/ec2-deploy.md).

## Project submission checklist

- [ ] Demo video (≤5 min): login → incident query → contacts + dependencies → change correlation  
- [ ] GitHub link  
- [ ] Google Doc: framework fields, prompts, eval results, Graph vs vector analysis  
- [ ] Graph ≥20 nodes (seed script)  
- [ ] 10-query comparison report  

## License

Course project — internal use.
