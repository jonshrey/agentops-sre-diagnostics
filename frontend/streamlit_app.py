import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000/diagnose"


st.set_page_config(
    page_title="AgentOps SRE Diagnostics",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ AgentOps: Autonomous SRE Diagnostics Agent")

st.write(
    "Upload a log file, ask an incident question, and generate an evidence-grounded RCA report."
)

uploaded_file = st.file_uploader(
    "Upload log file",
    type=["log", "txt"],
)

question = st.text_input(
    "Incident question",
    value="Why did the service fail around 2 AM?",
)

system_type = st.text_input(
    "System / service type",
    value="payment-service",
)

analyze_button = st.button("Analyze Incident")


if analyze_button:
    if uploaded_file is None:
        st.error("Please upload a log file first.")
    elif not question.strip():
        st.error("Please enter an incident question.")
    else:
        with st.spinner("Analyzing logs and generating RCA..."):
            files = {
                "log_file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/plain",
                )
            }

            data = {
                "question": question,
                "system_type": system_type,
            }

            try:
                response = requests.post(
                    API_URL,
                    files=files,
                    data=data,
                    timeout=60,
                )

                if response.status_code != 200:
                    st.error(f"API returned status code {response.status_code}")
                    st.code(response.text)
                else:
                    result = response.json()

                    st.success("Analysis complete")

                    st.subheader("Workflow Trace")
                    st.write(" → ".join(result.get("workflow_trace", [])))

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Confidence",
                            result.get("confidence_score", 0),
                        )

                    with col2:
                        st.metric(
                            "Docs Search",
                            "Yes" if result.get("needs_docs_search") else "No",
                        )

                    with col3:
                        st.metric(
                            "LLM Enabled",
                            "Yes" if result.get("llm_enabled") else "No",
                        )

                    st.subheader("Incident Summary")
                    st.write(result.get("incident_summary", ""))

                    st.subheader("Probable Root Cause")
                    st.write(result.get("probable_root_cause", ""))

                    st.subheader("Detected Patterns")
                    st.write(result.get("detected_patterns", []))

                    st.subheader("Timeline")
                    timeline = result.get("timeline", [])

                    if timeline:
                        for event in timeline:
                            st.markdown(
                                f"- **{event.get('timestamp')}** "
                                f"`{event.get('log_level')}` "
                                f"**{event.get('service')}** — "
                                f"{event.get('event')}"
                            )
                    else:
                        st.info("No timeline events found.")

                    st.subheader("Suggested Fixes")
                    for fix in result.get("suggested_fix", []):
                        st.markdown(f"- {fix}")

                    st.subheader("Prevention Steps")
                    for step in result.get("prevention_steps", []):
                        st.markdown(f"- {step}")

                    if result.get("external_context_used"):
                        st.subheader("Docs / Runbook Findings")
                        for doc in result.get("docs_findings", []):
                            st.markdown(f"### {doc.get('title')}")
                            st.write(doc.get("summary"))

                    if result.get("llm_rca_report"):
                        st.subheader("LLM-Generated RCA Report")
                        st.markdown(result.get("llm_rca_report"))

                    st.subheader("Evidence Lines")
                    evidence_lines = result.get("evidence_lines", [])

                    for evidence in evidence_lines:
                        with st.expander(
                            f"{evidence.get('chunk_id')} | Lines {evidence.get('line_range')} | Score {evidence.get('retrieval_score')}"
                        ):
                            st.write(
                                f"Timestamp range: {evidence.get('timestamp_range')}"
                            )
                            st.code(evidence.get("evidence", ""), language="text")

                    with st.expander("Debug Info"):
                        st.json(result.get("debug", {}))

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to FastAPI backend. Make sure it is running on http://127.0.0.1:8000"
                )
            except Exception as error:
                st.error(f"Unexpected error: {error}")