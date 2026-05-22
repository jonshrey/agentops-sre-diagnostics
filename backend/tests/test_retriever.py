from app.rag.ingest import parse_log_lines, build_log_chunks
from app.rag.retriever import retrieve_relevant_chunks


SAMPLE_LOG = """2026-05-22 01:59:50 INFO  payment-service Starting request processing
2026-05-22 01:59:58 WARN  payment-service Database connection pool usage at 95%
2026-05-22 02:00:01 ERROR payment-service DBConnectionPoolExhausted: No available connections in pool
2026-05-22 02:00:03 ERROR payment-service RequestTimeoutException: request timed out
2026-05-22 02:00:05 ERROR payment-service HTTP 500 returned
"""


def test_retrieve_relevant_chunks_scores_error_chunks():
    parsed = parse_log_lines(SAMPLE_LOG)
    chunks = build_log_chunks(parsed, window_size=1)

    results = retrieve_relevant_chunks(
        chunks=chunks,
        question="Why did the service fail around 2 AM?",
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["retrieval_score"] > 0
    assert "score_breakdown" in results[0]
    assert results[0]["score_breakdown"]["time_score"] == 3