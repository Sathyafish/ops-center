"""Load application catalog into Neo4j with stakeholder relationships."""

from __future__ import annotations

from typing import Any

from app.graph.application_catalog import load_catalog
from app.graph.neo4j_client import run_query


def seed_applications_and_stakeholders() -> int:
    catalog = load_catalog()
    apps: list[dict[str, Any]] = catalog["applications"]

    run_query(
        """
        UNWIND $apps AS row
        MERGE (a:Application {name: row.name})
        SET a.description = row.description,
            a.domain = row.domain,
            a.tier = row.tier,
            a.criticality = row.criticality
        WITH a, row
        MERGE (t:Team {name: row.domain})
        MERGE (t)-[:OWNS]->(a)
        WITH a, row
        MERGE (sme:Person {email: row.sme.email})
        SET sme.name = row.sme.name, sme.role = 'SME', sme.title = coalesce(row.sme.title, 'SME')
        MERGE (sme)-[:SME_FOR]->(a)
        WITH a, row
        MERGE (em:Person {email: row.eng_manager.email})
        SET em.name = row.eng_manager.name, em.role = 'Engineering Manager',
            em.title = coalesce(row.eng_manager.title, 'Engineering Manager')
        MERGE (em)-[:ENG_MANAGER_FOR]->(a)
        WITH a, row
        MERGE (pm:Person {email: row.product_manager.email})
        SET pm.name = row.product_manager.name, pm.role = 'Product Manager',
            pm.title = coalesce(row.product_manager.title, 'Product Manager')
        MERGE (pm)-[:PRODUCT_MANAGER_FOR]->(a)
        WITH a, row
        MERGE (dir:Person {email: row.director.email})
        SET dir.name = row.director.name, dir.role = 'Director',
            dir.title = coalesce(row.director.title, 'Director')
        MERGE (dir)-[:DIRECTOR_FOR]->(a)
        """,
        {"apps": apps},
    )

    # Dependency edges (only where target app exists in catalog)
    names = {a["name"] for a in apps}
    dep_rows = []
    for app in apps:
        for dep in app.get("depends_on") or []:
            if dep in names and dep != app["name"]:
                dep_rows.append({"from": app["name"], "to": dep})
    if dep_rows:
        run_query(
            """
            UNWIND $deps AS d
            MATCH (a:Application {name: d.from})
            MATCH (b:Application {name: d.to})
            MERGE (a)-[:DEPENDS_ON]->(b)
            """,
            {"deps": dep_rows},
        )

    return len(apps)


def seed_ops_overlay() -> None:
    """Ops Center users, on-call contacts, change requests, escalation ladder."""
    run_query(
        """
        MERGE (t6:Team {name: 'Ops Center'})
        MERGE (p1:Person {email: 'alice.chen@enterprise.com'})
        SET p1.name = 'Alice Chen', p1.role = 'lead', p1.on_call = true
        MERGE (p2:Person {email: 'bob.m@enterprise.com'})
        SET p2.name = 'Bob Martinez', p2.role = 'engineer', p2.on_call = false
        MERGE (p5:Person {email: 'eve.n@enterprise.com'})
        SET p5.name = 'Eve Nguyen', p5.role = 'oncall', p5.on_call = true
        MERGE (p1)-[:MEMBER_OF]->(t6)
        MERGE (p2)-[:MEMBER_OF]->(t6)
        MERGE (p5)-[:MEMBER_OF]->(t6)

        WITH 1 AS _
        MATCH (a1:Application {name: 'PaymentGateway'})
        MATCH (a2:Application {name: 'OrderService'})
        MATCH (a4:Application {name: 'CustomerPortal'})
        MATCH (a5:Application {name: 'AuthService'})
        MATCH (a8:Application {name: 'DataWarehouse'})
        MERGE (p1)-[:PRIMARY_CONTACT_FOR]->(a1)
        MERGE (p2)-[:PRIMARY_CONTACT_FOR]->(a2)
        MERGE (p3:Person {email: 'carol.o@enterprise.com'})
        SET p3.name = 'Carol Okonkwo', p3.role = 'engineer', p3.on_call = true
        MERGE (p3)-[:PRIMARY_CONTACT_FOR]->(a5)
        MERGE (p4:Person {email: 'dave.p@enterprise.com'})
        SET p4.name = 'Dave Patel', p4.role = 'sre', p4.on_call = false
        MERGE (p4)-[:PRIMARY_CONTACT_FOR]->(a8)
        MERGE (p7:Person {email: 'grace.k@enterprise.com'})
        SET p7.name = 'Grace Kim', p7.role = 'engineer', p7.on_call = false
        MERGE (p7)-[:PRIMARY_CONTACT_FOR]->(a4)
        """
    )

    run_query(
        """
        MERGE (cr1:ChangeRequest {
            id: 'CR-10482', title: 'PaymentGateway TLS cert rotation',
            status: 'IN_PROGRESS', window: '2026-10-16 14:00-16:00 UTC',
            owner: 'Alice Chen', ack_ticket: 'OPS-8891',
            details: 'Rolling cert update; expect brief 502s on edge nodes.'
        })
        MERGE (cr2:ChangeRequest {
            id: 'CR-10490', title: 'OrderService DB index rebuild',
            status: 'SCHEDULED', window: '2026-10-17 02:00-04:00 UTC',
            owner: 'Bob Martinez', ack_ticket: 'OPS-8902',
            details: 'Read latency may spike; no write outage expected.'
        })
        MERGE (cr3:ChangeRequest {
            id: 'CR-10477', title: 'AuthService session store migration',
            status: 'IN_PROGRESS', window: '2026-10-16 12:00-18:00 UTC',
            owner: 'Carol Okonkwo', ack_ticket: 'OPS-8875',
            details: 'Users may need to re-login once per region.'
        })
        WITH cr1, cr2, cr3
        MATCH (a1:Application {name: 'PaymentGateway'})
        MATCH (a2:Application {name: 'OrderService'})
        MATCH (a4:Application {name: 'CustomerPortal'})
        MATCH (a5:Application {name: 'AuthService'})
        MERGE (cr1)-[:AFFECTS]->(a1)
        MERGE (cr2)-[:AFFECTS]->(a2)
        MERGE (cr3)-[:AFFECTS]->(a5)
        MERGE (cr3)-[:AFFECTS]->(a4)
        """
    )

    run_query(
        """
        MERGE (e1:EscalationLevel {level: 1})
        SET e1.role = 'Ops Center L1', e1.sla_minutes = 15,
            e1.required_fields = 'incident_id, app, severity, start_time, customer_impact'
        MERGE (e2:EscalationLevel {level: 2})
        SET e2.role = 'Service Owner SME', e2.sla_minutes = 30,
            e2.required_fields = 'timeline, logs, change_ids, mitigation, blast_radius'
        MERGE (e3:EscalationLevel {level: 3})
        SET e3.role = 'Director / Major Incident', e3.sla_minutes = 60,
            e3.required_fields = 'executive_summary, comms_status, root_cause_hypothesis'
        MERGE (e1)-[:NEXT]->(e2)
        MERGE (e2)-[:NEXT]->(e3)
        """
    )
