from datetime import datetime, timedelta
from app.rag.vector_store import retrieve_semantic_chunks
import re


def extract_base_date_from_chunks(chunks: list[dict]) -> datetime | None:
    for chunk in chunks:
        timestamp = chunk.get("timestamp_start")

        if not timestamp:
            continue

        parsed_timestamp = parse_timestamp(timestamp)

        if parsed_timestamp:
            return parsed_timestamp

    return None


def extract_time_from_question(
    question: str,
    base_date: datetime | None = None
) -> datetime | None:
    question_lower = question.lower()

    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", question_lower)

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = match.group(3)

    if meridiem == "pm" and hour != 12:
        hour += 12

    if meridiem == "am" and hour == 12:
        hour = 0

    if base_date is None:
        return None

    return base_date.replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )


def parse_timestamp(timestamp: str | None) -> datetime | None:
    if not timestamp:
        return None

    try:
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def calculate_time_score(
    chunk: dict,
    target_time: datetime | None,
    window_minutes: int = 10
) -> int:
    if target_time is None:
        return 0

    start = parse_timestamp(chunk.get("timestamp_start"))
    end = parse_timestamp(chunk.get("timestamp_end"))

    if start is None or end is None:
        return 0

    window_start = target_time - timedelta(minutes=window_minutes)
    window_end = target_time + timedelta(minutes=window_minutes)

    overlaps_window = start <= window_end and end >= window_start

    if overlaps_window:
        return 3

    return 0


def retrieve_relevant_chunks(
    chunks: list[dict],
    question: str,
    top_k: int = 3
) -> list[dict]:
    base_date = extract_base_date_from_chunks(chunks)
    target_time = extract_time_from_question(question, base_date)
    semantic_results = retrieve_semantic_chunks(
       chunks=chunks,
       question=question,
       top_k=top_k,
  )
    semantic_score_by_chunk_id = {
    item["chunk_id"]: item["semantic_score"]
    for item in semantic_results
}
    
    question_words = set(
        word.lower().strip(".,?!:;")
        for word in question.split()
        if len(word) > 2
    )

    scored_chunks = []

    for chunk in chunks:
        chunk_text = chunk["chunk_text"].lower()

        keyword_score = sum(
            1 for word in question_words
            if word in chunk_text
        )

        severity_score = 0
        if chunk["log_level"] == "ERROR":
            severity_score = 2
        elif chunk["log_level"] == "WARN":
            severity_score = 1
            
        semantic_score = semantic_score_by_chunk_id.get(chunk["chunk_id"], 0)    

        time_score = calculate_time_score(chunk, target_time)

        total_score = keyword_score + severity_score + time_score + semantic_score
        scored_chunks.append({
            **chunk,
            "retrieval_score": total_score,
            "score_breakdown": {
                "keyword_score": keyword_score,
                "severity_score": severity_score,
                "time_score": time_score,
                "semantic_score": semantic_score,
            }
        })

    scored_chunks.sort(
        key=lambda item: item["retrieval_score"],
        reverse=True
    )

    return scored_chunks[:top_k]