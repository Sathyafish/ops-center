# GraphRAG vs Vector RAG — Comparison Analysis (Template)

Run after seeding and evaluation:

```bash
docker compose exec api python -m app.scripts.run_eval --report /tmp/eval_report.json --with-llm
```

Copy metrics from `eval_report.json` into the table below and add 1–2 sentences per query.

## Summary metrics

| Metric | Graph retrieval | Vector retrieval |
|--------|-----------------|------------------|
| Wins (keyword overlap on golden set) | _TBD_ | _TBD_ |
| Avg retrieval score | _TBD_ | _TBD_ |

## 10 comparison queries

| # | Question | Winner | Why |
|---|----------|--------|-----|
| 1 | Who to contact for PaymentGateway? | Graph | Ownership edges + PRIMARY_CONTACT |
| 2 | OrderService dependencies | Graph | Multi-hop DEPENDS_ON |
| 3 | SME report required fields | Vector | Runbook chunk, no graph schema for prose |
| 4 | Active CR on PaymentGateway | Graph | ChangeRequest-AFFECTS-Application |
| 5 | Ack ticket for Auth change | Graph | CR node properties |
| 6 | L1 triage checklist | Vector | Procedure text |
| 7 | BillingEngine dependencies | Graph | Structured deps |
| 8 | Change ack procedure | Vector | Policy wording |
| 9 | Escalation L2 SLA | Graph | EscalationLevel nodes |
| 10 | Full incident bundle (PG) | Hybrid | Graph facts + vector ack steps |

## When to use which

- **GraphRAG** wins on relationship, ownership, dependency, and change-correlation questions.
- **Vector RAG** wins on procedural templates and free-text runbooks.
- **Hybrid (LangGraph default routing)** wins on compound ops questions during live incidents.

## Failure modes observed

- _Document ambiguous app names, missing nodes, or retrieval misses here after your demo._
