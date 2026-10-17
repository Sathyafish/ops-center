"""Seed Neo4j graph (20+ nodes) and ingest runbook markdown into Chroma."""

from app.graph.neo4j_client import run_query
from app.ingestion.pipeline import ingest_runbooks_directory


def clear_graph() -> None:
    run_query("MATCH (n) DETACH DELETE n")


def seed_graph() -> None:
    run_query(
        """
        CREATE (t1:Team {name: 'Payments Platform'})
        CREATE (t2:Team {name: 'Commerce Core'})
        CREATE (t3:Team {name: 'Identity & Access'})
        CREATE (t4:Team {name: 'Data Platform'})
        CREATE (t5:Team {name: 'Customer Experience'})
        CREATE (t6:Team {name: 'Ops Center'})

        CREATE (p1:Person {name: 'Alice Chen', email: 'alice.chen@enterprise.com', role: 'lead', on_call: true})
        CREATE (p2:Person {name: 'Bob Martinez', email: 'bob.m@enterprise.com', role: 'engineer', on_call: false})
        CREATE (p3:Person {name: 'Carol Okonkwo', email: 'carol.o@enterprise.com', role: 'engineer', on_call: true})
        CREATE (p4:Person {name: 'Dave Patel', email: 'dave.p@enterprise.com', role: 'sre', on_call: false})
        CREATE (p5:Person {name: 'Eve Nguyen', email: 'eve.n@enterprise.com', role: 'oncall', on_call: true})
        CREATE (p6:Person {name: 'Frank Li', email: 'frank.l@enterprise.com', role: 'manager', on_call: false})
        CREATE (p7:Person {name: 'Grace Kim', email: 'grace.k@enterprise.com', role: 'engineer', on_call: false})

        CREATE (a1:Application {name: 'PaymentGateway', tier: 'Tier-0', criticality: 'critical'})
        CREATE (a2:Application {name: 'OrderService', tier: 'Tier-0', criticality: 'critical'})
        CREATE (a3:Application {name: 'InventoryAPI', tier: 'Tier-1', criticality: 'high'})
        CREATE (a4:Application {name: 'CustomerPortal', tier: 'Tier-1', criticality: 'high'})
        CREATE (a5:Application {name: 'AuthService', tier: 'Tier-0', criticality: 'critical'})
        CREATE (a6:Application {name: 'NotificationHub', tier: 'Tier-2', criticality: 'medium'})
        CREATE (a7:Application {name: 'BillingEngine', tier: 'Tier-1', criticality: 'high'})
        CREATE (a8:Application {name: 'DataWarehouse', tier: 'Tier-1', criticality: 'high'})
        CREATE (a9:Application {name: 'CRMConnector', tier: 'Tier-2', criticality: 'medium'})
        CREATE (a10:Application {name: 'ShippingTracker', tier: 'Tier-2', criticality: 'medium'})
        CREATE (a11:Application {name: 'FraudDetection', tier: 'Tier-1', criticality: 'high'})
        CREATE (a12:Application {name: 'MobileBackend', tier: 'Tier-1', criticality: 'high'})
        CREATE (a13:Application {name: 'SearchIndex', tier: 'Tier-2', criticality: 'medium'})
        CREATE (a14:Application {name: 'LegacyMainframe', tier: 'Tier-0', criticality: 'critical'})
        CREATE (a15:Application {name: 'HRPortal', tier: 'Tier-3', criticality: 'low'})

        CREATE (cr1:ChangeRequest {
            id: 'CR-10482', title: 'PaymentGateway TLS cert rotation',
            status: 'IN_PROGRESS', window: '2026-10-16 14:00-16:00 UTC',
            owner: 'Alice Chen', ack_ticket: 'OPS-8891',
            details: 'Rolling cert update; expect brief 502s on edge nodes.'
        })
        CREATE (cr2:ChangeRequest {
            id: 'CR-10490', title: 'OrderService DB index rebuild',
            status: 'SCHEDULED', window: '2026-10-17 02:00-04:00 UTC',
            owner: 'Bob Martinez', ack_ticket: 'OPS-8902',
            details: 'Read latency may spike; no write outage expected.'
        })
        CREATE (cr3:ChangeRequest {
            id: 'CR-10477', title: 'AuthService session store migration',
            status: 'IN_PROGRESS', window: '2026-10-16 12:00-18:00 UTC',
            owner: 'Carol Okonkwo', ack_ticket: 'OPS-8875',
            details: 'Users may need to re-login once per region.'
        })

        CREATE (e1:EscalationLevel {level: 1, role: 'Ops Center L1', sla_minutes: 15,
            required_fields: 'incident_id, app, severity, start_time, customer_impact'})
        CREATE (e2:EscalationLevel {level: 2, role: 'Service Owner SME', sla_minutes: 30,
            required_fields: 'timeline, logs, change_ids, mitigation, blast_radius'})
        CREATE (e3:EscalationLevel {level: 3, role: 'Director / Major Incident', sla_minutes: 60,
            required_fields: 'executive_summary, comms_status, root_cause_hypothesis'})

        MERGE (t1)-[:OWNS]->(a1)
        MERGE (t1)-[:OWNS]->(a7)
        MERGE (t2)-[:OWNS]->(a2)
        MERGE (t2)-[:OWNS]->(a3)
        MERGE (t2)-[:OWNS]->(a10)
        MERGE (t3)-[:OWNS]->(a5)
        MERGE (t4)-[:OWNS]->(a8)
        MERGE (t4)-[:OWNS]->(a13)
        MERGE (t5)-[:OWNS]->(a4)
        MERGE (t5)-[:OWNS]->(a6)
        MERGE (t5)-[:OWNS]->(a9)
        MERGE (t5)-[:OWNS]->(a12)
        MERGE (t2)-[:OWNS]->(a11)
        MERGE (t4)-[:OWNS]->(a14)
        MERGE (t6)-[:OWNS]->(a15)

        MERGE (p1)-[:MEMBER_OF]->(t1)
        MERGE (p2)-[:MEMBER_OF]->(t2)
        MERGE (p3)-[:MEMBER_OF]->(t3)
        MERGE (p4)-[:MEMBER_OF]->(t4)
        MERGE (p5)-[:MEMBER_OF]->(t6)
        MERGE (p6)-[:MEMBER_OF]->(t1)
        MERGE (p7)-[:MEMBER_OF]->(t5)

        MERGE (p1)-[:PRIMARY_CONTACT_FOR]->(a1)
        MERGE (p2)-[:PRIMARY_CONTACT_FOR]->(a2)
        MERGE (p3)-[:PRIMARY_CONTACT_FOR]->(a5)
        MERGE (p4)-[:PRIMARY_CONTACT_FOR]->(a8)
        MERGE (p7)-[:PRIMARY_CONTACT_FOR]->(a4)

        MERGE (a2)-[:DEPENDS_ON]->(a1)
        MERGE (a2)-[:DEPENDS_ON]->(a5)
        MERGE (a2)-[:DEPENDS_ON]->(a3)
        MERGE (a4)-[:DEPENDS_ON]->(a2)
        MERGE (a4)-[:DEPENDS_ON]->(a5)
        MERGE (a12)-[:DEPENDS_ON]->(a2)
        MERGE (a12)-[:DEPENDS_ON]->(a5)
        MERGE (a7)-[:DEPENDS_ON]->(a1)
        MERGE (a7)-[:DEPENDS_ON]->(a14)
        MERGE (a11)-[:DEPENDS_ON]->(a1)
        MERGE (a11)-[:DEPENDS_ON]->(a2)
        MERGE (a6)-[:DEPENDS_ON]->(a2)
        MERGE (a9)-[:DEPENDS_ON]->(a4)
        MERGE (a10)-[:DEPENDS_ON]->(a2)
        MERGE (a10)-[:DEPENDS_ON]->(a3)
        MERGE (a8)-[:DEPENDS_ON]->(a2)
        MERGE (a8)-[:DEPENDS_ON]->(a7)
        MERGE (a13)-[:DEPENDS_ON]->(a2)
        MERGE (a1)-[:DEPENDS_ON]->(a5)

        MERGE (cr1)-[:AFFECTS]->(a1)
        MERGE (cr2)-[:AFFECTS]->(a2)
        MERGE (cr3)-[:AFFECTS]->(a5)
        MERGE (cr3)-[:AFFECTS]->(a4)

        MERGE (e1)-[:NEXT]->(e2)
        MERGE (e2)-[:NEXT]->(e3)
        """
    )


def seed_vectors() -> int:
    result = ingest_runbooks_directory(rebuild=True)
    if result.get("status") != "ok":
        raise RuntimeError(result.get("message", "Runbook ingestion failed"))
    return int(result["chunks"])


def main() -> None:
    print("Clearing Neo4j...")
    clear_graph()
    print("Seeding graph...")
    seed_graph()
    count = run_query("MATCH (n) RETURN count(n) AS c")[0]["c"]
    print(f"Neo4j nodes: {count}")
    print("Seeding vector store...")
    chunks = seed_vectors()
    print(f"Chroma chunks indexed: {chunks}")
    print("Done.")


if __name__ == "__main__":
    main()
