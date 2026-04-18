"""
Document Manager Page — Dark Theme
Upload + RAG Query
"""

import streamlit as st
import httpx

BASE_URL = "http://localhost:8000"

# ─── Dark Theme CSS ───────────────────────────────────────────────────────────
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

/* Inputs & Forms */
.stTextArea textarea,
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background-color: #111114 !important;
    border: 1px solid #222228 !important;
    color: #e8e8e8 !important;
    border-radius: 10px !important;
}

.stTextArea label, .stSelectbox label,
.stTextInput label, .stFileUploader label {
    color: #888896 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #111114 !important;
    border: 1px dashed #222228 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"] * { color: #666672 !important; }

/* Buttons */
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
.stButton > button:hover { background: #00c987 !important; transform: translateY(-1px) !important; }

/* Alerts */
.stSuccess { background: #0d2d22 !important; color: #00e5a0 !important; border-radius: 10px !important; border: none !important; }
.stInfo    { background: #0d1a2d !important; color: #4db8ff !important; border-radius: 10px !important; border: none !important; }
.stError   { background: #2d0d0d !important; color: #ff6b6b !important; border-radius: 10px !important; border: none !important; }

.stExpander { background: #111114 !important; border: 1px solid #1e1e26 !important; border-radius: 10px !important; }

/* Page Specific Typography */
.page-title { font-family: 'Space Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #f0f0f0; margin-bottom: 0.3rem; }
.page-sub   { font-size: 0.82rem; color: #444450; margin-bottom: 2rem; }
.section-label { font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; color: #444450; margin: 1.5rem 0 0.6rem 0; }
.output-box { background: #111114; border: 1px solid #1e1e26; border-radius: 14px; padding: 1.5rem 1.8rem; margin-top: 1rem; line-height: 1.8; color: #c8c8d0; font-size: 0.9rem; }
.source-chip { display: inline-block; background: #0d2d22; color: #00e5a0; font-family: 'Space Mono', monospace; font-size: 0.7rem; padding: 0.2rem 0.7rem; border-radius: 6px; border: 1px solid #00e5a025; margin: 0.2rem; }
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

# ─── Page Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">📄 Document Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Upload a PDF or TXT file, then ask questions using the RAG pipeline.</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ─── Upload Section ───────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Upload Document</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Document", type=["pdf", "txt"], label_visibility="collapsed")

if uploaded_file:
    if st.button("⬆  UPLOAD DOCUMENT"):
        try:
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            with httpx.Client(timeout=60.0) as client:
                response = client.post(f"{BASE_URL}/api/v1/document/upload", files=files)
                response.raise_for_status()
                result = response.json()
            st.success(f"✓  Uploaded — {result.get('chunks_stored', 0)} chunks stored in ChromaDB")
        except Exception as e:
            st.error(f"Upload failed: {e}")

# ─── RAG Query Section ────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Ask Questions (RAG)</div>', unsafe_allow_html=True)

question = st.text_input("Enter Question", placeholder="e.g. What is the tech stack mentioned in this document?", label_visibility="collapsed")

if st.button("🔍  ASK"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{BASE_URL}/api/v1/document/query",
                    json={"query": question}
                )
                response.raise_for_status()
                data = response.json()

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Answer</div>', unsafe_allow_html=True)

            answer = data.get("answer", "No answer returned.")
            st.markdown(f'<div class="output-box">{answer}</div>', unsafe_allow_html=True)

            sources = data.get("sources", [])
            if sources:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-label">Sources</div>', unsafe_allow_html=True)
                chips = "".join([f'<span class="source-chip">{s}</span>' for s in sources])
                st.markdown(f'<div style="margin-top:0.5rem">{chips}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"RAG query failed: {e}")