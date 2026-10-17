"""Run golden-set evaluation: GraphRAG vs vector-only retrieval quality."""

import argparse
import json
from pathlib import Path

from app.graph.retriever import graph_context_for_question
from app.rag.graph_agent import run_query
from app.rag.vector_store import vector_retrieve


def load_golden(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def keyword_score(text: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    lower = text.lower()
    hits = sum(1 for k in keywords if k.lower() in lower)
    return hits / len(keywords)


def eval_retrieval_only(question: str, must_include: list[str]) -> dict:
    g_ctx, _ = graph_context_for_question(question)
    v_ctx, _ = vector_retrieve(question)
    return {
        "graph_retrieval_score": keyword_score(g_ctx, must_include),
        "vector_retrieval_score": keyword_score(v_ctx, must_include),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("/eval/golden_dataset.json"),
    )
    parser.add_argument("--report", type=Path, default=Path("eval_report.json"))
    parser.add_argument("--with-llm", action="store_true", help="Also run full GraphRAG answers (uses OpenAI)")
    args = parser.parse_args()

    if not args.dataset.exists():
        args.dataset = Path(__file__).resolve().parents[3] / "eval" / "golden_dataset.json"

    data = load_golden(args.dataset)
    results = []
    graph_wins = 0
    vector_wins = 0
    ties = 0

    for case in data["cases"]:
        must = case.get("must_include") or []
        retrieval = eval_retrieval_only(case["question"], must)
        row = {
            "id": case["id"],
            "question": case["question"],
            "preferred_route": case.get("preferred_route"),
            **retrieval,
        }
        g = retrieval["graph_retrieval_score"]
        v = retrieval["vector_retrieval_score"]
        if g > v:
            graph_wins += 1
            row["retrieval_winner"] = "graph"
        elif v > g:
            vector_wins += 1
            row["retrieval_winner"] = "vector"
        else:
            ties += 1
            row["retrieval_winner"] = "tie"

        if args.with_llm:
            full = run_query(case["question"], mode="auto")
            row["answer_score"] = keyword_score(full["answer"], must)
            row["route"] = full["route"]
            if case.get("expect_refusal"):
                row["refusal_ok"] = "cannot" in full["answer"].lower() or "could not" in full["answer"].lower()

        results.append(row)

    report = {
        "summary": {
            "total": len(results),
            "graph_retrieval_wins": graph_wins,
            "vector_retrieval_wins": vector_wins,
            "ties": ties,
        },
        "results": results,
    }
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Wrote {args.report}")


if __name__ == "__main__":
    main()
