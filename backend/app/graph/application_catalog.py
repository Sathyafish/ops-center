"""Enterprise application catalog (100 apps) for Neo4j GraphRAG seeding."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CATALOG_VERSION = "1.0"
APP_COUNT = 100

# Canonical apps used in runbooks, eval, and demo incidents
CANONICAL_APPS: list[dict[str, Any]] = [
    {
        "name": "PaymentGateway",
        "description": "Primary card and ACH payment authorization service for all digital channels.",
        "domain": "Payments Platform",
        "tier": "Tier-0",
        "criticality": "critical",
        "depends_on": ["AuthService"],
    },
    {
        "name": "OrderService",
        "description": "Order capture, checkout orchestration, and order lifecycle API.",
        "domain": "Commerce Core",
        "tier": "Tier-0",
        "criticality": "critical",
        "depends_on": ["PaymentGateway", "AuthService", "InventoryAPI"],
    },
    {
        "name": "InventoryAPI",
        "description": "Real-time stock reservations and SKU availability for commerce.",
        "domain": "Commerce Core",
        "tier": "Tier-1",
        "criticality": "high",
        "depends_on": ["AuthService"],
    },
    {
        "name": "CustomerPortal",
        "description": "Logged-in customer web experience for orders, profile, and support.",
        "domain": "Customer Experience",
        "tier": "Tier-1",
        "criticality": "high",
        "depends_on": ["OrderService", "AuthService"],
    },
    {
        "name": "AuthService",
        "description": "Enterprise SSO, session management, and OAuth token issuance.",
        "domain": "Identity & Access",
        "tier": "Tier-0",
        "criticality": "critical",
        "depends_on": ["LegacyMainframe"],
    },
    {
        "name": "NotificationHub",
        "description": "Email, SMS, and push notification dispatch for transactional events.",
        "domain": "Customer Experience",
        "tier": "Tier-2",
        "criticality": "medium",
        "depends_on": ["OrderService"],
    },
    {
        "name": "BillingEngine",
        "description": "Subscription billing, invoicing, and revenue recognition batch jobs.",
        "domain": "Payments Platform",
        "tier": "Tier-1",
        "criticality": "high",
        "depends_on": ["PaymentGateway", "LegacyMainframe"],
    },
    {
        "name": "DataWarehouse",
        "description": "Analytics warehouse ingesting operational feeds for BI and finance.",
        "domain": "Data Platform",
        "tier": "Tier-1",
        "criticality": "high",
        "depends_on": ["OrderService", "BillingEngine"],
    },
    {
        "name": "CRMConnector",
        "description": "Syncs customer profiles and cases with Salesforce CRM.",
        "domain": "Customer Experience",
        "tier": "Tier-2",
        "criticality": "medium",
        "depends_on": ["CustomerPortal"],
    },
    {
        "name": "ShippingTracker",
        "description": "Shipment status aggregation from carriers for post-purchase tracking.",
        "domain": "Commerce Core",
        "tier": "Tier-2",
        "criticality": "medium",
        "depends_on": ["OrderService", "InventoryAPI"],
    },
    {
        "name": "FraudDetection",
        "description": "Real-time scoring and rules engine for checkout fraud prevention.",
        "domain": "Commerce Core",
        "tier": "Tier-1",
        "criticality": "high",
        "depends_on": ["PaymentGateway", "OrderService"],
    },
    {
        "name": "MobileBackend",
        "description": "BFF API for iOS and Android retail applications.",
        "domain": "Customer Experience",
        "tier": "Tier-1",
        "criticality": "high",
        "depends_on": ["OrderService", "AuthService"],
    },
    {
        "name": "SearchIndex",
        "description": "Product catalog search indexing and query service.",
        "domain": "Data Platform",
        "tier": "Tier-2",
        "criticality": "medium",
        "depends_on": ["OrderService"],
    },
    {
        "name": "LegacyMainframe",
        "description": "COBOL host system for core ledger and legacy SSO bridge.",
        "domain": "Data Platform",
        "tier": "Tier-0",
        "criticality": "critical",
        "depends_on": [],
    },
    {
        "name": "HRPortal",
        "description": "Employee self-service HR, benefits, and org directory.",
        "domain": "Ops Center",
        "tier": "Tier-3",
        "criticality": "low",
        "depends_on": ["AuthService"],
    },
]

DOMAINS: list[tuple[str, list[str]]] = [
    ("Payments Platform", ["Settlement", "Reconciliation", "Dispute", "Refund", "Wallet", "Treasury"]),
    ("Commerce Core", ["Catalog", "Pricing", "Promotion", "Cart", "Checkout", "Returns"]),
    ("Identity & Access", ["MFA", "Directory", "Provisioning", "Secrets", "Certificate", "Policy"]),
    ("Data Platform", ["Pipeline", "Lakehouse", "Metrics", "FeatureStore", "MDM", "Archive"]),
    ("Customer Experience", ["Chatbot", "Survey", "Loyalty", "Recommendations", "Content", "Personalization"]),
    ("Finance Systems", ["GL", "AP", "AR", "Tax", "Payroll", "Expense"]),
    ("Supply Chain", ["WMS", "TMS", "Vendor", "Procurement", "Forecast", "Allocation"]),
    ("Security Operations", ["SIEM", "VulnScan", "GRC", "DLP", "SOAR", "PKI"]),
    ("Integration Hub", ["ESB", "EventBus", "APIGateway", "FileTransfer", "Webhook", "SchemaRegistry"]),
    ("Marketing Tech", ["Campaign", "Attribution", "Segment", "EmailPref", "AdSync", "LeadRouter"]),
]

TIER_CYCLE = [
    ("Tier-0", "critical"),
    ("Tier-1", "high"),
    ("Tier-2", "medium"),
    ("Tier-3", "low"),
]

# Shared leadership pool (directors cover domains)
DIRECTORS = [
    {"name": "Diana Roth", "email": "diana.roth@enterprise.com", "title": "Director, Payments & Finance Tech"},
    {"name": "Ethan Brooks", "email": "ethan.brooks@enterprise.com", "title": "Director, Commerce & Supply Chain"},
    {"name": "Fatima Hassan", "email": "fatima.hassan@enterprise.com", "title": "Director, Identity & Security"},
    {"name": "George Walsh", "email": "george.walsh@enterprise.com", "title": "Director, Data & Analytics"},
    {"name": "Hannah Ortiz", "email": "hannah.ortiz@enterprise.com", "title": "Director, Customer Experience"},
    {"name": "Ian Cooper", "email": "ian.cooper@enterprise.com", "title": "Director, Platform Engineering"},
    {"name": "Julia Park", "email": "julia.park@enterprise.com", "title": "Director, Enterprise Applications"},
    {"name": "Kevin Singh", "email": "kevin.singh@enterprise.com", "title": "Director, Ops & Corporate Systems"},
]

FIRST_NAMES = [
    "Alex",
    "Jordan",
    "Morgan",
    "Riley",
    "Casey",
    "Taylor",
    "Jamie",
    "Quinn",
    "Avery",
    "Blake",
    "Cameron",
    "Drew",
    "Emerson",
    "Finley",
    "Harper",
]
LAST_NAMES = [
    "Chen",
    "Martinez",
    "Okonkwo",
    "Patel",
    "Nguyen",
    "Li",
    "Kim",
    "Johnson",
    "Williams",
    "Brown",
    "Davis",
    "Garcia",
    "Miller",
    "Wilson",
    "Anderson",
]


def _person(idx: int, role_suffix: str) -> dict[str, str]:
    fn = FIRST_NAMES[idx % len(FIRST_NAMES)]
    ln = LAST_NAMES[(idx // len(FIRST_NAMES)) % len(LAST_NAMES)]
    slug = f"{fn}.{ln}".lower()
    return {
        "name": f"{fn} {ln}",
        "email": f"{slug}.{role_suffix}@enterprise.com",
        "title": role_suffix.replace("_", " ").title(),
    }


def _director_for_domain(domain: str) -> dict[str, str]:
    domain_map = {
        "Payments Platform": DIRECTORS[0],
        "Finance Systems": DIRECTORS[0],
        "Commerce Core": DIRECTORS[1],
        "Supply Chain": DIRECTORS[1],
        "Identity & Access": DIRECTORS[2],
        "Security Operations": DIRECTORS[2],
        "Data Platform": DIRECTORS[3],
        "Integration Hub": DIRECTORS[5],
        "Customer Experience": DIRECTORS[4],
        "Marketing Tech": DIRECTORS[4],
        "Ops Center": DIRECTORS[7],
    }
    base = domain_map.get(domain, DIRECTORS[6])
    return {**base, "title": "Director"}


def _stakeholders(index: int, domain: str) -> dict[str, Any]:
    return {
        "sme": _person(index, "sme"),
        "eng_manager": _person(index + 17, "eng_mgr"),
        "product_manager": _person(index + 31, "pm"),
        "director": _director_for_domain(domain),
    }


def _expand_canonical(app: dict[str, Any], index: int) -> dict[str, Any]:
    stakeholders = _stakeholders(index, app["domain"])
    # Align demo contacts for flagship apps
    if app["name"] == "PaymentGateway":
        stakeholders["sme"] = {"name": "Alice Chen", "email": "alice.chen@enterprise.com", "title": "SME"}
        stakeholders["eng_manager"] = {
            "name": "Frank Li",
            "email": "frank.l@enterprise.com",
            "title": "Engineering Manager",
        }
    if app["name"] == "OrderService":
        stakeholders["sme"] = {"name": "Bob Martinez", "email": "bob.m@enterprise.com", "title": "SME"}
    if app["name"] == "AuthService":
        stakeholders["sme"] = {"name": "Carol Okonkwo", "email": "carol.o@enterprise.com", "title": "SME"}
    if app["name"] == "DataWarehouse":
        stakeholders["sme"] = {"name": "Dave Patel", "email": "dave.p@enterprise.com", "title": "SME"}
    if app["name"] == "CustomerPortal":
        stakeholders["sme"] = {"name": "Grace Kim", "email": "grace.k@enterprise.com", "title": "SME"}
    return {
        "name": app["name"],
        "description": app["description"],
        "domain": app["domain"],
        "tier": app["tier"],
        "criticality": app["criticality"],
        "depends_on": app.get("depends_on", []),
        **stakeholders,
    }


def generate_catalog() -> dict[str, Any]:
    applications: list[dict[str, Any]] = []
    used_names: set[str] = set()

    for i, app in enumerate(CANONICAL_APPS):
        row = _expand_canonical(app, i)
        applications.append(row)
        used_names.add(row["name"])

    idx = len(CANONICAL_APPS)
    suffixes = ["Service", "API", "Portal", "Hub", "Engine", "Worker", "Gateway", "Platform", "Sync", "Bridge"]
    while len(applications) < APP_COUNT:
        domain, stems = DOMAINS[idx % len(DOMAINS)]
        stem = stems[(idx // len(DOMAINS)) % len(stems)]
        suffix = suffixes[(idx // 3) % len(suffixes)]
        name = f"{stem}{suffix}"
        if name in used_names:
            name = f"{stem}{suffix}{idx}"
        used_names.add(name)
        tier, criticality = TIER_CYCLE[idx % len(TIER_CYCLE)]
        depends_on = ["AuthService"]
        if domain in ("Payments Platform", "Finance Systems") and name != "PaymentGateway":
            depends_on.append("PaymentGateway")
        if domain == "Commerce Core" and name not in ("OrderService", "InventoryAPI"):
            depends_on.append("OrderService")
        row = {
            "name": name,
            "description": (
                f"{name} supports {domain.lower()} capabilities including {stem.lower()} workflows "
                f"for internal and customer-facing operations."
            ),
            "domain": domain,
            "tier": tier,
            "criticality": criticality,
            "depends_on": depends_on,
            **_stakeholders(idx, domain),
        }
        applications.append(row)
        idx += 1

    return {
        "version": CATALOG_VERSION,
        "application_count": len(applications),
        "applications": applications,
    }


def catalog_paths() -> list[Path]:
    candidates = [
        Path("/data/graph/applications_catalog.json"),
        Path(__file__).resolve().parents[3] / "data" / "graph" / "applications_catalog.json",
    ]
    return candidates


def resolve_catalog_path() -> Path:
    for path in catalog_paths():
        if path.is_file():
            return path
    return catalog_paths()[-1]


def load_catalog() -> dict[str, Any]:
    path = resolve_catalog_path()
    if path.is_file():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return generate_catalog()


def save_catalog(path: Path | None = None) -> Path:
    target = path or resolve_catalog_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    data = generate_catalog()
    target.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return target


def application_names() -> list[str]:
    return [a["name"] for a in load_catalog().get("applications", [])]
