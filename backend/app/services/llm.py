import google.generativeai as genai

from app.core.config import settings


def is_llm_enabled() -> bool:
    return settings.llm_enabled


def generate_llm_rca(rca_report: dict) -> str:
    if not is_llm_enabled():
        return ""

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        prompt = f"""
You are an expert Site Reliability Engineer.

Generate a concise, professional Root Cause Analysis report using ONLY the structured evidence below.
Do not invent facts. If evidence is insufficient, say so clearly.

Incident Summary:
{rca_report.get("incident_summary")}

Probable Root Cause:
{rca_report.get("probable_root_cause")}

Detected Patterns:
{rca_report.get("detected_patterns")}

Timeline:
{rca_report.get("timeline")}

Evidence Lines:
{rca_report.get("evidence_lines")}

Docs Findings:
{rca_report.get("docs_findings")}

Suggested Fixes:
{rca_report.get("suggested_fix")}

Prevention Steps:
{rca_report.get("prevention_steps")}

Return the answer in this format:

## Incident Summary
...

## Root Cause
...

## Evidence
- ...

## Timeline
- ...

## Suggested Fix
- ...

## Prevention
- ...

## Confidence
...
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as error:
        return f"LLM generation failed: {str(error)}"