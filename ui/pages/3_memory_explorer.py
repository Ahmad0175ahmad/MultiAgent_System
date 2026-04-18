"""
Memory Explorer Page — Dark Theme
Search ChromaDB memory
"""

import streamlit as st
import httpx

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
.stTextInput > div > div > input, .stSelectbox > div > div { 
    background-color: #111114 !important; 
    border: 1px solid #222228 !important; 
    color: #e8e8e8 !important; 
    border-radius: 10px !important; 
}
.stTextInput label, .stSelectbox label { 
    color: #888896 !important; 
    font-size: 0.82rem !important; 
}

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
}
.stButton > button:hover { background: #00c987 !important; transform: translateY(-1px) !important; }

/* Alerts */
.stSuccess { background: #0d2d22 !important; color: #00e5a0 !important; border-radius: 10px !important; border: none !important; }
.stInfo    { background: #0d1a2d !important; color: #4db8ff !important; border-radius: 10px !important; border: none !important; }
.stError   { background: #2d0d0d !important; color: #ff6b6b !important; border-radius: 10px !important; border: none !important; }
.stWarning { background: #2d1f0d !important; color: #ffaa00 !important; border-radius: 10px !important; border: none !important; }

.stExpander { background: #111114 !important; border: 1px solid #1e1e26 !important; border-radius: 10px !important; }

/* Page Specific Typography */
.page-title { font-family: 'Space Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #f0f0f0; margin-bottom: 0.3rem; }
.page-sub { font-size: 0.82rem; color: #444450; margin-bottom: 2rem; }
.section-label { font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; color: #444450; margin: 1.5rem 0 0.6rem 0; }
.result-card { background: #111114; border: 1px solid #1e1e26; border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem; }
.score-badge { display: inline-block; background: #0d2d22; color: #00e5a0; font-family: 'Space Mono', monospace; font-size: 0.7rem; padding: 0.2rem 0.6rem; border-radius: 6px; border: 1px solid #00e5a025; margin-bottom: 0.6rem; }
.result-text { font-size: 0.85rem; color: #888896; line-height: 1.7; }
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
st.markdown('<div class="page-title">🧠 Memory Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Search directly across all ChromaDB collections — documents, research, task outputs.</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown('<div class="section-label">Search Query</div>', unsafe_allow_html=True)
    query = st.text_input("Search Query", placeholder="e.g. Python, tech stack, AI tools...", label_visibility="collapsed")
with col2:
    st.markdown('<div class="section-label">Collection</div>', unsafe_allow_html=True)
    collection = st.selectbox("Collection", options=["document_store","research_memory","task_outputs","agent_scratchpad","user_preferences"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔍  SEARCH MEMORY"):
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(f"{BASE_URL}/api/v1/memory/search", params={"q": query, "collection": collection})
                response.raise_for_status()
                results = response.json().get("results", [])

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

            if not results:
                st.info(f"No results found for '{query}' in '{collection}'")
            else:
                st.success(f"✓  {len(results)} result(s) found in {collection}")
                st.markdown("<br>", unsafe_allow_html=True)
                for item in results:
                    score   = round(item.get("score", 0), 3)
                    text    = item.get("text", "")
                    meta    = item.get("metadata", {})
                    preview = text[:300] + "..." if len(text) > 300 else text
                    st.markdown(f'<div class="result-card"><div class="score-badge">score: {score}</div><div class="result-text">{preview}</div></div>', unsafe_allow_html=True)
                    if meta:
                        with st.expander("Metadata"):
                            st.json(meta)
        except Exception as e:
            st.error(f"Search failed: {e}")