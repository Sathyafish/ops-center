---
title: AuthService Troubleshooting Runbook
doc_type: runbook
application: AuthService
version: "2.4"
---

## Common symptoms

- Users forced to re-login across regions
- Spike in `session_store_timeout` errors
- Mobile and portal login failures simultaneously

## Quick checks

1. **Session store** — Redis/ElastiCache latency and memory; check migration CR if session store move is in progress.
2. **LegacyMainframe bridge** — Some enterprise SSO paths still proxy through mainframe; check MF health dashboard.
3. **Dependent apps** — OrderService, CustomerPortal, MobileBackend, PaymentGateway all depend on AuthService.

## Mitigation paths

- If session migration CR is active: communicate “single re-login expected” on status page; extend session TTL only with Identity approval.
- If Redis down: fail over to read replica; invoke **AUTH-DR-03** runbook.
- If SSO provider outage: enable maintenance banner; disable password reset flood via rate limit.

## Data to capture for SME

Session error rate by region, Redis CPU/memory, last successful deployment hash, linked change ids.
