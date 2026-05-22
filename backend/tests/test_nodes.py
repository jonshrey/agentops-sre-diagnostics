from app.rag.ingest import parse_log_lines, build_log_chunks
from app.rag.retriever import retrieve_relevant_chunks
from app.agent.nodes import analyze_error_pattern, generate_rca_report


SAMPLE_LOG = """2026-05-22 01:59:50 INFO  payment-service Starting request processing
2026-05-22 01:59:58 WARN  payment-service Database connection pool usage at 95%
2026-05-22 02:00:01 ERROR payment-service DBConnectionPoolExhausted: No available connections in pool
2026-05-22 02:00:03 ERROR payment-service RequestTimeoutException: request timed out
2026-05-22 02:00:05 ERROR payment-service HTTP 500 returned
"""


def test_analyze_error_pattern_detects_database_pool_exhaustion():
    parsed = parse_log_lines(SAMPLE_LOG)
    chunks = build_log_chunks(parsed, window_size=1)
    relevant_chunks = retrieve_relevant_chunks(
        chunks=chunks,
        question="Why did the service fail around 2 AM?",
    )

    analysis = analyze_error_pattern(relevant_chunks)

    assert "database_connection_pool_exhaustion" in analysis["detected_patterns"]
    assert "timeout" in analysis["detected_patterns"]
    assert analysis["confidence_score"] == 0.9


def test_generate_rca_report_contains_required_sections():
    parsed = parse_log_lines(SAMPLE_LOG)
    chunks = build_log_chunks(parsed, window_size=1)
    relevant_chunks = retrieve_relevant_chunks(
        chunks=chunks,
        question="Why did the service fail around 2 AM?",
    )
    analysis = analyze_error_pattern(relevant_chunks)

    report = generate_rca_report(
        analysis=analysis,
        relevant_chunks=relevant_chunks,
        docs_context=[],
    )

    assert "incident_summary" in report
    assert "probable_root_cause" in report
    assert "timeline" in report
    assert "evidence_lines" in report
    assert "suggested_fix" in report
    assert report["confidence_score"] == 0.9