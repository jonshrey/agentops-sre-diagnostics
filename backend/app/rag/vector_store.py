import uuid

import chromadb


def retrieve_semantic_chunks(
    chunks: list[dict],
    question: str,
    top_k: int = 3,
) -> list[dict]:
    if not chunks:
        return []

    client = chromadb.Client()

    collection_name = f"agentops_logs_{uuid.uuid4().hex}"

    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Temporary per-request log chunks"},
    )

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["chunk_text"])
        metadatas.append({
            "chunk_id": chunk["chunk_id"],
            "center_line": chunk["center_line"],
            "line_start": chunk["line_start"],
            "line_end": chunk["line_end"],
            "timestamp_start": chunk.get("timestamp_start") or "",
            "timestamp_end": chunk.get("timestamp_end") or "",
            "log_level": chunk.get("log_level") or "",
            "service": chunk.get("service") or "",
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, len(chunks)),
    )

    semantic_results = []

    result_ids = results.get("ids", [[]])[0]
    result_distances = results.get("distances", [[]])[0]

    for result_id, distance in zip(result_ids, result_distances):
        semantic_results.append({
            "chunk_id": result_id,
            "semantic_distance": distance,
            "semantic_score": max(0, 3 - distance),
        })

    return semantic_results