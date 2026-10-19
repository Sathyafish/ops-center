"""Detect when a question cannot be answered from ops graph + runbooks."""

from __future__ import annotations

import re

from app.graph.retriever import extract_app_name

# Not in corpus — refuse without calling the LLM
OUT_OF_SCOPE_PHRASES = (
    "pricing model",
    "saas pricing",
    "our saas product",
    "product pricing",
    "subscription price",
    "how much do we charge",
    "stock price",
    "company revenue",
    "earnings report",
    "marketing campaign",
    "hr policy vacation",
)

OPS_TOPIC_HINTS = (
    "incident",
    "outage",
    "down",
    "contact",
    "sme",
    "on-call",
    "oncall",
    "depend",
    "blast",
    "impact",
    "change",
    "cr-",
    "escalat",
    "runbook",
    "troubleshoot",
    "ack",
    "tier-",
    "application",
    "service",
    "portal",
    "gateway",
    "api",
    "who owns",
    "who is the",
)

STOPWORDS = frozenset(
    "a an the is are was were what how when where who which our we do does for of in on to".split()
)


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9][a-z0-9-]{2,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


REFUSAL_MESSAGE = (
    "I could not find this in the ops knowledge base (application graph and runbooks). "
    "This system covers incident contacts, dependencies, changes, escalation, and troubleshooting procedures. "
    "Try naming a specific application (e.g. PaymentGateway), a change ID (CR-xxxx), or ask about runbook steps."
)


def is_out_of_scope_question(question: str) -> bool:
    q = question.lower()
    return any(phrase in q for phrase in OUT_OF_SCOPE_PHRASES)


def graph_context_is_generic_fallback(graph_context: str) -> bool:
    return "Sample applications in graph:" in (graph_context or "")


def context_supports_question(question: str, graph_context: str, vector_context: str) -> bool:
    """Heuristic: enough overlap between question and retrieved text."""
    if extract_app_name(question):
        return True
    q_lower = question.lower()
    if any(h in q_lower for h in OPS_TOPIC_HINTS):
        # Ops-shaped question — require some overlap with context
        combined = f"{graph_context}\n{vector_context}".lower()
        if vector_context.strip().startswith("No vector documents"):
            return graph_context_is_generic_fallback(graph_context) is False and bool(combined.strip())
        q_tok = _tokens(question)
        ctx_tok = _tokens(combined)
        overlap = q_tok & ctx_tok
        return len(overlap) >= 2
    return False


def check_should_refuse(question: str, graph_context: str, vector_context: str) -> tuple[bool, str]:
    if is_out_of_scope_question(question):
        return True, REFUSAL_MESSAGE
    if graph_context_is_generic_fallback(graph_context) and not extract_app_name(question):
        if not context_supports_question(question, graph_context, vector_context):
            return True, REFUSAL_MESSAGE
    if not context_supports_question(question, graph_context, vector_context):
        if not extract_app_name(question):
            return True, REFUSAL_MESSAGE
    return False, ""
