#!/bin/bash
# AutoAgent — Project Structure Setup Script
# Run this in your terminal: bash setup.sh

echo "🚀 AutoAgent project structure ban raha hai..."

# Root folder
mkdir -p autoagent

cd autoagent

# ── agents/
mkdir -p agents
touch agents/__init__.py
touch agents/researcher.py
touch agents/writer.py
touch agents/critic.py
touch agents/rag_agent.py
touch agents/coder.py

# ── core/
mkdir -p core
touch core/__init__.py
touch core/orchestrator.py
touch core/state.py
touch core/llm_router.py
touch core/memory.py
touch core/tools.py

# ── api/
mkdir -p api/routes
touch api/__init__.py
touch api/main.py
touch api/models.py
touch api/session_store.py
touch api/routes/__init__.py
touch api/routes/tasks.py
touch api/routes/documents.py
touch api/routes/memory.py

# ── ui/
mkdir -p ui/pages
touch ui/__init__.py
touch ui/streamlit_app.py
touch ui/pages/__init__.py
touch ui/pages/1_task_runner.py
touch ui/pages/2_document_manager.py
touch ui/pages/3_memory_explorer.py
touch ui/pages/4_session_history.py

# ── utils/
mkdir -p utils
touch utils/__init__.py
touch utils/retry.py

# ── data/
mkdir -p data/chroma_db
mkdir -p data/uploads
touch data/.gitkeep

# ── Root files
touch config.py
touch requirements.txt
touch README.md

# .env.example
cat > .env.example << 'EOF'
# LLM Providers
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

# Search
TAVILY_API_KEY=your_tavily_key_here

# App Config
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile
CHROMADB_PATH=./data/chroma_db
UPLOADS_PATH=./data/uploads
SESSIONS_DB_PATH=./data/sessions.db

# API Config
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=True
EOF

# Copy .env.example to .env
cp .env.example .env

# .gitignore
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
*.pyo
data/chroma_db/
data/uploads/
data/sessions.db
.venv/
venv/
*.egg-info/
dist/
build/
.DS_Store
EOF

echo ""
echo "✅ Project structure tayyar ho gaya!"
echo ""
echo "📁 Folder: $(pwd)"
echo ""
echo "🔧 Ab yeh karo:"
echo "   1. cd autoagent"
echo "   2. python -m venv venv"
echo "   3. source venv/bin/activate   (Mac/Linux)"
echo "      venv\\Scripts\\activate     (Windows)"
echo "   4. pip install -r requirements.txt"
echo "   5. .env file mein apni API keys dalo"
echo ""
echo "🚀 VS Code mein kholne ke liye:"
echo "   code ."
