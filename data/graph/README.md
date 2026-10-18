# Application reference data (GraphRAG)

| File | Purpose |
|------|---------|
| `applications_catalog.json` | 100 applications with SME, Eng Manager, PM, Director (Neo4j seed source) |
| `applications_reference.csv` | Same mapping for spreadsheets / ops desk |

Regenerate:

```bash
cd backend
PYTHONPATH=. python -m app.scripts.generate_application_catalog
```

Load into Neo4j:

```bash
docker compose exec api python -m app.scripts.seed_all
```

## Neo4j relationships per application

- `(Team)-[:OWNS]->(Application)`
- `(Person)-[:SME_FOR]->(Application)`
- `(Person)-[:ENG_MANAGER_FOR]->(Application)`
- `(Person)-[:PRODUCT_MANAGER_FOR]->(Application)`
- `(Person)-[:DIRECTOR_FOR]->(Application)`
- `(Application)-[:DEPENDS_ON]->(Application)`
