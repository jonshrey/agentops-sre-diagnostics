from app.rag.ingest import parse_log_lines
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.rag.ingest import parse_log_lines, build_log_chunks
from app.rag.retriever import retrieve_relevant_chunks
from app.agent.nodes import analyze_error_pattern
from app.agent.nodes import analyze_error_pattern, generate_rca_report

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
    rca_report = generate_rca_report(analysis, relevant_chunks)
    error_lines = [
    line for line in parsed_lines
    if line["log_level"] in ["ERROR", "WARN"]
]

    return {
    "question": question,
    "filename": log_file.filename,
    "system_type": system_type,
    "log_size_chars": len(log_text),

    "incident_summary": rca_report["incident_summary"],
    "probable_root_cause": rca_report["probable_root_cause"],
    "detected_patterns": rca_report["detected_patterns"],
    "evidence_lines": rca_report["evidence_lines"],
    "timeline": rca_report["timeline"],
    "suggested_fix": rca_report["suggested_fix"],
    "prevention_steps": rca_report["prevention_steps"],
    "confidence_score": rca_report["confidence_score"],

    "debug": {
        "total_lines": len(parsed_lines),
        "error_or_warning_count": len(error_lines),
        "chunk_count": len(chunks),
        "sample_error_lines": error_lines[:3],
        "sample_chunks": chunks[:2],
        "relevant_chunks": relevant_chunks,
    }
}