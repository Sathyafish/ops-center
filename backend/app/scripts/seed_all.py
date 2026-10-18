"""Seed Neo4j graph (100 applications + stakeholders) and ingest runbooks into Chroma."""

from app.graph.neo4j_client import run_query
from app.graph.seed_catalog import seed_applications_and_stakeholders, seed_ops_overlay
from app.ingestion.pipeline import ingest_runbooks_directory


def clear_graph() -> None:
    run_query("MATCH (n) DETACH DELETE n")


def seed_graph() -> int:
    count = seed_applications_and_stakeholders()
    seed_ops_overlay()
    return count


def seed_vectors() -> int:
    result = ingest_runbooks_directory(rebuild=True)
    if result.get("status") != "ok":
        raise RuntimeError(result.get("message", "Runbook ingestion failed"))
    return int(result["chunks"])


def main() -> None:
    print("Clearing Neo4j...")
    clear_graph()
    print("Seeding graph (100 applications + stakeholder mapping)...")
    app_count = seed_graph()
    nodes = run_query("MATCH (n) RETURN count(n) AS c")[0]["c"]
    apps = run_query("MATCH (a:Application) RETURN count(a) AS c")[0]["c"]
    print(f"Applications loaded: {apps} (catalog size {app_count})")
    print(f"Total Neo4j nodes: {nodes}")
    print("Seeding vector store...")
    chunks = seed_vectors()
    print(f"Chroma chunks indexed: {chunks}")
    print("Done.")


if __name__ == "__main__":
    main()
