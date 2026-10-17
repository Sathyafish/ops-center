---
title: Correlating Incidents with In-Flight Changes
doc_type: procedure
application: ""
version: "1.0"
---

## When to correlate

Correlate when symptoms started **during or after** a change window, or when monitoring shows errors tied to a deployment/certificate/database task.

## Acknowledgment procedure

1. In the **OPS incident ticket**, add related change id (e.g. `CR-10477`).
2. Open the change **ack ticket** (format `OPS-XXXX` on the change record).
3. Comment: `Incident correlated to CR-XXXX — investigating overlap with change window.`
4. @ mention the **change owner** and request confirmation of rollback status.
5. Do **not** mark the change **Closed** until the incident commander confirms safe completion or rollback.

## Information to pull from the change record

- Change title and implementation window (UTC)
- Owner and implementation team
- Expected customer impact statement from the CR
- Rollback plan summary
