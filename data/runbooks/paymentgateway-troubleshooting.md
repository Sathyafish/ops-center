---
title: PaymentGateway Troubleshooting Runbook
doc_type: runbook
application: PaymentGateway
version: "3.1"
---

## Common symptoms

- HTTP **502/503** on checkout or authorize endpoints
- Elevated latency on `/v1/charge`
- TLS or certificate warnings in edge logs

## Quick checks

1. **Certificate expiry** — Dashboard `PGW-Certs`; if rotation in progress, see active CR (often TLS rotation).
2. **AuthService dependency** — PaymentGateway validates tokens via AuthService; if auth error rate spikes, fix auth first.
3. **Regional health** — Compare primary vs secondary region request success rate.
4. **Recent changes** — Filter changes affecting PaymentGateway in the last 24 hours.

## Mitigation paths

| Condition | Action |
|-----------|--------|
| Edge 502 during cert rotation | Fail over to secondary region per **DR-12** |
| Auth 401/403 spike | Engage Identity on-call; do not disable fraud checks |
| DB connection pool exhausted | Scale read replicas; engage DBA if persist > 15 min |

## Escalation

Primary: Payments Platform on-call. SEV1: open major incident bridge and notify Commerce Core (OrderService dependency).

## Log queries (examples)

- `service=payment-gateway status>=500 | stats count by region`
- `error="certificate verify failed" | last 1h`
