from app.rag.ingest import parse_log_lines
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.agent.graph import run_diagnostics_graph

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

    graph_result = run_diagnostics_graph(
        question=question,
        log_text=log_text,
        filename=log_file.filename,
        system_type=system_type,
    )

    rca_report = graph_result["rca_report"]

    return {
        "question": question,
        "filename": log_file.filename,
        "system_type": system_type,
        "log_size_chars": len(log_text),
        
        "workflow_trace": graph_result["workflow_trace"],

        
        "incident_summary": rca_report["incident_summary"],
        "probable_root_cause": rca_report["probable_root_cause"],
        "detected_patterns": rca_report["detected_patterns"],
        "evidence_lines": rca_report["evidence_lines"],
        "timeline": rca_report["timeline"],
        "suggested_fix": rca_report["suggested_fix"],
        "prevention_steps": rca_report["prevention_steps"],
        "confidence_score": rca_report["confidence_score"],
        "debug": {
            "total_lines": len(graph_result["parsed_lines"]),
            "error_or_warning_count": len(graph_result["error_lines"]),
            "chunk_count": len(graph_result["chunks"]),
            "sample_error_lines": graph_result["error_lines"][:3],
            "sample_chunks": graph_result["chunks"][:2],
            "relevant_chunks": graph_result["relevant_chunks"],
        },
    }