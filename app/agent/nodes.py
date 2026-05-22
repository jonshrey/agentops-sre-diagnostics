def analyze_error_pattern(relevant_chunks: list[dict]) -> dict:
    combined_text = "\n".join(
        chunk["chunk_text"] for chunk in relevant_chunks
    ).lower()

    detected_patterns = []

    if "dbconnectionpoolexhausted" in combined_text or "connection pool" in combined_text:
        detected_patterns.append("database_connection_pool_exhaustion")

    if "timeout" in combined_text:
        detected_patterns.append("timeout")

    if "http 500" in combined_text or "internal server error" in combined_text:
        detected_patterns.append("http_500_errors")

    if "retry failed" in combined_text:
        detected_patterns.append("retry_failures")

    if "database_connection_pool_exhaustion" in detected_patterns:
        probable_root_cause = (
            "Database connection pool exhaustion caused requests to time out, "
            "which then resulted in HTTP 500 errors."
        )
        confidence_score = 0.9

    elif "timeout" in detected_patterns:
        probable_root_cause = (
            "The service appears to be failing due to repeated timeout errors."
        )
        confidence_score = 0.7

    elif "http_500_errors" in detected_patterns:
        probable_root_cause = (
            "The service returned HTTP 500 errors, but the underlying cause is unclear from the current logs."
        )
        confidence_score = 0.5

    else:
        probable_root_cause = (
            "The root cause could not be confidently determined from the retrieved logs."
        )
        confidence_score = 0.3

    return {
        "detected_patterns": detected_patterns,
        "probable_root_cause": probable_root_cause,
        "confidence_score": confidence_score,
    }

def extract_timeline_events(relevant_chunks: list[dict]) -> list[dict]:
    seen_lines = set()
    timeline = []

    for chunk in relevant_chunks:
        for raw_line in chunk["chunk_text"].splitlines():
            if raw_line in seen_lines:
                continue

            seen_lines.add(raw_line)

            parts = raw_line.split(maxsplit=4)

            if len(parts) < 5:
                continue

            timestamp = f"{parts[0]} {parts[1]}"
            log_level = parts[2]
            service = parts[3]
            message = parts[4]

            if log_level not in ["WARN", "ERROR"]:
                continue

            timeline.append({
                "timestamp": timestamp,
                "log_level": log_level,
                "service": service,
                "event": message,
            })

    timeline.sort(key=lambda item: item["timestamp"])

    return timeline    
    
def generate_rca_report(
    analysis: dict,
    relevant_chunks: list[dict]
) -> dict:
    evidence_lines = []

    for chunk in relevant_chunks:
        evidence_lines.append({
            "chunk_id": chunk["chunk_id"],
            "line_range": f"{chunk['line_start']}-{chunk['line_end']}",
            "timestamp_range": f"{chunk['timestamp_start']} to {chunk['timestamp_end']}",
            "log_level": chunk["log_level"],
            "service": chunk["service"],
            "evidence": chunk["chunk_text"],
            "retrieval_score": chunk.get("retrieval_score", 0),
        })

    timeline = extract_timeline_events(relevant_chunks)
    

    return {
        "incident_summary": "The service failure appears to be caused by errors found in the retrieved log window.",
        "probable_root_cause": analysis["probable_root_cause"],
        "detected_patterns": analysis["detected_patterns"],
        "evidence_lines": evidence_lines,
        "timeline": timeline,
        "suggested_fix": [
            "Increase or tune the database connection pool size.",
            "Check for connection leaks or long-running database queries.",
            "Review timeout configuration between the service and database.",
            "Add alerts for high connection pool usage before exhaustion.",
            "Review retry behavior to avoid repeated pressure during failure."
        ],
        "prevention_steps": [
            "Monitor connection pool utilization.",
            "Set alerts for pool usage above 80%.",
            "Add circuit breakers or backoff for retrying failed requests.",
            "Track request latency and database timeout rates.",
            "Load test the service with realistic traffic spikes."
        ],
        "confidence_score": analysis["confidence_score"],
    }    

from app.rag.ingest import parse_log_lines, build_log_chunks
from app.rag.retriever import retrieve_relevant_chunks


def parse_and_chunk_logs_node(state: dict) -> dict:
    parsed_lines = parse_log_lines(state["log_text"])

    error_lines = [
        line for line in parsed_lines
        if line["log_level"] in ["ERROR", "WARN"]
    ]

    chunks = build_log_chunks(parsed_lines)

    return {
        **state,
        "parsed_lines": parsed_lines,
        "error_lines": error_lines,
        "chunks": chunks,
    }


def retrieve_logs_node(state: dict) -> dict:
    relevant_chunks = retrieve_relevant_chunks(
        chunks=state["chunks"],
        question=state["question"],
    )

    return {
        **state,
        "relevant_chunks": relevant_chunks,
    }


def analyze_patterns_node(state: dict) -> dict:
    analysis = analyze_error_pattern(state["relevant_chunks"])

    return {
        **state,
        "analysis": analysis,
    }


def generate_report_node(state: dict) -> dict:
    rca_report = generate_rca_report(
        analysis=state["analysis"],
        relevant_chunks=state["relevant_chunks"],
    )

    return {
        **state,
        "rca_report": rca_report,
    }    