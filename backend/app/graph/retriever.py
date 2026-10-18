"""Structured graph retrieval for ops-center incident questions."""

import re
from typing import Any

from app.graph.application_catalog import application_names
from app.graph.neo4j_client import run_query

APP_PATTERN = re.compile(r"\b([A-Z][A-Za-z0-9-]{2,})\b")

_APP_NAMES_CACHE: list[str] | None = None


def _all_app_names() -> list[str]:
    global _APP_NAMES_CACHE
    if _APP_NAMES_CACHE is None:
        try:
            _APP_NAMES_CACHE = sorted(application_names(), key=len, reverse=True)
        except Exception:
            _APP_NAMES_CACHE = []
    return _APP_NAMES_CACHE


def extract_app_name(question: str) -> str | None:
    """Match longest application name appearing in the question (100-app catalog)."""
    q_lower = question.lower()
    for name in _all_app_names():
        if name.lower() in q_lower:
            return name
    known = set(_all_app_names())
    for match in APP_PATTERN.findall(question):
        if match in known:
            return match
    return None


def graph_context_for_question(question: str) -> tuple[str, list[dict[str, Any]]]:
    """Build human-readable graph context and raw records for citations."""
    app = extract_app_name(question)
    blocks: list[str] = []
    records: list[dict[str, Any]] = []

    q_lower = question.lower()
    if app:
        profile = run_query(
            """
            MATCH (a:Application {name: $app})
            OPTIONAL MATCH (a)<-[:OWNS]-(t:Team)
            OPTIONAL MATCH (sme:Person)-[:SME_FOR]->(a)
            OPTIONAL MATCH (em:Person)-[:ENG_MANAGER_FOR]->(a)
            OPTIONAL MATCH (pm:Person)-[:PRODUCT_MANAGER_FOR]->(a)
            OPTIONAL MATCH (dir:Person)-[:DIRECTOR_FOR]->(a)
            OPTIONAL MATCH (oncall:Person)-[:PRIMARY_CONTACT_FOR]->(a)
            RETURN a.name AS app, a.description AS description, a.tier AS tier,
                   a.criticality AS criticality, t.name AS team,
                   sme { .name, .email, .title } AS sme,
                   em { .name, .email, .title } AS eng_manager,
                   pm { .name, .email, .title } AS product_manager,
                   dir { .name, .email, .title } AS director,
                   collect(DISTINCT oncall { .name, .email, .role, .on_call }) AS on_call_contacts
            LIMIT 1
            """,
            {"app": app},
        )
        if profile:
            records.extend(profile)
            o = profile[0]
            desc = o.get("description") or ""
            blocks.append(
                f"Application {o['app']} (tier {o['tier']}, criticality {o['criticality']}) — {desc}"
            )
            if o.get("team"):
                blocks.append(f"Owning team / domain: {o['team']}.")
            for label, key in (
                ("SME", "sme"),
                ("Engineering Manager", "eng_manager"),
                ("Product Manager", "product_manager"),
                ("Director", "director"),
            ):
                person = o.get(key)
                if person and person.get("name"):
                    title = person.get("title") or label
                    blocks.append(f"{label}: {person['name']} ({title}) — {person.get('email', '')}")
            for person in o.get("on_call_contacts") or []:
                if person.get("name"):
                    oc = " [ON-CALL]" if person.get("on_call") else ""
                    blocks.append(
                        f"Ops primary contact: {person['name']} ({person.get('role', 'engineer')}) "
                        f"{person.get('email', '')}{oc}"
                    )

        deps = run_query(
            """
            MATCH (a:Application {name: $app})-[:DEPENDS_ON*1..3]->(d:Application)
            RETURN DISTINCT d.name AS dependency, d.tier AS tier, d.criticality AS criticality
            ORDER BY d.name
            LIMIT 15
            """,
            {"app": app},
        )
        if deps:
            records.extend(deps)
            names = ", ".join(f"{d['dependency']} ({d['tier']})" for d in deps)
            blocks.append(f"Downstream dependencies (blast radius): {names}.")

        upstream = run_query(
            """
            MATCH (u:Application)-[:DEPENDS_ON*1..2]->(a:Application {name: $app})
            RETURN DISTINCT u.name AS upstream, u.tier AS tier
            ORDER BY u.name
            LIMIT 10
            """,
            {"app": app},
        )
        if upstream:
            records.extend(upstream)
            blocks.append(
                "Upstream callers that may be impacted: "
                + ", ".join(f"{u['upstream']} ({u['tier']})" for u in upstream)
                + "."
            )

    if "change" in q_lower or "cr-" in q_lower or "deployment" in q_lower:
        crs = run_query(
            """
            MATCH (cr:ChangeRequest)-[:AFFECTS]->(a:Application)
            WHERE cr.status IN ['IN_PROGRESS', 'SCHEDULED']
            RETURN cr.id AS change_id, cr.title AS title, cr.status AS status,
                   cr.window AS window, cr.owner AS owner, collect(a.name) AS apps
            ORDER BY cr.id
            LIMIT 10
            """
        )
        if crs:
            records.extend(crs)
            for cr in crs:
                blocks.append(
                    f"Active change {cr['change_id']}: {cr['title']} ({cr['status']}), "
                    f"window {cr['window']}, owner {cr['owner']}, apps: {', '.join(cr['apps'])}."
                )
        if app:
            linked = run_query(
                """
                MATCH (cr:ChangeRequest)-[:AFFECTS]->(a:Application {name: $app})
                WHERE cr.status IN ['IN_PROGRESS', 'SCHEDULED']
                RETURN cr.id AS change_id, cr.title AS title, cr.status AS status,
                       cr.ack_ticket AS ack_ticket, cr.details AS details
                """,
                {"app": app},
            )
            if linked:
                records.extend(linked)
                for cr in linked:
                    blocks.append(
                        f"Change aligned to {app}: {cr['change_id']} — {cr['title']}. "
                        f"Acknowledge via ticket {cr['ack_ticket']}. Details: {cr['details']}"
                    )

    if "escalat" in q_lower or "sme" in q_lower or "report" in q_lower:
        paths = run_query(
            """
            MATCH (e:EscalationLevel)
            OPTIONAL MATCH (e)-[:NEXT]->(n:EscalationLevel)
            RETURN e.level AS level, e.role AS role, e.sla_minutes AS sla,
                   e.required_fields AS fields, n.level AS next_level
            ORDER BY e.level
            """
        )
        if paths:
            records.extend(paths)
            for row in paths:
                blocks.append(
                    f"Escalation L{row['level']} ({row['role']}): SLA {row['sla']} min. "
                    f"Required fields: {row['fields']}. Next: L{row.get('next_level')}."
                )

    if not blocks:
        summary = run_query(
            """
            MATCH (a:Application)
            OPTIONAL MATCH (a)<-[:OWNS]-(t:Team)
            RETURN a.name AS app, t.name AS team
            ORDER BY a.name
            LIMIT 8
            """
        )
        records.extend(summary)
        blocks.append(
            "Sample applications in graph: "
            + "; ".join(f"{s['app']} → {s.get('team')}" for s in summary)
            + ". Ask about a specific application by name."
        )

    return "\n".join(blocks), records
