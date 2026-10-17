"""LangGraph flow: route → retrieve (graph/vector/both) → generate grounded answer."""

from typing import Literal, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from app.config import settings
from app.graph.retriever import graph_context_for_question
from app.rag.vector_store import vector_retrieve

SYSTEM_PROMPT = """You are Ops Center GraphRAG assistant for an enterprise command center.
Answer ONLY using the provided CONTEXT sections. If context is insufficient, say you cannot find it in the knowledge base and suggest what to clarify (application name, change ID, etc.).

Structure incident answers with:
1. Primary contacts / on-call
2. Dependency blast radius
3. Escalation / SME report fields if relevant
4. Related in-flight change requests and ack ticket if relevant

Cite sources inline as [Graph] or [Vector:n]."""


class AgentState(TypedDict):
    question: str
    mode: str
    route: str
    graph_context: str
    vector_context: str
    graph_records: list
    vector_meta: list
    answer: str


def _llm() -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=0)


def classify_route(state: AgentState) -> AgentState:
    mode = state.get("mode", "auto")
    if mode in ("graph", "vector"):
        return {**state, "route": mode}
    q = state["question"].lower()
    graph_hints = (
        "who",
        "contact",
        "own",
        "depend",
        "impact",
        "blast",
        "change",
        "cr-",
        "on-call",
        "oncall",
        "escalat",
        "team",
    )
    vector_hints = ("how", "template", "field", "procedure", "steps", "sme report", "format")
    if any(h in q for h in graph_hints):
        route = "graph" if not any(h in q for h in vector_hints) else "hybrid"
    elif any(h in q for h in vector_hints):
        route = "vector"
    else:
        route = "hybrid"
    return {**state, "route": route}


def retrieve_graph(state: AgentState) -> AgentState:
    ctx, records = graph_context_for_question(state["question"])
    return {**state, "graph_context": ctx, "graph_records": records}


def retrieve_vector(state: AgentState) -> AgentState:
    ctx, meta = vector_retrieve(state["question"])
    return {**state, "vector_context": ctx, "vector_meta": meta}


def generate(state: AgentState) -> AgentState:
    route = state.get("route", "hybrid")
    sections: list[str] = []
    if route in ("graph", "hybrid"):
        sections.append("=== GRAPH CONTEXT ===\n" + (state.get("graph_context") or ""))
    if route in ("vector", "hybrid"):
        sections.append("=== VECTOR CONTEXT ===\n" + (state.get("vector_context") or ""))
    context = "\n\n".join(sections)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Question: {state['question']}\n\nCONTEXT:\n{context}"),
    ]
    if not settings.openai_api_key:
        answer = (
            f"(Demo mode — set OPENAI_API_KEY)\n\nRetrieved via **{route}**:\n\n{context[:3500]}"
        )
        return {**state, "answer": answer}
    response = _llm().invoke(messages)
    return {**state, "answer": response.content}


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("classify", classify_route)
    workflow.add_node("retrieve_graph", retrieve_graph)
    workflow.add_node("retrieve_vector", retrieve_vector)
    workflow.add_node("generate", generate)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "retrieve_graph")
    workflow.add_edge("retrieve_graph", "retrieve_vector")
    workflow.add_edge("retrieve_vector", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()


_agent = None


def run_query(question: str, mode: Literal["auto", "graph", "vector"] = "auto") -> dict:
    global _agent
    if _agent is None:
        _agent = build_graph()
    initial: AgentState = {
        "question": question,
        "mode": mode,
        "route": "",
        "graph_context": "",
        "vector_context": "",
        "graph_records": [],
        "vector_meta": [],
        "answer": "",
    }
    final = _agent.invoke(initial)
    return {
        "answer": final["answer"],
        "route": final.get("route", mode),
        "graph_context": final.get("graph_context", ""),
        "vector_context": final.get("vector_context", ""),
        "citations": {
            "graph_records": final.get("graph_records", []),
            "vector_sources": final.get("vector_meta", []),
        },
    }
