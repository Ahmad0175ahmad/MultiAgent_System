import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers.base.model").setLevel(logging.WARNING)

from api.session_store import init_db
from api.routes import tasks, documents, memory

logger = logging.getLogger(__name__)

app = FastAPI(title="AutoAgent API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    logger.info("Initializing database...")
    init_db()


# Routers
app.include_router(tasks.router)
app.include_router(documents.router)
app.include_router(memory.router)


@app.get("/api/v1/health")
def health_check():
    return {"status": "ok"}
