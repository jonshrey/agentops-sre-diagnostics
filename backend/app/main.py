from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.agent.graph import run_diagnostics_graph
from app.schemas.diagnose import DiagnoseResponse, DiagnoseTextRequest
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Autonomous SRE Diagnostics Agent",
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_allow_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_diagnose_response(
    question: str,
    log_text: str,
    filename: str | None = None,
    system_type: str | None = None,
) -> dict:
    graph_result = run_diagnostics_graph(
        question=question,
        log_text=log_text,
        filename=filename or "pasted-log-text",
        system_type=system_type,
    )

    rca_report = graph_result["rca_report"]

    return {
        "question": question,
        "filename": filename,
        "system_type": system_type,
        "log_size_chars": len(log_text),

        "workflow_trace": graph_result["workflow_trace"],
        "needs_docs_search": graph_result.get("needs_docs_search", False),
        "docs_context": graph_result.get("docs_context", []),

        "external_context_used": rca_report["external_context_used"],
        "docs_findings": rca_report["docs_findings"],

        "llm_enabled": rca_report["llm_enabled"],
        "llm_rca_report": rca_report["llm_rca_report"],

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


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_logs(
    question: str = Form(...),
    log_file: UploadFile = File(...),
    system_type: str | None = Form(default=None),
):
    content = await log_file.read()
    log_text = content.decode("utf-8", errors="ignore")

    return build_diagnose_response(
        question=question,
        log_text=log_text,
        filename=log_file.filename,
        system_type=system_type,
    )


@app.post("/diagnose-text", response_model=DiagnoseResponse)
def diagnose_text(payload: DiagnoseTextRequest):
    return build_diagnose_response(
        question=payload.question,
        log_text=payload.log_text,
        filename="pasted-log-text",
        system_type=payload.system_type,
    )