---
title: SME L2 Escalation Report Template
doc_type: template
application: ""
version: "2.0"
---

## Required fields (L2 SME handoff)

| Field | Description |
|-------|-------------|
| incident_id | OPS or PagerDuty id |
| affected_application | CMDB application name |
| severity | SEV1–SEV4 |
| customer_impact | Orders/minutes affected, regions |
| timeline | UTC timestamps: detection, escalation, mitigations |
| primary_on_call_contacted | Name + ack time |
| active_change_ids | e.g. CR-10482 or “none” |
| logs_and_dashboards | Links or excerpt (no secrets/PII) |
| mitigation_steps | What was tried and outcome |
| blast_radius | Upstream/downstream apps affected |
| next_update | When Ops will publish next status |

## Narrative section

Write a short paragraph summarizing **what broke**, **what we know**, and **what we need from the SME** (e.g. approve rollback, validate DB query plan).

## SLA

L2 SME acknowledgment target: **30 minutes** from L1 escalation. L3 director engagement per major-incident policy.
