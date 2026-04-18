"""
Main Streamlit App Entry Point
AutoAgent — Multi-Agent AI System
"""

import streamlit as st

st.set_page_config(
    page_title="AutoAgent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');

/* ── Global ── */
.stApp {
    background-color: #0d0d0f;
    font-family: 'Inter', sans-serif;
    color: #e8e8e8;
}

/* ── Hide default streamlit elements ── */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── Sidebar Proper Styling ── */
[data-testid="stSidebar"] {
    background-color: #111114 !important;
    border-right: 1px solid #222228;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important; 
}

/* 🔴 HIDE SIDEBAR ARROWS COMPLETELY 🔴 */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    display: none !important;
}
            
/* 🔴 2. FIX FOR LINKS AND CAPTIONS (Forced Bright White) 🔴 */
[data-testid="stSidebar"] a p {
    color: #e8e8e8 !important;
    opacity: 1 !important;
}

/* System text (FastAPI, Version etc.) ko bright white kiya */
[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] span,
[data-testid="stSidebar"] .stCaption p {
    color: #ffffff !important; 
    opacity: 1 !important; 
    font-size: 0.85rem !important;
}

/* Sidebar Headings (PAGES, SYSTEM) in Neon Green */
[data-testid="stSidebar"] b,
[data-testid="stSidebar"] strong {
    color: #00e5a0 !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] hr {
    border-color: #00e5a0 !important;
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

/* ── Hero Section ── */
.hero-wrapper {
    padding: 3rem 0 2rem 0;
}
.hero-badge {
    display: inline-block;
    background: #0d2d22;
    color: #00e5a0;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    padding: 0.35rem 0.9rem;
    border-radius: 100px;
    border: 1px solid #00e5a030;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 3.2rem;
    font-weight: 700;
    line-height: 1.1;
    color: #f0f0f0;
    margin-bottom: 0.5rem;
}
.hero-title span {
    color: #00e5a0;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #666672;
    font-weight: 300;
    max-width: 900px;
    line-height: 1.7;
    margin-bottom: 2.5rem;
}

/* ── Status bar ── */
.status-bar {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 3rem;
    flex-wrap: wrap;
}
.status-pill {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #111114;
    border: 1px solid #222228;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.82rem;
    color: #888896;
}
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00e5a0;
    box-shadow: 0 0 8px #00e5a0;
    animation: pulse 2s infinite;
}
.status-dot.warning {
    background: #ffaa00;
    box-shadow: 0 0 8px #ffaa00;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Feature Cards ── */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 3rem;
}
.feature-card {
    background: #111114;
    border: 1px solid #1e1e26;
    border-radius: 14px;
    padding: 1.5rem;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00e5a040, transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.feature-card:hover {
    border-color: #00e5a025;
    background: #13131a;
    transform: translateY(-2px);
}
.feature-card:hover::before { opacity: 1; }
.card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e0e0e8;
    margin-bottom: 0.6rem;
    font-family: 'Inter', sans-serif;
}
.card-desc {
    font-size: 0.82rem;
    color: #555560;
    line-height: 1.7;
}

/* ── Footer ── */
.footer-line {
    margin-top: 3rem;
    padding: 1.5rem 1rem;
    border-top: 1px solid #00e5a030;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(90deg, #0d0d0f, #111114, #0d0d0f);
    color: #00e5a0;
    box-shadow: 0 -1px 10px #00e5a020, 0 0 20px #00e5a010 inset;
}
.footer-line span {
    color: #00e5a0;
    text-shadow: 0 0 5px #00e5a0, 0 0 10px #00e5a080, 0 0 20px #00e5a040;
}
.footer-line span:hover {
    color: #ffffff;
    text-shadow: 0 0 8px #00e5a0, 0 0 18px #00e5a0, 0 0 30px #00e5a0;
    transition: 0.3s;
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

    st.markdown("<hr style='border-color:#1a1a22; margin: 1.5rem 0'>", unsafe_allow_html=True)

    st.markdown("**SYSTEM**")

    import httpx
    def ping(url):
        try:
            httpx.get(url, timeout=2.0)
            return True
        except:
            return False

    api_ok = ping("http://localhost:8000/api/v1/health")
    api_status = "🟢 Online" if api_ok else "🔴 Offline"

    st.caption(f"FastAPI   {api_status}")
    st.caption("ChromaDB  🟢 Local")
    st.caption("Groq API  🟢 Connected")

    st.markdown("<hr style='border-color:#1a1a22; margin: 1.5rem 0'>", unsafe_allow_html=True)
    st.caption("v1.0 · Solo Developer Edition · 2026")


# ─── Main Dashboard ───────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-wrapper">
    <div class="hero-badge">◈ AUTOAGENT v1.0 · APRIL 2026</div>
    <div class="hero-title">Multi-Agent<br><span>AI System</span></div>
    <div class="hero-subtitle">
        Give a high-level goal — the system automatically breaks it into
        sub-tasks, assigns each to a specialized agent, searches the web,
        reads documents, writes reports, and stores everything in memory
        for future use.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="status-bar">
    <div class="status-pill"><div class="status-dot"></div> System Active</div>
    <div class="status-pill"><div class="status-dot"></div> ChromaDB Ready</div>
    <div class="status-pill"><div class="status-dot warning"></div> Groq API Connected</div>
</div>
""", unsafe_allow_html=True)

cards_html = (
    '<div class="cards-grid">'
    '<div class="feature-card">'
    '<div class="card-title">⚡ Task Runner</div>'
    '<div class="card-desc">Submit any goal in plain English. The Orchestrator agent '
    'decomposes it into sub-tasks and routes each one to the right '
    'specialist — Researcher, Writer, Critic, or Coder — then '
    'returns a final structured output.</div>'
    '</div>'
    '<div class="feature-card">'
    '<div class="card-title">📄 Document Manager</div>'
    '<div class="card-desc">Upload a PDF or TXT file. The RAG Agent splits it into chunks, '
    'embeds them into ChromaDB, and lets you ask questions directly '
    'against your document content using semantic similarity search.</div>'
    '</div>'
    '<div class="feature-card">'
    '<div class="card-title">🧠 Memory Explorer</div>'
    '<div class="card-desc">A direct window into ChromaDB. Search across all agent memory — '
    'past research results, task outputs, document chunks, and '
    'intermediate reasoning steps stored across sessions.</div>'
    '</div>'
    '<div class="feature-card">'
    '<div class="card-title">🕓 Session History</div>'
    '<div class="card-desc">Every task run is saved automatically. Browse past sessions, '
    'view the full agent execution trace, and reload any previous '
    'result without re-running the pipeline.</div>'
    '</div>'
    '</div>'
)
st.markdown(cards_html, unsafe_allow_html=True)

st.markdown("""
<div class="footer-line">
    <span>AUTOAGENT SYSTEM · DEVELOPER AHMAD</span>
    <span>100% FREE STACK · NO PAID API REQUIRED</span>
</div>
""", unsafe_allow_html=True)