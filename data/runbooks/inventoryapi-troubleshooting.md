---
title: InventoryAPI Troubleshooting Runbook
doc_type: runbook
application: InventoryAPI
version: "1.3"
---

## Common symptoms

- “Out of stock” for known in-stock SKUs
- Slow product detail pages (SearchIndex cache stale)
- ShippingTracker shows incorrect availability

## Checks

1. Cache hit ratio on inventory Redis cluster
2. Replication lag on inventory primary → read replicas
3. Upstream **OrderService** reservation timeout logs

## Mitigation

- Flush stale SKU cache keys for affected product ids (list in ticket)
- Shift read traffic to replica with lag < 2s
- If data corruption suspected: stop manual stock adjustments; engage Commerce Core SME

## Escalation

Commerce Core team; SEV2 if checkout blocked nationwide > 20 minutes.
