"""
Task Runner Page
Submit goal → Track progress → View result
"""

import streamlit as st
import httpx
import time

BASE_URL = "http://localhost:8000"

# ─── Dark Theme CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d0d0f;
    color: #e8e8e8;
}
.stApp { background-color: #0d0d0f; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; background-color: transparent !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Sidebar Proper Styling ── */
section[data-testid="stSidebar"] {
    background-color: #111114 !important;
    border-right: 1px solid #222228;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important; 
}
section[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif !important;
}

/* 🔴 HIDE SIDEBAR ARROWS COMPLETELY 🔴 */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Sidebar Headings and Links */
[data-testid="stSidebar"] a p {
    color: #e8e8e8 !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] b,
[data-testid="stSidebar"] strong {
    color: #00e5a0 !important;
    opacity: 1 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #00e5a0 !important;
}
[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] span,
[data-testid="stSidebar"] .stCaption p {
    color: #ffffff !important; 
    opacity: 1 !important; 
    font-size: 0.85rem !important;
}

/* Inputs */
.stTextArea textarea,
.stSelectbox > div > div {
    background-color: #111114 !important;
    border: 1px solid #222228 !important;
    color: #e8e8e8 !important;
    border-radius: 10px !important;
}
.stTextArea textarea:focus {
    border-color: #00e5a050 !important;
    box-shadow: 0 0 0 2px #00e5a015 !important;
}

/* Labels */
.stTextArea label, .stSelectbox label {
    color: #888896 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
}

/* Button */
.stButton > button {
    background: #00e5a0 !important;
    color: #0d0d0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #00c987 !important;
    transform: translateY(-1px) !important;
}

/* Progress bar */
.stProgress > div > div {
    background: #00e5a0 !important;
    border-radius: 100px !important;
}
.stProgress {
    background: #1a1a22 !important;
    border-radius: 100px !important;
}

/* Alerts */
.stSuccess, .stInfo, .stError, .stWarning {
    border-radius: 10px !important;
    border: none !important;
}
.stSuccess { background: #0d2d22 !important; color: #00e5a0 !important; }
.stInfo    { background: #0d1a2d !important; color: #4db8ff !important; }
.stError   { background: #2d0d0d !important; color: #ff6b6b !important; }

/* Output box */
.output-box {
    background: #111114;
    border: 1px solid #1e1e26;
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-top: 1rem;
    line-height: 1.8;
    color: #c8c8d0;
    font-size: 0.9rem;
}

/* Page title */
.page-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #f0f0f0;
    margin-bottom: 0.3rem;
}
.page-sub {
    font-size: 0.82rem;
    color: #444450;
    margin-bottom: 2rem;
    font-family: 'Inter', sans-serif;
}

/* Section label */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #444450;
    margin: 1.5rem 0 0.6rem 0;
}

/* Divider */
hr { border-color: #1a1a22 !important; margin: 1.5rem 0 !important; }

/* ── Logo area ── */
.logo-area {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #00e5a0 !important;
    letter-spacing: 0.05em;
    margin-top: 0;
    padding: 0 0 1rem 0; 
    border-bottom: 1px solid #222228;
    margin-bottom: 1.5rem;
}

.logo-sub {
    font-size: 0.7rem;
    font-weight: 400;
    color: #e8e8e8 !important; 
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.2rem;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-area">
        ◈ AutoAgent
        <div class="logo-sub">Multi-Agent AI System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**PAGES**")
    st.page_link("streamlit_app.py",                    label="🏠  Dashboard")
    st.page_link("pages/1_task_runner.py",              label="⚡  Task Runner")
    st.page_link("pages/2_document_manager.py",         label="📄  Document Manager")
    st.page_link("pages/3_memory_explorer.py",          label="🧠  Memory Explorer")
    st.page_link("pages/4_session_history.py",          label="🕓  Session History")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("v1.0 · Solo Developer Edition · 2026")

# ─── Page Header ─────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">⚡ Task Runner</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Submit a goal — agents will research, write, and return a structured output.</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
if "task_id" not in st.session_state:
    st.session_state.task_id = None

# ─── Input Section ───────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Goal</div>', unsafe_allow_html=True)
# Fix: Added "Enter Goal" instead of ""
goal = st.text_area("Enter Goal", placeholder="e.g. Research the top 5 AI tools in 2026 and write a comparison report", height=120, label_visibility="collapsed")

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="section-label">LLM Provider</div>', unsafe_allow_html=True)
    # Fix: Added "LLM Provider" instead of ""
    llm_choice = st.selectbox("LLM Provider", ["groq", "gemini"], index=0, label_visibility="collapsed")
with col2:
    st.markdown('<div class="section-label">Output Format</div>', unsafe_allow_html=True)
    # Fix: Added "Output Format" instead of ""
    output_format = st.selectbox("Output Format", ["report", "summary", "bullets", "comparison"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("▶  RUN TASK"):
    if not goal.strip():
        st.warning("Please enter a goal first.")
    else:
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{BASE_URL}/api/v1/task/create",
                    json={
                        "goal": goal,
                        "config": {
                            "llm_provider": llm_choice,
                            "output_format": output_format,
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()
                st.session_state.task_id = data.get("task_id")
                st.success(f"Task started — ID: {st.session_state.task_id}")
        except Exception as e:
            st.error(f"Error starting task: {e}")

# ─── Progress Tracking ────────────────────────────────────────────────────────
if st.session_state.task_id:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Progress</div>', unsafe_allow_html=True)

    progress_placeholder = st.empty()
    status_placeholder   = st.empty()

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{BASE_URL}/api/v1/task/{st.session_state.task_id}/status"
            )
            response.raise_for_status()
            status_data = response.json()

        progress     = float(status_data.get("progress", 0.0))
        agent        = status_data.get("current_agent", "—")
        status       = status_data.get("status", "unknown")
        logs         = status_data.get("logs", [])

        progress_placeholder.progress(min(max(progress, 0.0), 1.0))
        status_placeholder.info(f"**Status:** {status.upper()}  ·  **Active Agent:** {agent}")

        if logs:
            st.caption("  ›  ".join(logs[-3:]))

        if status in {"created", "running", "started"}:
            time.sleep(2)
            st.rerun()

        elif status == "failed":
            st.error("Task failed. Check backend logs.")

        else:
            st.success("✓  Task completed successfully.")

            with httpx.Client(timeout=60.0) as client:
                result_resp = client.get(
                    f"{BASE_URL}/api/v1/task/{st.session_state.task_id}/result"
                )
                result_resp.raise_for_status()
                result_data = result_resp.json()

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Final Output</div>', unsafe_allow_html=True)

            output_text = result_data.get("output") or "_No output generated._"
            st.markdown(f'<div class="output-box">{output_text}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error fetching status: {e}")