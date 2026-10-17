---
title: Database Connection Timeout Playbook
doc_type: runbook
application: ""
version: "1.0"
---

## Symptoms

Applications log `connection pool exhausted`, `timeout acquiring connection`, or ORM `TooManyConnections`.

## Triage

1. Identify **which database cluster** (orders-db, payments-db, auth-redis, etc.) from the app runbook.
2. Check DBA dashboard: active connections, CPU, lock waits, long-running queries.
3. Correlate with **index rebuild** or **migration** change windows.

## Safe mitigations

- Restart unhealthy app pods **one AZ at a time** to release leaked connections (not all at once).
- Reduce max pool size temporarily only with app owner approval.
- Kill identified long-running analytics queries (DBA only).

## Do not

- Increase pool size unbounded — can overwhelm the database and cause cluster-wide failure.
- Run schema migrations during active SEV1 unless directed by incident commander.
