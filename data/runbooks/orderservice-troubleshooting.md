---
title: OrderService Troubleshooting Runbook
doc_type: runbook
application: OrderService
version: "1.8"
---

## Common symptoms

- Orders stuck in `PENDING_PAYMENT`
- Checkout timeout from CustomerPortal or MobileBackend
- Inventory reservation failures

## Dependency order (check top-down)

1. **AuthService** — token validation errors block checkout APIs.
2. **PaymentGateway** — payment authorization failures leave orders pending.
3. **InventoryAPI** — stock reservation errors cause checkout rollback.

## Quick checks

- Order API error rate by endpoint (`POST /orders`, `/orders/{id}/commit`)
- DB index rebuild CR — expect read latency spike during maintenance window
- Queue depth on `order-events` Kafka topic

## Mitigation

- Enable **read-only checkout** flag only with Product approval (reduces new orders during partial outage).
- Roll back last deployment if error rate jumped within 15 minutes of release.
- Page Commerce Core on-call; notify Customer Experience if portal impact > 5 minutes.

## Customer messaging

Use template **COMMS-ORDER-DEGRADED**: “Checkout may be slower than usual; orders are safe once confirmation email sends.”
