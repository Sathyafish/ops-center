---
title: Ops Center L1 Incident Triage
doc_type: procedure
application: ""
version: "1.2"
---

## Purpose

Standard first-response checklist for any production incident reported to the Ops Center command desk.

## Steps

1. **Identify the application** — Confirm the CMDB name with the reporter (e.g. PaymentGateway, not “payments”).
2. **Set severity** — SEV1: Tier-0 outage or widespread customer impact. SEV2: degraded Tier-0/1. SEV3/4: limited scope.
3. **Check the status page** — Note existing customer-facing incidents to avoid duplicate comms.
4. **Search active changes** — In the change calendar, filter `IN_PROGRESS` and `SCHEDULED` for the affected app.
5. **Page ownership** — Use the graph/on-call matrix for primary contact; include backup if no ack in 10 minutes.
6. **Open a bridge** — Required for SEV1/SEV2; record bridge link in the OPS ticket.
7. **Document within 15 minutes** — OPS ticket must include start time (UTC), app, severity, and initial impact statement.

## When to escalate to L2 SME

Escalate when mitigation requires code/config change, root cause is unknown after 30 minutes, or blast radius expands beyond the initial app.
