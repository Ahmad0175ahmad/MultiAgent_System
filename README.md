# AutoAgent - Multi-Agent AI System

AutoAgent is a modular multi-agent workflow app that breaks a user goal into tasks and routes them through research and writing agents. It uses API-based LLM providers only, with Groq and Gemini handling generation while ChromaDB stores memory.

## Tech Stack

- Python 3.11+
- LangGraph
- Groq API
- Gemini API
- ChromaDB
- Tavily
- FastAPI
- Streamlit

## Setup

1. Clone the repository.
2. Change into the app folder with `cd autoagent`.
3. Create and activate a virtual environment. `uv init --python 3.11`
4. Install dependencies with `uv add -r requirements.txt`.
5. Copy `.env.example` to `.env`.
6. Add at least one LLM API key: `GROQ_API_KEY` or `GEMINI_API_KEY`.
7. Optionally set `TAVILY_API_KEY` for Tavily-backed web search.
8. Start the backend and Streamlit app.

## How To Run

Start FastAPI:

```bash
uvicorn api.main:app --reload --port 8000
```

Start Streamlit:

```bash
streamlit run ui/streamlit_app.py
```

The API will be available at `http://127.0.0.1:8000` and the Streamlit UI at `http://127.0.0.1:8501`.

## Environment

Use these keys in `.env`:

- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `DEFAULT_LLM_PROVIDER=groq` or `gemini`
- `TAVILY_API_KEY` for improved search results
- `CHROMADB_PATH`, `UPLOADS_PATH`, and `SESSIONS_DB_PATH` for local storage

## Project Structure

```text
autoagent/
|-- agents/
|-- api/
|-- core/
|-- data/
|-- ui/
|-- config.py
|-- requirements.txt
`-- README.md
```

## Example Usage

Open the Streamlit UI, enter a goal like `Research AI agents and generate a report`, choose `groq` or `gemini`, and run the task. The system decomposes the goal, executes agents, stores memory, and returns a final answer.
