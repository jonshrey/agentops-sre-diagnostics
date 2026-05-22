from app.rag.ingest import parse_log_lines, build_log_chunks


SAMPLE_LOG = """2026-05-22 01:59:50 INFO  payment-service Starting request processing
2026-05-22 01:59:58 WARN  payment-service Database connection pool usage at 95%
2026-05-22 02:00:01 ERROR payment-service DBConnectionPoolExhausted: No available connections in pool
2026-05-22 02:00:03 ERROR payment-service RequestTimeoutException: request timed out
"""


def test_parse_log_lines_extracts_fields():
    parsed = parse_log_lines(SAMPLE_LOG)

    assert len(parsed) == 4
    assert parsed[0]["timestamp"] == "2026-05-22 01:59:50"
    assert parsed[0]["log_level"] == "INFO"
    assert parsed[0]["service"] == "payment-service"
    assert parsed[2]["log_level"] == "ERROR"
    assert "DBConnectionPoolExhausted" in parsed[2]["message"]


def test_build_log_chunks_creates_chunks_for_warn_and_error():
    parsed = parse_log_lines(SAMPLE_LOG)
    chunks = build_log_chunks(parsed, window_size=1)

    assert len(chunks) == 3
    assert chunks[0]["center_line"] == 2
    assert chunks[0]["line_start"] == 1
    assert chunks[0]["line_end"] == 3
    assert "Database connection pool usage" in chunks[0]["chunk_text"]