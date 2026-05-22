from langgraph.graph import StateGraph, END

from app.agent.state import DiagnosticsState
from app.agent.nodes import (
    parse_and_chunk_logs_node,
    retrieve_logs_node,
    analyze_patterns_node,
    generate_report_node,
)


def build_diagnostics_graph():
    graph = StateGraph(DiagnosticsState)

    graph.add_node("parse_and_chunk_logs", parse_and_chunk_logs_node)
    graph.add_node("retrieve_logs", retrieve_logs_node)
    graph.add_node("analyze_patterns", analyze_patterns_node)
    graph.add_node("generate_report", generate_report_node)

    graph.set_entry_point("parse_and_chunk_logs")

    graph.add_edge("parse_and_chunk_logs", "retrieve_logs")
    graph.add_edge("retrieve_logs", "analyze_patterns")
    graph.add_edge("analyze_patterns", "generate_report")
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
    }

    return diagnostics_graph.invoke(initial_state)