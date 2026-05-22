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