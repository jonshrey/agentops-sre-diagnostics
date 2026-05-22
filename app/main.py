from app.rag.ingest import parse_log_lines
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.rag.ingest import parse_log_lines, build_log_chunks
from app.rag.retriever import retrieve_relevant_chunks
from app.agent.nodes import analyze_error_pattern

app = FastAPI(
    title="AgentOps",
    description="Autonomous SRE Diagnostics Agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/diagnose")
async def diagnose_logs(
    question: str = Form(...),
    log_file: UploadFile = File(...),
    system_type: str | None = Form(default=None),
):
    content = await log_file.read()
    log_text = content.decode("utf-8", errors="ignore")
    parsed_lines = parse_log_lines(log_text)
    chunks = build_log_chunks(parsed_lines)
    relevant_chunks = retrieve_relevant_chunks(chunks, question)
    analysis = analyze_error_pattern(relevant_chunks)
    error_lines = [
    line for line in parsed_lines
    if line["log_level"] in ["ERROR", "WARN"]
]

    return {
        "question": question,
        "filename": log_file.filename,
        "system_type": system_type,
        "log_size_chars": len(log_text),
        "incident_summary": "Initial analysis completed using parsed log evidence.",
        "suggested_fix": "Review database connection pool sizing, timeout settings, and retry behavior.",        
        "evidence_lines": [],
        "suggested_fix": "Next step: implement log ingestion and retrieval.",
        "confidence_score": 0.0,
        "total_lines": len(parsed_lines),
        "error_or_warning_count": len(error_lines),
        "sample_error_lines": error_lines[:3],
        "chunk_count": len(chunks),
        "sample_chunks": chunks[:2],
        "relevant_chunks": relevant_chunks,
        "probable_root_cause": analysis["probable_root_cause"],
        "confidence_score": analysis["confidence_score"],
        "detected_patterns": analysis["detected_patterns"],
    }