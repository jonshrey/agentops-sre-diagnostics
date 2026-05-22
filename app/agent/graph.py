from langgraph.graph import StateGraph, END

from app.agent.state import DiagnosticsState
from app.agent.nodes import (
    parse_and_chunk_logs_node,
    retrieve_logs_node,
    analyze_patterns_node,
    decide_docs_search_node,
    search_docs_node,
    generate_report_node,
)


def route_after_decision(state: DiagnosticsState) -> str:
    if state.get("needs_docs_search"):
        return "search_docs"

    return "generate_report"


def build_diagnostics_graph():
    graph = StateGraph(DiagnosticsState)

    graph.add_node("parse_and_chunk_logs", parse_and_chunk_logs_node)
    graph.add_node("retrieve_logs", retrieve_logs_node)
    graph.add_node("analyze_patterns", analyze_patterns_node)
    graph.add_node("decide_docs_search", decide_docs_search_node)
    graph.add_node("search_docs", search_docs_node)
    graph.add_node("generate_report", generate_report_node)

    graph.set_entry_point("parse_and_chunk_logs")

    graph.add_edge("parse_and_chunk_logs", "retrieve_logs")
    graph.add_edge("retrieve_logs", "analyze_patterns")
    graph.add_edge("analyze_patterns", "decide_docs_search")

    graph.add_conditional_edges(
        "decide_docs_search",
        route_after_decision,
        {
            "search_docs": "search_docs",
            "generate_report": "generate_report",
        },
    )

    graph.add_edge("search_docs", "generate_report")
    graph.add_edge("generate_report", END)

    return graph.compile()


diagnostics_graph = build_diagnostics_graph()


def run_diagnostics_graph(
    question: str,
    log_text: str,
    filename: str,
    system_type: str | None = None,
) -> dict:
    initial_state = {
        "question": question,
        "log_text": log_text,
        "filename": filename,
        "system_type": system_type,
        "workflow_trace": [],
        "docs_context": [],
        "needs_docs_search": False,
    }

    return diagnostics_graph.invoke(initial_state)