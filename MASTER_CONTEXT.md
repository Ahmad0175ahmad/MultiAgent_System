# AutoAgent — Multi-Agent AI System
## Master Context File (Har ChatGPT Chat Mein Attach Karo)

> **Stack:** LangGraph | Groq API | Gemini API | ChromaDB | Tavily | FastAPI | Streamlit  
> **Language:** Python 3.11+  
> **Developer:** Solo Developer  

---

## PROJECT STRUCTURE (Module 08)

```
autoagent/
├── agents/
│   ├── __init__.py
│   ├── researcher.py       ← Researcher Agent
│   ├── writer.py           ← Writer/Synthesizer Agent
│   ├── critic.py           ← QA/Critic Agent
│   ├── rag_agent.py        ← RAG Agent
│   └── coder.py            ← Coder Agent
│
├── core/
│   ├── orchestrator.py     ← LangGraph graph definition
│   ├── state.py            ← AgentState TypedDict
│   ├── llm_router.py       ← Groq/Gemini router
│   ├── memory.py           ← ChromaDB read/write helpers
│   └── tools.py            ← Tavily, DuckDuckGo tool wrappers
│
├── api/
│   ├── main.py             ← FastAPI app entry point
│   ├── models.py           ← Pydantic request/response models
│   ├── session_store.py    ← SQLite session management
│   └── routes/
│       ├── tasks.py        ← Task endpoints
│       ├── documents.py    ← Upload/RAG endpoints
│       └── memory.py       ← Memory search endpoints
│
├── ui/
│   ├── streamlit_app.py    ← Streamlit main app
│   └── pages/
│       ├── 1_task_runner.py
│       ├── 2_document_manager.py
│       ├── 3_memory_explorer.py
│       └── 4_session_history.py
│
├── data/
│   ├── chroma_db/          ← ChromaDB persisted storage
│   ├── uploads/            ← User uploaded documents
│   └── sessions.db         ← SQLite sessions
│
├── config.py               ← All settings (LLM choice, API keys)
├── requirements.txt
├── .env                    ← API keys (NEVER commit this)
└── README.md
```

---

## SYSTEM OVERVIEW

Yeh ek Multi-Agent AI System hai jahan user ek high-level goal deta hai aur system automatically:
1. Goal ko sub-tasks mein todta hai
2. Har sub-task sahi agent ko assign karta hai
3. Agents web search, document reading, writing, coding karte hain
4. Results ChromaDB mein store hote hain future use ke liye

---

## AGENTS OVERVIEW

| Agent | File | Kaam |
|-------|------|------|
| Researcher | agents/researcher.py | Tavily/DuckDuckGo se web search, facts extract karta hai |
| Writer | agents/writer.py | LLM se structured reports/summaries banata hai |
| Critic | agents/critic.py | Output review karta hai, score < 7 ho to revision bhejta hai |
| RAG | agents/rag_agent.py | Local documents se answer deta hai ChromaDB ke zariye |
| Coder | agents/coder.py | Python code generate/explain/review/debug karta hai |

---

## AGENTSTATE (Shared State)

```python
class AgentState(TypedDict):
    goal: str                        # Original user goal
    tasks: List[TaskItem]            # Decomposed sub-tasks
    current_task_id: str             # Currently running task
    results: Dict[str, Any]          # Outputs from each agent (keyed by task_id)
    memory_context: List[str]        # Past results from ChromaDB
    final_output: str                # Final synthesized answer
    error_log: List[str]             # Errors encountered
    session_id: str                  # Unique run ID
```

---

## LLM TIERS

| Tier | Provider | Model | Kab Use |
|------|----------|-------|---------|
| Default | Groq API | Llama 3.3 70B | Fast general tasks |
| Long Context | Gemini API | Gemini 1.5 Flash | Large prompts and summaries |

---

## CHROMADB COLLECTIONS

| Collection | Stores | Used By |
|-----------|--------|---------|
| research_memory | Web search results | Researcher Agent |
| document_store | PDF/text chunks | RAG Agent |
| task_outputs | Final session outputs | All agents |
| agent_scratchpad | Intermediate reasoning | Orchestrator |
| user_preferences | User feedback | Writer Agent |

---

## FASTAPI ENDPOINTS

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/task/create | New goal submit karo |
| GET | /api/v1/task/{id}/status | Task progress check karo |
| GET | /api/v1/task/{id}/result | Final output lo |
| POST | /api/v1/document/upload | PDF upload for RAG |
| GET | /api/v1/memory/search | ChromaDB search |
| GET | /api/v1/sessions | Past sessions list |
| GET | /api/v1/health | System health check |

---

## REQUIREMENTS.TXT

```
langchain>=0.2.0
langchain-community>=0.2.0
langgraph>=0.1.0
groq
google-genai
chromadb>=0.5.0
sentence-transformers>=2.7.0
tavily-python
duckduckgo-search
fastapi>=0.111.0
uvicorn[standard]
pydantic>=2.0
sqlmodel
python-multipart
streamlit>=1.35.0
pypdf2
python-docx
python-dotenv
httpx
```

---

## .ENV FILE

```
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile
CHROMADB_PATH=./data/chroma_db
UPLOADS_PATH=./data/uploads
SESSIONS_DB_PATH=./data/sessions.db
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
DEBUG=True
```

---

## IMPORTANT RULES (ChatGPT ke liye)

1. **Sirf woh file banao jo is chat mein request ki gayi hai**
2. **Dusri files mein import karo lekin unka code mat likho**
3. **Type hints aur docstrings zaroor add karo**
4. **Error handling aur logging har function mein**
5. **AgentState TypedDict ka structure change mat karo**
6. **Config values hamesha config.py / .env se lao, hardcode mat karo**
