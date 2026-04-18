import logging

import httpx


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

print("=" * 70)
print("AutoAgent System Diagnostics")
print("=" * 70)

# 1. FastAPI
print("\n[1/5] FastAPI (Backend Server)")
print("-" * 70)
try:
    response = httpx.get("http://localhost:8000/api/v1/health", timeout=5)
    print(f"OK FastAPI is running: {response.json()}")
except httpx.ConnectError:
    print("FAIL FastAPI is NOT running")
    print("    Fix: Run 'uvicorn api.main:app --reload --port 8000'")
except Exception as e:
    print(f"FAIL FastAPI check failed: {e}")

# 2. ChromaDB
print("\n[2/5] ChromaDB (Vector Database)")
print("-" * 70)
try:
    from config import settings
    import chromadb

    client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
    collections = client.list_collections()
    print("OK ChromaDB is working")
    print(f"    Path: {settings.CHROMADB_PATH}")
    print(f"    Collections: {len(collections)} found")
    for col in collections:
        print(f"      - {col.name}")
except Exception as e:
    print(f"FAIL ChromaDB error: {e}")

# 3. Streamlit
print("\n[3/5] Streamlit (Frontend UI)")
print("-" * 70)
try:
    httpx.get("http://localhost:8501", timeout=5)
    print("OK Streamlit is running")
    print("    URL: http://localhost:8501")
except httpx.ConnectError:
    print("FAIL Streamlit is NOT running")
    print("    Fix: Run 'streamlit run ui/streamlit_app.py'")
except Exception as e:
    print(f"WARN Streamlit check inconclusive: {e}")

# 4. Provider Keys
print("\n[4/5] Provider Keys")
print("-" * 70)
try:
    from config import settings

    print("OK Config loaded successfully")
    print(f"    Default Provider: {settings.DEFAULT_LLM_PROVIDER}")
    print(f"    Default Model: {settings.DEFAULT_LLM_MODEL}")
    print(
        f"    Groq API Key: {'OK Set' if settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your_groq_api_key_here' else 'FAIL Not set or placeholder'}"
    )
    print(
        f"    Gemini API Key: {'OK Set' if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != 'your_gemini_api_key_here' else 'FAIL Not set or placeholder'}"
    )
    print(
        f"    Tavily API Key: {'OK Set' if settings.TAVILY_API_KEY and settings.TAVILY_API_KEY != 'your_tavily_api_key_here' else 'FAIL Not set or placeholder'}"
    )
except Exception as e:
    print(f"FAIL Config error: {e}")

# 5. LLM Routing Readiness
print("\n[5/5] LLM Routing Readiness")
print("-" * 70)
try:
    from config import settings

    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
        print("OK Groq routing is ready")
    elif settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
        print("OK Gemini routing is ready")
    else:
        print("FAIL No LLM API key configured")
        print("    Fix: Set GROQ_API_KEY or GEMINI_API_KEY in autoagent/.env")
except Exception as e:
    print(f"FAIL LLM readiness check failed: {e}")

print("\n" + "=" * 70)
print("STARTUP SEQUENCE (Run in separate terminals):")
print("=" * 70)
print("Terminal 1: uvicorn api.main:app --reload --port 8000")
print("Terminal 2: streamlit run ui/streamlit_app.py")
print("\nThen access the UI at: http://localhost:8501")
print("=" * 70)
