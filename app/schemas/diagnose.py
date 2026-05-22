from typing import Any
from pydantic import BaseModel


class EvidenceLine(BaseModel):
    chunk_id: str
    line_range: str
    timestamp_range: str
    log_level: str
    service: str | None = None
    evidence: str
    retrieval_score: int | float


class TimelineEvent(BaseModel):
    timestamp: str
    log_level: str
    service: str | None = None
    event: str


class DocsFinding(BaseModel):
    source: str | None = None
    title: str | None = None
    summary: str | None = None


class DebugInfo(BaseModel):
    total_lines: int
    error_or_warning_count: int
    chunk_count: int
    sample_error_lines: list[dict[str, Any]]
    sample_chunks: list[dict[str, Any]]
    relevant_chunks: list[dict[str, Any]]


class DiagnoseResponse(BaseModel):
    question: str
    filename: str | None = None
    system_type: str | None = None
    log_size_chars: int

    workflow_trace: list[str]
    needs_docs_search: bool
    docs_context: list[dict[str, Any]]

    external_context_used: bool
    docs_findings: list[DocsFinding]

    llm_enabled: bool
    llm_rca_report: str

    incident_summary: str
    probable_root_cause: str
    detected_patterns: list[str]
    evidence_lines: list[EvidenceLine]
    timeline: list[TimelineEvent]
    suggested_fix: list[str]
    prevention_steps: list[str]
    confidence_score: float

    debug: DebugInfo