from typing import TypedDict, Optional


class DiagnosticsState(TypedDict, total=False):
    question: str
    log_text: str
    filename: str
    system_type: Optional[str]

    parsed_lines: list[dict]
    error_lines: list[dict]
    chunks: list[dict]
    relevant_chunks: list[dict]

    analysis: dict
    rca_report: dict

    needs_docs_search: bool
    docs_context: list[dict]

    workflow_trace: list[str]