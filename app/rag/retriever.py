def retrieve_relevant_chunks(
    chunks: list[dict],
    question: str,
    top_k: int = 3
) -> list[dict]:
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

        total_score = keyword_score + severity_score

        scored_chunks.append({
            **chunk,
            "retrieval_score": total_score,
        })

    scored_chunks.sort(
        key=lambda item: item["retrieval_score"],
        reverse=True
    )

    return scored_chunks[:top_k]