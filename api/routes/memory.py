import logging
from fastapi import APIRouter, Query, HTTPException

from api.models import MemorySearchResponse, MemorySearchResult
from core.memory import MemoryManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])
memory_manager = MemoryManager()


@router.get("/search", response_model=MemorySearchResponse)
async def search(
    q: str = Query(...),
    collection: str = Query(default="research_memory"),  # ✅ collection parameter add kiya
    k: int = Query(default=5)
):
    try:
        results = memory_manager.retrieve(
            collection_name=collection,
            query=q,
            k=k,
            threshold=0.0  # ✅ threshold 0 — koi bhi result filter na ho
        )

        formatted = [
            MemorySearchResult(
                text=r["data"],
                score=r["score"],
                metadata=r.get("metadata", {})
            )
            for r in results
        ]

        return MemorySearchResponse(results=formatted)

    except Exception:
        logger.exception("Memory search failed")
        raise HTTPException(status_code=500, detail="Search failed")