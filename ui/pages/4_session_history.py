"""
Session History Page — Dark Theme
View past sessions, reload results, and delete history
"""

import streamlit as st
import httpx
import time

BASE_URL = "http://localhost:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0d0d0f; color: #e8e8e8; }
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
[data-testid="stSidebar"] a p { color: #e8e8e8 !important; opacity: 1 !important; }
[data-testid="stSidebar"] b, [data-testid="stSidebar"] strong { color: #00e5a0 !important; opacity: 1 !important; }
[data-testid="stSidebar"] hr { border-color: #00e5a0 !important; }
[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] span,
[data-testid="stSidebar"] .stCaption p { color: #ffffff !important; opacity: 1 !important; font-size: 0.85rem !important; }

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
.logo-sub { font-size: 0.7rem; font-weight: 400; color: #e8e8e8 !important; letter-spacing: 0.12em; text-transform: uppercase; margin-top: 0.2rem; opacity: 1 !important; }

/* ── Regular Buttons (Green) ── */
.stButton > button { 
    background: #00e5a0 !important; color: #0d0d0f !important; border: none !important; 
    border-radius: 8px !important; font-family: 'Space Mono', monospace !important; 
    font-size: 0.78rem !important; font-weight: 700 !important; letter-spacing: 0.08em !important; 
    padding: 0.4rem 1.2rem !important; transition: all 0.2s;
}
.stButton > button:hover { background: #00c987 !important; transform: translateY(-1px) !important; }

/* ── Danger/Delete Buttons (Red - Overrides standard button) ── */
.stButton > button[data-testid="baseButton-primary"] {
    background: #2d0d0d !important; color: #ff6b6b !important; 
    border: 1px solid #ff6b6b40 !important;
}
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: #4a1515 !important; border-color: #ff6b6b !important; transform: translateY(-1px) !important;
}

/* Page Specific CSS */
.stSuccess { background: #0d2d22 !important; color: #00e5a0 !important; border-radius: 10px !important; border: none !important; }
.stError   { background: #2d0d0d !important; color: #ff6b6b !important; border-radius: 10px !important; border: none !important; }
.page-title { font-family: 'Space Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #f0f0f0; margin-bottom: 0.3rem; }
.page-sub { font-size: 0.82rem; color: #444450; margin-bottom: 2rem; }
.section-label { font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; color: #444450; margin: 1.5rem 0 0.6rem 0; }
.session-card { background: #111114; border: 1px solid #1e1e26; border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; transition: all 0.2s; }
.session-card:hover { border-color: #00e5a025; background: #13131a; }
.session-goal { font-size: 0.9rem; color: #c0c0c8; margin: 0.4rem 0 0.8rem 0; line-height: 1.5; }
.session-meta { font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #333340; margin-bottom: 0.8rem; }
.status-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.68rem; font-family: 'Space Mono', monospace; font-weight: 700; }
.status-completed { background: #0d2d22; color: #00e5a0; }
.status-failed    { background: #2d0d0d; color: #ff6b6b; }
.status-running   { background: #0d1a2d; color: #4db8ff; }
.status-pending   { background: #1a1a22; color: #666672; }
.output-box { background: #0d0d0f; border: 1px solid #1a1a22; border-radius: 10px; padding: 1.2rem 1.5rem; margin-top: 0.8rem; line-height: 1.8; color: #888896; font-size: 0.85rem; }
hr { border-color: #1a1a22 !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
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
    
    st.markdown("<hr style='border-color:#1a1a22; margin: 1.5rem 0'>", unsafe_allow_html=True)
    st.caption("v1.0 · Solo Developer Edition · 2026")

# ─── Main Page Content ────────────────────────────────────────────────────────
st.markdown('<div class="page-title">🕓 Session History</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Browse all past task runs, reload results, or manage history.</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

try:
    with httpx.Client(timeout=30.0) as client:
        response = client.get(f"{BASE_URL}/api/v1/task/sessions")
        response.raise_for_status()
        sessions = response.json()

    if not sessions:
        st.info("No sessions found. Run a task first from the Task Runner.")
    else:
        # Header with Delete All button
        col_header, col_delete_all = st.columns([3, 1])
        with col_header:
            st.markdown('<div class="section-label" style="margin-top:0;">Past Sessions</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='color:#444450;font-size:0.8rem;margin-bottom:1rem'>{len(sessions)} session(s) found</p>", unsafe_allow_html=True)
        with col_delete_all:
            if st.button("🗑️ DELETE ALL", type="primary", use_container_width=True):
                try:
                    with httpx.Client(timeout=30.0) as client:
                        res = client.delete(f"{BASE_URL}/api/v1/task/sessions")
                        res.raise_for_status()
                    st.success("All sessions deleted successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete all: {e}")

        for session in sessions:
            session_id = session.get("session_id") or session.get("id", "unknown")
            status     = session.get("status", "unknown")
            goal       = session.get("goal", "No goal recorded")
            created_at = session.get("created_at", "")

            # Status tag color
            status_class = {
                "completed": "status-completed",
                "failed":    "status-failed",
                "running":   "status-running",
            }.get(status, "status-pending")

            st.markdown(
                f'<div class="session-card">'
                f'<span class="status-tag {status_class}">{status.upper()}</span>'
                f'<div class="session-goal">{goal}</div>'
                f'<div class="session-meta">ID: {session_id[:24]}...  ·  {created_at[:19] if created_at else "—"}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Fix: Adjusted column width ratio so text doesn't wrap
            col_btn1, col_btn2, _ = st.columns([2.5, 2.0, 5.5])
            
            with col_btn1:
                # Fix: Added use_container_width=True to fill perfectly
                if st.button("Load Result", key=f"load_{session_id}", use_container_width=True):
                    try:
                        with httpx.Client(timeout=60.0) as client:
                            res = client.get(f"{BASE_URL}/api/v1/task/{session_id}/result")
                            res.raise_for_status()
                            data = res.json()

                        output = data.get("output", "No output available.")
                        st.markdown(f'<div class="output-box">{output}</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Failed to load session: {e}")
            
            with col_btn2:
                # Type primary makes it red based on our Custom CSS
                if st.button("🗑️ Delete", type="primary", key=f"del_{session_id}", use_container_width=True):
                    try:
                        with httpx.Client(timeout=30.0) as client:
                            res = client.delete(f"{BASE_URL}/api/v1/task/{session_id}")
                            res.raise_for_status()
                        st.rerun()  # Refresh the page to show updated list
                    except Exception as e:
                        st.error(f"Failed to delete session: {e}")

except Exception as e:
    st.error(f"Could not fetch sessions: {e}")